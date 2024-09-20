import folium
import pandas as pd
import numpy as np
import tkinter as tk
import math
import webbrowser
import random
import sys
import string
import os
import random
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans
from PyQt5.QtCore import QUrl,QEventLoop, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QComboBox, QListWidget, QPushButton, QLineEdit, QSizePolicy, QDialog, QDialogButtonBox, QMessageBox, QDesktopWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtGui import QPixmap
# 验证码生成
def read_start_locations(self):
    # 从 start_loc.csv 读取起始点位置
    start_loc_data = pd.read_csv('../data/start_loc.csv', encoding="utf-8")
    start_locations = list(start_loc_data['location'])
    # 使用 self.tr 对每个位置进行翻译
    return [self.tr(location) for location in start_locations]

def read_end_locations(self):
    # 从 end_loc.csv 读取终点位置
    end_loc_data = pd.read_csv('../data/end_loc.csv', encoding="utf-8")
    end_locations = list(end_loc_data['location'])
    # 使用 self.tr 对每个位置进行翻译
    return [self.tr(location) for location in end_locations]

def generate_verification_code_image():
    code = ''.join(random.choices(string.digits, k=4))
    image = Image.new('RGB', (100, 40), color = (255, 255, 255))
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
    # 为每个数字设置随机颜色并绘制
    for i, digit in enumerate(code):
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.text((10 + i * 25, 20), digit, font=font, fill=color)  
    image.save("../picture/verifivation_code/verification_code.png")
    return code
def generate_random_guest_name():
    return "游客" + ''.join(random.choices(string.ascii_letters + string.digits, k=10))

class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("欢迎界面"))
        self.setGeometry(200, 200, 600, 600)  # 放大窗口
        
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        
        # 欢迎语和程序介绍
        welcome_label = QLabel(self.tr("欢迎来到燕园个性化导游系统！"))
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        introduction_label = QLabel(self.tr("在这里，您可以根据您的需求规划北大校园的个性化游玩路线。\n请注册或登录开始使用，或者以游客模式浏览。"))
        
        # 添加图片
        pixmap = QPixmap("../picture/welcome_image1.jpg")  # 确保文件路径正确
        image_label = QLabel(self)
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)
        image_label.setFixedHeight(400)  # 控制图片高度

        # 创建三个按钮：注册、登录、游客模式
        self.register_button = QPushButton(self.tr("注册"), self)
        self.register_button.clicked.connect(self.show_register_window)
        
        self.login_button = QPushButton(self.tr("登录"), self)
        self.login_button.clicked.connect(self.show_login_window)
        
        self.guest_button = QPushButton(self.tr("游客模式"), self)
        self.guest_button.clicked.connect(self.enter_guest_mode)
        
        layout.addWidget(welcome_label)
        layout.addWidget(introduction_label)
        layout.addWidget(image_label)
        layout.addWidget(self.register_button)
        layout.addWidget(self.login_button)
        layout.addWidget(self.guest_button)
        
        self.setCentralWidget(central_widget)
    
    def show_register_window(self):
        self.register_window = RegisterWindow(self)  # 传递欢迎界面的引用
        self.register_window.show()
        self.close()

    def show_login_window(self):
        self.login_window = LoginWindow(self)  # 传递欢迎界面的引用
        self.login_window.show()
        self.close()

    def enter_guest_mode(self):
        guest_name = generate_random_guest_name()
        QMessageBox.information(self, self.tr("游客模式"), f"{self.tr("欢迎进入游客模式！您的用户名是：")}{guest_name}")
        self.open_main_window(guest_name)  # 直接进入主窗口

    def open_main_window(self,username):
        self.main_window = MainWindow(username)  # 打开主窗口
        self.main_window.show()
        self.close()
        
