import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt6.QtGui import QPainter, QColor, QIcon

from item1 import DynamicWidget  # 2D动态组件
from item2 import CarouselTextWidget  # 轮播文字组件
from app2 import UserInterface  # 用户界面

class LoginPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;  /* 白色背景 */
                border-radius: 12px;
                border: 1px solid #e557eb;
            }
            QLabel {
                color: #374151;  /* 深灰色 */
                font-size: 14px;
                font-weight: 500;
            }
            QLineEdit {
                background: #f9fafb;  /* 浅米色背景 */
                border: 1px solid #d1d5db;  /* 浅灰色边框 */
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: #111827;  /* 深绿色 */
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background: #ffffff;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 24px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 60, 40, 40)
        layout.setSpacing(20)

        self.label_username = QLabel("用户名：", self)
        self.label_username.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.label_username.setStyleSheet('''
        QLabel{
            background-color: #f3f4f6;  /* 浅米色背景 */
            padding:5px 8px;
            border-radius:5px;
            color: #374151;  /* 深灰色 */
        }
        ''')
        layout.addWidget(self.label_username)

        self.lineedit_username = QLineEdit(self)
        layout.addWidget(self.lineedit_username)

        self.label_password = QLabel("密码：", self)
        self.label_password.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.label_password.setStyleSheet('''
        QLabel{
            background-color: #f3f4f6;  /* 浅米色背景 */
            padding:5px 8px;
            border-radius:5px;
            color: #374151;  /* 深灰色 */
        }
        ''')
        layout.addWidget(self.label_password)

        self.lineedit_password = QLineEdit(self)
        self.lineedit_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.lineedit_password)

        #添加错误提示标签（初始时隐藏）
        self.label_error = QLabel("用户名或密码错误", self)
        self.label_error.setStyleSheet("color: red; font-size: 12px;")
        self.label_error.hide()
        layout.addWidget(self.label_error)

        self.button_login = QPushButton("登录", self)
        self.button_login.clicked.connect(self.handle_login)
        layout.addWidget(self.button_login)

        layout.addStretch(1)
        
        # 创建动画效果
        self.shake_animation = QPropertyAnimation(self.lineedit_password, b"geometry")
        self.shake_animation.setDuration(100)
        self.shake_animation.setLoopCount(3)
        #获取初始位置
        initial_rect = self.lineedit_password.geometry()

        # 设置关键帧（左右轻微移动，但最终回到原位）
        self.shake_animation.setKeyValueAt(0, initial_rect)
        self.shake_animation.setKeyValueAt(0.2, initial_rect.translated(-5, 0))  # 左移
        self.shake_animation.setKeyValueAt(0.4, initial_rect.translated(5, 0))   # 右移
        self.shake_animation.setKeyValueAt(0.6, initial_rect.translated(-5, 0))  # 左移
        self.shake_animation.setKeyValueAt(0.8, initial_rect.translated(5, 0))   # 右移
        self.shake_animation.setKeyValueAt(1, initial_rect)  # 回到原位
        self.button_login.clicked.connect(self.handle_login)
        layout.addWidget(self.button_login)

        layout.addStretch(1)
        
        # 动画将在showEvent中初始化，以确保获取正确的位置
        self.shake_animation = None
        
    def showEvent(self, a0):
        """在窗口显示时，如果动画尚未创建，则创建它"""
        super().showEvent(a0)
        if self.shake_animation is None:
            # 创建动画效果
            self.shake_animation = QPropertyAnimation(self.lineedit_password, b"geometry")
            self.shake_animation.setDuration(100)
            self.shake_animation.setLoopCount(3)
            
            # 获取密码框的正确初始位置
            initial_rect = self.lineedit_password.geometry()

            # 设置关键帧（左右轻微移动，但最终回到原位）
            self.shake_animation.setKeyValueAt(0, initial_rect)
            self.shake_animation.setKeyValueAt(0.2, initial_rect.translated(-5, 0))  # 左移
            self.shake_animation.setKeyValueAt(0.4, initial_rect.translated(5, 0))   # 右移
            self.shake_animation.setKeyValueAt(0.6, initial_rect.translated(-5, 0))  # 左移
            self.shake_animation.setKeyValueAt(0.8, initial_rect.translated(5, 0))   # 右移
            self.shake_animation.setKeyValueAt(1, initial_rect)  # 回到原位

    def reset_login_ui(self):
        self.label_error.hide()
        self.lineedit_username.setStyleSheet("")
        self.lineedit_password.setStyleSheet("QLineEdit { border: 1px solid red; }")
        
    def show_login_error(self):
        # 显示错误消息
        self.label_error.show()
        
        # 设置输入框红色边框
        self.lineedit_username.setStyleSheet("QLineEdit { border: 1px solid red; }")
        self.lineedit_password.setStyleSheet("QLineEdit { border: 1px solid red; }")
        
        # 启动震动动画
        if self.shake_animation:
            self.shake_animation.start()
        
        # 3秒后恢复原状
        QTimer.singleShot(3000, self.reset_login_ui)
    
    def handle_login(self):
        username = self.lineedit_username.text()
        password = self.lineedit_password.text()
        if username == "dais" and password == "123456":
            # 通过主窗口切换界面
            main_window = self.window()
            if isinstance(main_window, SoftBackgroundWindow):
                main_window.show_user_interface(username)
        else:
            self.show_login_error()

class LoginArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_panel = QWidget(self)
        self.tab_panel.setStyleSheet("""
            background-color: rgba(249, 250, 251, 0.9);
            border-radius: 18px;
        """)
        self.tab_panel.lower()  # 保证在底层

        self.login_panel = LoginPanel(self)
        self.login_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.login_panel.raise_()  # 保证在顶层

        # 用于动态调整登录面板高度
        self._update_layout()

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self._update_layout()
        

    def _update_layout(self):
        # 让tab_panel填满整个区域
        self.tab_panel.setGeometry(0, 0, self.width(), self.height())
        # 登录面板高度为4/5，居中
        panel_height = int(self.height() * 0.8)
        panel_width = int(self.width() * 0.92)
        x = (self.width() - panel_width) // 2
        y = (self.height() - panel_height) // 2
        self.login_panel.setGeometry(x, y, panel_width, panel_height)

class SoftBackgroundWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能识别题干，直击核心难点——数学从未如此清晰！")
        self.resize(1200, 700)
        
        # 创建堆叠窗口用于界面切换
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.setWindowIcon(QIcon("aislogo.png"))
        # 创建登录界面
        self.setup_login_interface()
        
        # 初始化用户界面(但不立即创建)
        self.user_interface = None

    def setup_login_interface(self):
        """设置登录界面"""
        self.login_container = QWidget()
        login_layout = QHBoxLayout(self.login_container)
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_layout.setSpacing(0)

        # 左侧垂直布局：轮播文字 + 2D动态组件
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.carousel = CarouselTextWidget()
        self.carousel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        left_layout.addWidget(self.carousel)

        self.dynamic_widget = DynamicWidget()
        self.dynamic_widget.setMinimumWidth(500)
        left_layout.addWidget(self.dynamic_widget, 1)

        login_layout.addWidget(left_widget, 1)

        # 右侧登录区
        self.login_area = LoginArea(self)
        self.login_area.setMinimumWidth(320)
        login_layout.addWidget(self.login_area, 0)
        
        # 添加到堆叠窗口
        self.stacked_widget.addWidget(self.login_container)

    def show_user_interface(self, username):
        """显示用户界面"""
        # 如果用户界面尚未创建，则创建它
        if self.user_interface is None:
            self.user_interface = UserInterface(self, username)
            self.stacked_widget.addWidget(self.user_interface)
        
        # 更新用户名
        self.user_interface.set_username(username)
        
        # 切换到用户界面
        self.stacked_widget.setCurrentWidget(self.user_interface)
        
        # 设置窗口标题
        self.setWindowTitle(f"\"妈妈，我会做数学题了！\" - 欢迎 {username}")

    def show_login_interface(self):
        """显示登录界面"""
        self.stacked_widget.setCurrentWidget(self.login_container)
        self.setWindowTitle("数学动态演示")

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 255))  # 柔和米色背景

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoftBackgroundWindow()
    window.show()
    sys.exit(app.exec())                              