import cv2
import os
from src.biometrics.image_quality import is_image_quality_sufficient
 # from src.biometrics.liveness_detection import detect_liveness_blink_haar, analyze_texture_lbp
import os
import time
from datetime import datetime
from typing import Optional

class CaptureSession:
    def __init__(self, config, display_callback=None):
        """
        Gerencia sessões de captura facial automática com interface fluida.
        Controla todo o processo de captura de imagens faciais, incluindo inicialização
        da câmera, captura por variações, feedback visual em tempo real e salvamento
        automático das imagens organizadas por usuário e variação.
        """
        self.config = config
        self.cap: Optional[cv2.VideoCapture] = None
        self.current_variation_index: int = 0
        self.current_image_count: int = 0
        self.is_capturing: bool = False
        self.ultimo_tempo_captura: float = 0
        self.display_callback = display_callback
        
        # Carrega o classificador Haar Cascade para detecção facial
        face_cascade_path = os.path.join(os.path.dirname(__file__), 'cascades', 'haarcascade_frontalface_default.xml')
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        if self.face_cascade.empty():
            raise FileNotFoundError(f"Cascade não encontrado: {face_cascade_path}. Certifique-se de que o arquivo existe.")
    
    def enviar_status(self, mensagem: str):
        if self.status_callback:
            self.status_callback(mensagem)

    #Inicializa e configura a câmera com verificação de permissões.
    def inicializar_camera(self, camera_index: int = 0) -> bool:
        try:
            # Fechar câmera anterior se existir
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()
            
            # Inicializar com backend DSHOW (Windows)
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW) # OU CAP_MSMF SE TIVER USANDO DROIDCAM
            
            if not self.cap.isOpened():
                print("❌ Câmera não acessível. Verifique as permissões.")
                return False
            
            # Configurações otimizadas
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Testar com múltiplas tentativas
            for tentativa in range(8):
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    print(f"✅ Câmera {camera_index} inicializada - {frame.shape[1]}x{frame.shape[0]}")
                    return True
            
            print("❌ Câmera não retorna imagens válidas")
            return False
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    #Processamento de frame com feedback visual fluido e profissional.
    def _processar_frame_fluido(self, frame, variacao_nome: str, tempo_restante: float = None):
        frame_display = frame.copy()
        altura, largura = frame.shape[:2]
        
        # Overlay semi-transparente para informações
        overlay = frame_display.copy()
        cv2.rectangle(overlay, (0, 0), (500, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.75, frame_display, 0.25, 0, frame_display)
        
        # Informações principais
        textos = [
            "🎥 CAPTURA AUTOMÁTICA",
            f"👤: {self.config.user_id}",
            f"🎭: {variacao_nome.upper()}",
            f"📸: {self.current_image_count}/{self.config.images_per_variation}",
            f"⏱️: {self.config.capture_interval}s intervalo"
        ]
        
        # Adicionar textos com sombra para melhor legibilidade
        for i, texto in enumerate(textos):
            # Sombra
            cv2.putText(frame_display, texto, (17, 37 + i*30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
            # Texto principal
            cv2.putText(frame_display, texto, (15, 35 + i*30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Contagem regressiva visual
        if tempo_restante is not None and tempo_restante > 0:
            texto_contagem = f"⏳ Próxima: {tempo_restante:.1f}s"
            cv2.putText(frame_display, texto_contagem, (15, 185), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
        
        self.rosto_detectado = False

        # Detecção facial sutil
        if self.config.require_face_detection:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
                
                if len(faces) > 0:
                    self.rosto_detectado = True
                    for (x, y, w, h) in faces:
                        # Retângulo verde suave
                        cv2.rectangle(frame_display, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    status_text = "✅ ROSTO DETECTADO"
                    cv2.putText(frame_display, status_text, (largura - 280, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    status_text = "👤 POSICIONE-SE"
                    cv2.putText(frame_display, status_text, (largura - 250, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
            except:
                pass
        
        # Timestamp discreto
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame_display, f"🕒 {timestamp}", (largura - 120, altura - 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame_display
    
    #Captura automática com fluidez e timing preciso.
    def _capturar_variacao_fluida(self, variacao_nome: str) -> bool:
        self.current_image_count = 0
        self.ultimo_tempo_captura = time.time()
        
        print(f"   📸 Iniciando captura: {variacao_nome}")
        print(f"   ⏰ Intervalo: {self.config.capture_interval}s entre imagens")
        
        while (self.current_image_count < self.config.images_per_variation and 
               self.is_capturing):
            
            # Capturar frame
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Calcular tempo para próxima captura
            tempo_atual = time.time()
            tempo_decorrido = tempo_atual - self.ultimo_tempo_captura
            tempo_restante = max(0, self.config.capture_interval - tempo_decorrido)
            
            # Processar frame com informações
            frame_processado = self._processar_frame_fluido(frame, variacao_nome, tempo_restante)
            
            # Mostrar frame processado
            
            if self.display_callback:
                self.display_callback(frame_processado)
            
            # cv2.imshow('Captura Facial Automática - ESC para cancelar', frame_processado)

            # Verificar cancelamento

            '''
            if cv2.waitKey(1) & 0xFF == 27:
                self.is_capturing = False
                return False
            '''
            
            # Verificar se é hora de capturar
            if (tempo_decorrido >= self.config.capture_interval or self.current_image_count == 0):
                if self.rosto_detectado:
                    # Verificar qualidade da imagem antes de salvar
                    quality_ok, quality_message = is_image_quality_sufficient(frame)
                    if quality_ok:
                        if self._salvar_imagem(frame, variacao_nome):
                            self.current_image_count += 1
                            self.ultimo_tempo_captura = time.time()
                            self.enviar_status(f"   ✅ [{self.current_image_count}/{self.config.images_per_variation}] Imagem salva")
                        else:
                            self.enviar_status("❌ Erro ao salvar imagem.")
                    else:
                        self.enviar_status(f"⚠️ Qualidade da imagem insuficiente: {quality_message}")
                else:
                    self.enviar_status("⛔ Rosto não detectado — aguardando posicionamento...")
        print(f"   ✅ {variacao_nome} concluída - {self.current_image_count} imagens")
        return True
    
    #Transição suave entre variações com animação.
    def _transicao_entre_variações(self, variacao_anterior: str, proxima_variacao: str):
        
        print(f"   🔄 Transição: {variacao_anterior} → {proxima_variacao}")
        print(f"   ⏱️  Prepare-se para a próxima variação...")
        
        tempo_transicao = 3.0  # 3 segundos de transição
        inicio_transicao = time.time()
        
        while time.time() - inicio_transicao < tempo_transicao and self.is_capturing:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            tempo_restante = tempo_transicao - (time.time() - inicio_transicao)
            frame_display = frame.copy()
            
            # Overlay de transição
            overlay = frame_display.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
            alpha = 0.7 - (time.time() - inicio_transicao) / tempo_transicao * 0.4
            cv2.addWeighted(overlay, alpha, frame_display, 1 - alpha, 0, frame_display)
            
            # Texto de transição
            cv2.putText(frame_display, "🔄", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)
            cv2.putText(frame_display, f"PRÓXIMA: {proxima_variacao.upper()}", (50, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            cv2.putText(frame_display, f"{int(tempo_restante) + 1}...", (50, 220), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
            

            if self.display_callback:
                self.display_callback(frame_display)
            
            # cv2.imshow('Captura Facial Automática - ESC para cancelar', frame_display)

            '''
            if cv2.waitKey(30) & 0xFF == 27:
                self.is_capturing = False
                return False
            '''
        
        # Frame final de transição
        ret, frame = self.cap.read()
        if ret:
            cv2.putText(frame, f"🎬 {proxima_variacao.upper()}!", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            if self.display_callback:
                self.display_callback(frame)

            # cv2.imshow('Captura Facial Automática - ESC para cancelar', frame)
            # cv2.waitKey(300)  # Breve pausa
        
        return True
    
    #Mostra barra de progresso global da captura.
    def _mostrar_progresso_global(self):
        total_variações = len(self.config.variations)
        total_imagens = total_variações * self.config.images_per_variation
        imagens_capturadas = (self.current_variation_index * self.config.images_per_variation + 
                             self.current_image_count)
        
        if total_imagens > 0:
            progresso = imagens_capturadas / total_imagens
            barra_width = 40
            filled = int(barra_width * progresso)
            
            print(f"\n📊 PROGRESSO GLOBAL: {imagens_capturadas}/{total_imagens} imagens")
            print(f"   [{'█' * filled}{'░' * (barra_width - filled)}] {progresso*100:.1f}%")
    
    #Salva imagem com timestamp único e organização automática.
    def _salvar_imagem(self, frame, variacao_nome: str) -> bool:
        try:
            # Gerar nome único do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            nome_arquivo = f"{self.config.user_id}_{variacao_nome}_{timestamp}.jpg"
            
            # Criar estrutura de diretórios
            dir_path = os.path.join(self.config.base_directory, self.config.user_id, variacao_nome)
            os.makedirs(dir_path, exist_ok=True)
            
            # Caminho completo
            caminho_completo = os.path.join(dir_path, nome_arquivo)
            
            # Salvar imagem
            success = cv2.imwrite(caminho_completo, frame)
            
            return success
            
        except Exception as e:
            print(f"   ❌ Erro ao salvar imagem: {e}")
            return False
    
    #Inicia captura automática com máxima fluidez e experiência profissional.
    def iniciar_captura_fluida(self) -> bool:
        if self.cap is None or not self.cap.isOpened():
            print("❌ Câmera não inicializada")
            return False

        print("\n" + "="*60)
        print("INICIANDO CAPTURA FLUIDA")
        print("="*60)
        print(f"Usuário: {self.config.user_id}")
        print(f"Total de imagens: {len(self.config.variations) * self.config.images_per_variation}")
        print(f"Intervalo: {self.config.capture_interval}s entre capturas")
        print("="*60)
        
        self.is_capturing = True
        self.current_variation_index = 0

        try:
            for i, variacao in enumerate(self.config.variations):
                if not self.is_capturing:
                    break
                
                # Transição entre variações (exceto primeira)
                if i > 0:
                    if not self._transicao_entre_variações(self.config.variations[i-1], variacao):
                        break
                
                # Mostrar progresso global
                self._mostrar_progresso_global()
                
                # Capturar variação atual
                if not self._capturar_variacao_fluida(variacao):
                    break
                
                self.current_variation_index += 1
                self.current_image_count = 0

            if self.is_capturing:
                self.enviar_status("\n🎉 CAPTURA CONCLUÍDA COM SUCESSO!")
                print("\n🎉 CAPTURA CONCLUÍDA COM SUCESSO!")
                return True
            else:
                self.enviar_status("\n⏹️ CAPTURA INTERROMPIDA")
                print("\n⏹️ CAPTURA INTERROMPIDA")
                return False

        except Exception as e:
            print(f"❌ Erro durante captura: {e}")
            return False
        finally:
            self.liberar_recursos()
    
    #Libera recursos da câmera e fecha janelas.
    def liberar_recursos(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.is_capturing = False
        print("🧹 Recursos liberados")