class RegisterWindow(QMainWindow):
    def __init__(self, welcome_window):
        super().__init__()
        self.setWindowTitle("用户注册")
        self.setGeometry(300, 300, 400, 300)
        self.welcome_window = welcome_window  # 保存欢迎界面的引用
        
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        
        self.username_label = QLabel(self.tr("用户名:"))
        self.username_input = QLineEdit(self)
        
        self.password_label = QLabel(self.tr("密码:"))
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.confirm_password_label = QLabel(self.tr("再次输入密码:"))
        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.register_button = QPushButton(self.tr("注册"), self)
        self.register_button.clicked.connect(self.register_user)

        self.back_button = QPushButton(self.tr("返回"), self)  # 返回按钮
        self.back_button.clicked.connect(self.back_to_welcome)
        
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_label)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)
        
        self.setCentralWidget(central_widget)
    
    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if password != confirm_password:
            QMessageBox.warning(self, self.tr("注册失败"), self.tr("两次密码输入不一致！"))
            return

        try:
            users_data = pd.read_csv('../data/users.csv')
        except FileNotFoundError:
            users_data = pd.DataFrame(columns=['username', 'password'])

        if username in users_data['username'].values:
            QMessageBox.warning(self, self.tr("注册失败"), self.tr("用户名已存在！"))
        else:
            new_user = pd.DataFrame({'username': [username], 'password': [password]})
            users_data = pd.concat([users_data, new_user], ignore_index=True)
            users_data.to_csv('../data/users.csv', index=False)
            QMessageBox.information(self, self.tr("注册成功"), self.tr("用户注册成功！"))
            self.back_to_welcome()

    def back_to_welcome(self):
        self.welcome_window.show()
        self.close()

class LoginWindow(QMainWindow):
    def __init__(self, welcome_window):
        super().__init__()
        self.setWindowTitle(self.tr("用户登录"))
        self.setGeometry(300, 300, 400, 300)
        self.welcome_window = welcome_window  # 保存欢迎界面的引用

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.username_label = QLabel(self.tr("用户名:"))
        self.username_input = QLineEdit(self)

        self.password_label = QLabel(self.tr("密码:"))
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.verification_label = QLabel(self.tr("验证码:"))
        self.verification_code = generate_verification_code_image()
        verification_pixmap = QPixmap("../picture/verifivation_code/verification_code.png")
        self.verification_display = QLabel(self)
        self.verification_display.setPixmap(verification_pixmap)
        self.verification_display.setScaledContents(True)
        self.verification_display.setFixedHeight(70)
        self.verification_input = QLineEdit(self)

        self.login_button = QPushButton(self.tr("登录"), self)
        self.login_button.clicked.connect(self.login_user)

        self.back_button = QPushButton(self.tr("返回"), self)  # 返回按钮
        self.back_button.clicked.connect(self.back_to_welcome)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.verification_label)
        layout.addWidget(self.verification_display)
        layout.addWidget(self.verification_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.back_button)

        self.setCentralWidget(central_widget)

    def login_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        entered_code = self.verification_input.text()

        try:
            users_data = pd.read_csv('../data/users.csv')
        except FileNotFoundError:
            QMessageBox.warning(self, self.tr("登录失败"), self.tr("用户数据库不存在！"))
            return

        if username not in users_data['username'].values:
            QMessageBox.warning(self, self.tr("登录失败"),self.tr("用户名不存在！"))
        elif not str(users_data[users_data['username'] == username]['password'].values[0]) == str(password):
            QMessageBox.warning(self, self.tr("登录失败"),self.tr("密码错误！"))
        elif str(entered_code) != str(self.verification_code):
            QMessageBox.warning(self, self.tr("登录失败"), self.tr("验证码错误！"))
        else:
            QMessageBox.information(self, self.tr("登录成功"), f"{username}, {self.tr("欢迎回来！")}")
            self.open_main_window(username)

    def back_to_welcome(self):
        self.welcome_window.show()
        self.close()

    def open_main_window(self, username):
        self.main_window = MainWindow(username)  # 打开主窗口
        self.main_window.show()
        self.close()
        
from PyQt5.QtCore import QTranslator, QCoreApplication

app = QApplication(sys.argv)

translator = QTranslator()
if translator.load("path_to_translation_file.ts"):
    app.installTranslator(translator)

window = WelcomeWindow()
window.show()
sys.exit(app.exec_())