from ConfigCaptura import CaptureConfig
from SessaoCaptura import CaptureSession
from testes import Testes
import time

configuracao = CaptureConfig("facial_dataset", "unknown_user", None, 5, 1, (640, 480), (100, 100), True)
sessao = CaptureSession(configuracao)
sessao.inicializar_camera()

if sessao.inicializar_camera():
    print("✅ Câmera pronta! Iniciando captura fluida...")
    time.sleep(1)
    
    if sessao.iniciar_captura_fluida():
        print("🎉 Experiência de captura concluída com sucesso!")
    else:
        print("❌ Captura interrompida")
else:
    print("❌ Falha na câmera")
