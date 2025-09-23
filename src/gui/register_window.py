from PyQt6.QtWidgets import ( QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QComboBox, QFileDialog, QFrame )
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QGuiApplication

import os
import cv2

class RegisterWindow(QWidget):
    def __init__(self, db, matcher):
        super().__init__()
        self.db = db
        self.matcher = matcher
        self.session = None
        self.init_ui()
        self.result_message = ""

    def init_ui(self):
        self.setWindowTitle("Cadastro Biométrico")
        self.setGeometry(100, 100, 450, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f2e;
                color: #fff;
                font-family: 'Segoe UI';
            }
            QLabel#titleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #f5f5f5;
            }
            QPushButton {
                border-radius: 12px;
                padding: 10px 50px 10px 50px;
                font-weight: bold;
                background-color: #38b764;
            }
            QPushButton:hover {
                background-color: #2e9955;
            }
        """)

        self.title_label = QLabel("Cadastro Biométrico")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Digite o nome do usuário")

        self.access_input = QComboBox()
        self.access_input.addItems(['1', '2', '3'])

        form_layout = QVBoxLayout()
        for label_text, widget in [
            ("Nome", self.name_input),
            ("Nível de acesso", self.access_input),
        ]:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #ddd;")
            field_layout = QVBoxLayout()
            field_layout.addWidget(lbl)
            field_layout.addWidget(widget)
            form_layout.addLayout(field_layout)

        self.register_btn = QPushButton("Capturar Rosto")
        self.register_btn.clicked.connect(self.start_register)

        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c3e;
            }
            QLineEdit, QComboBox {
                border: 1px solid #fff;
                padding: 8px;
                background-color: #1f1f2e;
                color: #fff;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(20)
        card_layout.addLayout(form_layout)
        card_layout.addWidget(self.register_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        card_frame.setLayout(card_layout)

        self.status_label = QLabel("Status: aguardando...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-style: italic; color: #ccc;")

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addSpacing(15)
        layout.addWidget(card_frame)
        layout.addSpacing(10)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def center_window(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def limpar_campos(self):
        self.name_input.clear()
        self.access_input.setCurrentIndex(0)
        self.status_label.setText("Status: aguardando...")
        self.result_message = ""

    def showEvent(self, event):
        super().showEvent(event)
        self.limpar_campos()

    def start_register(self):
        from src.biometrics.ConfigCaptura import CaptureConfig
        from src.biometrics.SessaoCaptura import CaptureSession

        name = self.name_input.text().strip()
        if not name:
            self.status_label.setText("Nome não pode ser vazio.")
            return

        access_level = int(self.access_input.currentText())
        features = []

        base_dir = os.path.join("data", "images_to_register")
        user_dir = os.path.join(base_dir, name.replace(" ", "_"))
        os.makedirs(user_dir, exist_ok=True)

        config = CaptureConfig(user_id=name.replace(" ", "_"))
        self.session = CaptureSession(config)
        if not self.session.inicializar_camera(0):
            self.status_label.setText("Não foi possível abrir a câmera. Cadastro sem imagens.")
            self.finish_registration(name, access_level, features)
            return

        self.cam_window = CameraCaptureWindow(self.session, user_dir)
        self.cam_window.capture_finished.connect(self.on_capture_finished)
        
        self.cam_window.center_window() 
        self.cam_window.show()
        self.status_label.setText("Abra a câmera e clique em Capturar...")
            
    def process_features(self, folder):
        from src.biometrics.feature_extractor import extract_features_from_folder
        features = extract_features_from_folder(folder)
        name = self.name_input.text().strip()
        access_level = int(self.access_input.currentText())
        self.finish_registration(name, access_level, features)

    def on_capture_finished(self, folder):
        from src.biometrics.feature_extractor import extract_features_from_folder
        features = extract_features_from_folder(folder)
        name = self.name_input.text().strip()
        access_level = int(self.access_input.currentText())
        self.finish_registration(name, access_level, features)

    def finish_registration(self, name, access_level, features):
        user_id = self.db.register_user(name, access_level, features)
        if user_id:
            self.result_message = f"Usuário cadastrado com sucesso! ID={user_id}"
            if hasattr(self, 'cam_window') and self.cam_window:
                self.cam_window.close()
            self.close()
        else:
            self.result_message = "Falha ao cadastrar usuário."

class CameraCaptureWindow(QWidget):
    capture_finished = pyqtSignal(str)

    def __init__(self, session, user_dir):
        super().__init__()
        self.session = session
        self.user_dir = user_dir
        self.session.display_callback = self.show_frame
        self.session.status_callback = self.atualizar_status
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Captura da Câmera")
        self.setGeometry(200, 200, 700, 600)
        self.setStyleSheet("""
            QWidget { background-color: #1f1f2e; color: #fff; font-family: 'Segoe UI'; }
            QPushButton { background-color: #4e9af1; border-radius: 12px; padding: 10px 20px; font-weight: bold; }
            QPushButton:hover { background-color: #3a7bd5; }
            QLabel { font-size: 14px; }
        """)

        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("background-color: black; border: 2px solid #555;")

        self.status_label = QLabel("🟢 Câmera pronta")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.substatus_label = QLabel("")
        self.substatus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.substatus_label.setStyleSheet("font-size: 12px; color: #aaa; font-style: italic;")

        self.capture_btn = QPushButton("Iniciar captura")
        self.capture_btn.clicked.connect(self.start_capture)

        card_layout = QVBoxLayout()
        card_layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status_label)
        card_layout.addWidget(self.substatus_label)
        card_layout.addWidget(self.capture_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(card_layout)

    def center_window(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showEvent(self, event):
        super().showEvent(event)
        self.iniciar_video()

    def iniciar_video(self):
        from threading import Thread

        def loop_video():
            while self.session.cap and self.session.cap.isOpened():
                ret, frame = self.session.cap.read()
                if ret:
                    self.show_frame(frame)
                cv2.waitKey(30)

        Thread(target=loop_video, daemon=True).start()

    def start_capture(self):
        from threading import Thread

        if not self.session.cap or not self.session.cap.isOpened():
            self.status_label.setText("❌ Não foi possível abrir a câmera.")
            return
        
        self.capture_btn.hide()
        self.status_label.setText("🎯 Captura automática iniciada...")
        self.substatus_label.setText("Esta janela será fechada automaticamente ao final da captura.")

        def run_capture():
            self.session.iniciar_captura_fluida()
            self.capture_finished.emit(self.user_dir)

        Thread(target=run_capture, daemon=True).start()

    def show_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def atualizar_status(self, mensagem: str):
        self.status_label.setText(mensagem)