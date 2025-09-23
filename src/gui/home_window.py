from PyQt6.QtWidgets import ( QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,QMessageBox, QTableWidget, QTableWidgetItem,)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication

class HomeWindow(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db = db_manager
        self.user = user_data 
        self.setWindowTitle(f"Home")
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f2e;
                color: #ffffff;
                font-family: 'Segoe UI';
            }
            QLabel#titleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #f5f5f5;
            }
            QLabel#subtitleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #f5f5f5;
            }
            QPushButton {
                border-radius: 12px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton#deleteBtn {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton#deleteBtn:hover {
                background-color: #c0392b;
            }
            QTableWidget {
                border-radius: 10px;
                background-color: #2c2c3e;
                color: #fff;
                gridline-color: #555;
            }
            QHeaderView::section {
                background-color: #3c3c52;
                font-weight: bold;
            }
        """)

        self.setWindowTitle(f"Home")
        self.setGeometry(150, 150, 800, 450)

        self.title_label = QLabel(f"Bem vindo, {self.user['name']}!")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle_label = QLabel(f"Nível de acesso: {self.user['access_level']}")
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(3)
        self.user_table.setHorizontalHeaderLabels(["ID", "Nome", "Nível de Acesso"])
        self.user_table.horizontalHeader().setStretchLastSection(True)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setSelectionBehavior(self.user_table.SelectionBehavior.SelectRows)
        self.user_table.setEditTriggers(self.user_table.EditTrigger.NoEditTriggers)
        self.user_table.setMinimumSize(200, 250)

        self.user_table.setColumnWidth(0, 50)
        self.user_table.setColumnWidth(1, 500)
        self.user_table.setColumnWidth(2, 120)

        self.delete_btn = QPushButton("Remover Usuário")
        self.delete_btn.setObjectName("deleteBtn")
        self.delete_btn.clicked.connect(self.delete_selected_user)
        self.delete_btn.setFixedWidth(180)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addWidget(self.user_table)  

        list_layout = QHBoxLayout()
        list_layout.addWidget(self.user_table)

        if self.user['access_level'] == 1:
            main_layout.addWidget(self.delete_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)
        self.populate_user_list()

    def center_window(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def populate_user_list(self):
        self.user_table.setRowCount(0)
        if self.user['access_level'] in [1, 2]:
            users = self.db.get_all_users_with_features()
            for row, u in enumerate(users):
                self.user_table.insertRow(row)

                id_item = QTableWidgetItem(str(u['id']))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.user_table.setItem(row, 0, id_item)
                
                name_item = QTableWidgetItem(u['name'])
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.user_table.setItem(row, 1, name_item)
                
                level_item = QTableWidgetItem(str(u['access_level']))
                level_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.user_table.setItem(row, 2, level_item)
        elif self.user['access_level'] == 3:
            u = self.user
            self.user_table.insertRow(0)
            
            id_item = QTableWidgetItem(str(u['id']))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.user_table.setItem(0, 0, id_item)
            
            name_item = QTableWidgetItem(u['name'])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.user_table.setItem(0, 1, name_item)
            
            level_item = QTableWidgetItem(str(u['access_level']))
            level_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.user_table.setItem(0, 2, level_item)

    def delete_selected_user(self):
        row = self.user_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário para remover.")
            return

        user_id = int(self.user_table.item(row, 0).text())
        if user_id == self.user['id']:
            QMessageBox.warning(self, "Aviso", "Você não pode remover a si mesmo.")
            return

        ok = self.db.delete_user(user_id)
        if ok:
            QMessageBox.information(self, "Sucesso", f"Usuário {user_id} removido.")
            self.populate_user_list()
        else:
            QMessageBox.warning(self, "Erro", "Falha ao remover usuário.")