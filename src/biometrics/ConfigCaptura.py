import json
import os
from pathlib import Path

class CaptureConfig:
    """
    Gerencia as configurações para captura de dataset facial.
    Armazena e valida todos os parâmetros necessários para sessões de captura,
    incluindo diretórios, usuário, variações, resolução e critérios de qualidade.
    """
    def __init__(self,
                 user_id,
                 base_directory='data/images_to_register',
                 variations=None,
                 images_per_variation=5,
                 capture_interval=1.0,
                 resolution=(640, 480),
                 min_face_size=(100, 100),
                 require_face_detection=True):

        # Permite criar uma configuração com valores razoáveis por padrão.
        # O único parâmetro obrigatório é user_id (identificador do usuário).

        # Conversão de listas para tuplas
        if isinstance(resolution, list):
            resolution = tuple(resolution)
        if isinstance(min_face_size, list):
            min_face_size = tuple(min_face_size)

        # Diretório base onde todo o dataset será armazenado
        self.base_directory = base_directory

        # Identificador único do usuário/participante
        self.user_id = user_id

        # Lista de variações; default simples para integração leve
        self.variations = variations if variations else ['default']

        # Quantidade de imagens por variação (valor padrão pequeno e rápido)
        self.images_per_variation = images_per_variation

        # Intervalo entre capturas em segundos
        self.capture_interval = capture_interval

        # Resolução padrão (w,h)
        self.resolution = resolution

        # Tamanho mínimo de face (h,w)
        self.min_face_size = min_face_size

        # Salvar apenas se rosto detectado?
        self.require_face_detection = require_face_detection

    #validando os paâmetros    
    def validate(self):
        # Validar user_id
        if not self.user_id:
            raise ValueError("user_id deve conter apenas caracteres alfanuméricos")
        
        # Validar images_per_variation
        if not isinstance(self.images_per_variation, int) or self.images_per_variation <= 0:
            raise ValueError("images_per_variation deve ser um inteiro positivo")
        
        # Validar resolution
        if (not isinstance(self.resolution, tuple) or 
            len(self.resolution) != 2 or 
            not all(isinstance(dim, int) and dim > 0 for dim in self.resolution)):
            raise ValueError("resolution deve ser uma tuple com dois inteiros positivos")
        
        # Validar min_face_size
        if (not isinstance(self.min_face_size, tuple) or 
            len(self.resolution) != 2 or 
            not all(isinstance(dim, int) and dim > 0 for dim in self.resolution)):
            raise ValueError("resolution deve ser uma tuple com dois inteiros positivos")
             
        # Validar min_face_size
        if not self.require_face_detection == True:
            raise ValueError("só deve ser salvo se rosto for detectado")

    # transformando as config em dicionario python:
    def to_dict(self):    
        return {
            'base_directory': self.base_directory,
            'user_id': self.user_id,
            'variations': self.variations,
            'images_per_variation': self.images_per_variation,
            'capture_interval': self.capture_interval,
            'resolution': self.resolution,
            'min_face_size': self.min_face_size,
            'require_face_detection': self.require_face_detection
        }

    #salvando configurações em arquivo Json
    def save_to_json(self, file_path: str) -> None:
        """
        Salva as configurações atuais em um arquivo JSON de forma serializada.
        
        Esta função é útil para:
        - Persistir configurações entre sessões
        - Documentar os parâmetros usados em cada captura
        - Compartilhar configurações com outros pesquisadores
        - Reprodutibilidade de experimentos
        
        Args:
            file_path (str): Caminho completo do arquivo JSON a ser criado.
                            Exemplo: "configuracoes/usuario_01.json"
        """
        try:
            # Converte as configurações para dicionário
            config_data = self.to_dict()
            
            # Garante que o diretório pai existe
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Serializa e salva com formatação legível
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(config_data, json_file, indent=4, ensure_ascii=False)
            
            print(f"Configurações salvas com sucesso em: {file_path}")
            
        except PermissionError:
            raise PermissionError(f"Permissão negada para criar arquivo em: {file_path}")
        except TypeError as e:
            raise TypeError(f"Objeto não serializável nas configurações: {e}")
        except Exception as e:
            raise IOError(f"Erro inesperado ao salvar JSON: {e}")

    #carregando configurações em arquivo Jason
    @classmethod
    def load_from_json(cls, file_path: str):
        """
        Carrega configurações de um arquivo JSON e cria uma nova instância.
        
        Esta função permite recriar exatamente a mesma configuração usada
        anteriormente, garantindo consistência entre sessões de captura.
        
        Args:
            file_path (str): Caminho completo do arquivo JSON a ser carregado.
                            Exemplo: "configuracoes/usuario_01.json"
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as json_file:
                config_data = json.load(json_file)
            
            # Converter listas para tuplas nos campos específicos
            if 'resolution' in config_data and isinstance(config_data['resolution'], list):
                config_data['resolution'] = tuple(config_data['resolution'])
            
            if 'min_face_size' in config_data and isinstance(config_data['min_face_size'], list):
                config_data['min_face_size'] = tuple(config_data['min_face_size'])
            
            instance = cls(**config_data)
            print(f"Configurações carregadas com sucesso de: {file_path}")
            return instance
            
        except Exception as e:
            raise IOError(f"Erro ao carregar JSON: {e}")
        
        except Exception as e:
            raise IOError(f"Erro ao carregar JSON: {e}")
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Erro de decodificação JSON no arquivo {file_path}: {e.msg}", e.doc, e.pos)
        except TypeError as e:
            raise TypeError(f"Erro ao instanciar classe com parâmetros do JSON: {e}")
        except Exception as e:
            raise IOError(f"Erro inesperado ao carregar JSON: {e}")
        
        
