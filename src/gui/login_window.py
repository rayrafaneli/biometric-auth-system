from PyQt6.QtWidgets import ( QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QListWidget, QFileDialog, QFrame, QWidget)
from PyQt6.QtGui import  QImage, QPixmap, QGuiApplication
from PyQt6.QtCore import QTimer, Qt

from src.gui.register_window import RegisterWindow
from src.gui.home_window import HomeWindow

from src.biometrics import matcher
from src.biometrics.feature_extractor import extract_feature_from_image

import os
import cv2

class LoginWindow(QMainWindow):
    def __init__(self, db_manager, matcher_obj):
        super().__init__()
        self.db = db_manager
        self.matcher = matcher_obj
        self.register_window = None
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.current_frame = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login Biométrico")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f2e;
                color: #ffffff;
                font-family: 'Segoe UI';
            }
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #f5f5f5;
            }
            QPushButton {
                border-radius: 12px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton#loginBtn {
                background-color: #4e9af1;
                color: white;
            }
            QPushButton#loginBtn:hover {
                background-color: #3a7bd5;
            }
            QPushButton#registerBtn {
                background-color: #38b764;
                color: white;
            }
            QPushButton#registerBtn:hover {
                background-color: #2e9955;
            }
            QListWidget {
                border-radius: 10px;
                padding: 8px;
                background-color: #2c2c3e;
                color: #fff;
            }
        """)

        self.title_label = QLabel("Login Biométrico")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.camera_label = QLabel("Preview da câmera")
        self.camera_label.setFixedSize(720, 540)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("""
            background-color: #2c2c3e;
            border-radius: 15px;
            border: 2px solid #444;
            color: #aaa;
        """)
        self.camera_label.setVisible(False)

        self.capture_btn = QPushButton("Capturar / Autenticar")
        self.capture_btn.setObjectName("loginBtn")
        self.capture_btn.setStyleSheet("text-align: center;")
        self.capture_btn.clicked.connect(self.start_camera_login)

        self.register_btn = QPushButton("Cadastrar novo usuário")
        self.register_btn.setObjectName("registerBtn")
        self.register_btn.setStyleSheet("text-align: center;")
        self.register_btn.clicked.connect(self.open_register_window)

        self.top_matches_label = QLabel("Top Matches:")
        self.top_matches_label.setVisible(False) 

        self.result_list = QListWidget()
        self.result_list.setVisible(False) 

        self.status_label = QLabel("Status: aguardando ação...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #ccc; font-style: italic;")
        self.status_label.setVisible(False)

        h_layout_top = QHBoxLayout()
        h_layout_top.addStretch() 
        h_layout_top.addWidget(self.capture_btn)
        h_layout_top.addSpacing(10)  
        h_layout_top.addWidget(self.register_btn)
        h_layout_top.addStretch() 

        self.card_frame = QFrame()  
        self.card_frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c3e;
                border-radius: 20px;
                padding: 15px;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.addWidget(self.camera_label)
        self.card_frame.setLayout(card_layout)
        self.card_frame.setVisible(False)  

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.title_label)
        v_layout.addSpacing(10)
        v_layout.addLayout(h_layout_top)
        v_layout.addSpacing(20)
        v_layout.addWidget(self.card_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        v_layout.addSpacing(15)
        v_layout.addWidget(self.top_matches_label, alignment=Qt.AlignmentFlag.AlignLeft)
        v_layout.addWidget(self.result_list)
        v_layout.addSpacing(10)
        v_layout.addWidget(self.status_label)

        central_widget = QWidget()
        central_widget.setLayout(v_layout)
        self.setCentralWidget(central_widget)

    def center_window(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def open_register_window(self):
        if self.register_window is None:
            self.register_window = RegisterWindow(self.db, self.matcher)
            self.register_window.closeEvent = self.on_register_close

        self.register_window.center_window()
        self.register_window.show()
        self.hide()

    def on_register_close(self, event):
        self.show()
        self.center_window()  

        if hasattr(self.register_window, "result_message") and self.register_window.result_message:
            self.status_label.setText(self.register_window.result_message)

        if "sucesso" in self.register_window.result_message.lower():
            self.status_label.setStyleSheet("color: #38b764; font-weight: bold;")
        else: 
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;") 
        event.accept()

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.camera_label.setPixmap(QPixmap.fromImage(qt_img).scaled(
                    self.camera_label.width(), self.camera_label.height(), Qt.AspectRatioMode.KeepAspectRatio
                ))

    def start_camera_login(self):
        self.camera_label.setVisible(True) 
        self.card_frame.setVisible(True)

        self.top_matches_label.setVisible(True)
        self.result_list.setVisible(True)
        self.status_label.setVisible(True)

        self.center_window()  

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # OU CAP_MSMF SE TIVER USANDO DROIDCAM
        if not self.cap.isOpened():
            self.status_label.setText("Não foi possível abrir a câmera.")
            return

        self.timer.start(30)

        self.status_label.setText("Inicializando câmera...")

        QTimer.singleShot(2000, self.start_authentication)
    
    def start_authentication(self):
        for _ in range(20):
            self.cap.read()

        self.status_label.setText("Autenticação iniciada...")
        self.auth_timer = QTimer()
        self.auth_timer.timeout.connect(lambda: self.capture_and_authenticate(extract_feature_from_image))
        self.auth_timer.start(1000)

    def capture_and_authenticate(self, extract_func):
        if self.current_frame is None:
            self.status_label.setText("Falha: nenhum frame disponível.")
            return

        tmp_path = os.path.join('data', 'images_to_authenticate', 'tmp_capture.jpg')
        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
        cv2.imwrite(tmp_path, self.current_frame)

        self.status_label.setText("Processando reconhecimento...")
        query_feat = extract_func(tmp_path)
        if not query_feat:
            self.status_label.setText("Falha ao extrair features.")
            return

        self.process_matching(query_feat)

    def process_matching(self, query_feat):
        users = self.db.get_all_users_with_features()
        if not users:
            self.status_label.setText("Nenhum usuário cadastrado.")
            return

        scored = matcher.score_users(query_feat, users)
        self.result_list.clear()
        for i, (u, best_s, mean_k) in enumerate(scored[:3]):
            self.result_list.addItem(f"{i+1}. {u['name']} (ID {u['id']}): best={best_s:.4f} mean_top={mean_k:.4f}")

        granted, best_user, *_ = matcher.decide_match(query_feat, users)

        if granted:
            self.status_label.setText(f"Acesso concedido: {best_user['name']} (ID {best_user['id']})")
            self.stop_camera()
            self.hide()

            self.home_window = HomeWindow(self.db, best_user)
            self.home_window.center_window()  
            self.home_window.show()
        else:
            self.status_label.setText("Aguardando reconhecimento...")

    def stop_camera(self):
        self.timer.stop()
        if hasattr(self, 'auth_timer'):
            self.auth_timer.stop()
        if self.cap:
            self.cap.release()