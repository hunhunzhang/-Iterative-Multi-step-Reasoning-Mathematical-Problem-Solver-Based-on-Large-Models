from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation

class CarouselTextWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.texts = [
            ("欢迎使用数学动态演示", "探索数学的美丽与奥秘"),
            ("高效学习", "让知识变得生动有趣"),
            ("智能助手", "助你轻松解决难题")
        ]
        self.current_index = 0

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        self.setLayout(layout)

        self.label_title = QLabel()
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_title = self.label_title.font()
        font_title.setPointSize(20)
        font_title.setBold(True)
        self.label_title.setFont(font_title)
        layout.addWidget(self.label_title)

        self.label_sub = QLabel()
        self.label_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_sub = self.label_sub.font()
        font_sub.setPointSize(12)
        font_sub.setBold(False)
        self.label_sub.setFont(font_sub)
        self.label_sub.setStyleSheet("color: #444444;")
        layout.addWidget(self.label_sub)

        # 设置淡入淡出效果
        self.opacity_title = QGraphicsOpacityEffect(self.label_title)
        self.label_title.setGraphicsEffect(self.opacity_title)
        self.opacity_title.setOpacity(1.0)

        self.opacity_sub = QGraphicsOpacityEffect(self.label_sub)
        self.label_sub.setGraphicsEffect(self.opacity_sub)
        self.opacity_sub.setOpacity(1.0)

        self.update_text()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_fade_out)
        self.timer.start(5000)  # 每5秒切换一次

        self.anim_duration = 400  # 动画时长ms

    def start_fade_out(self):
        # 淡出动画
        self.anim_out_title = QPropertyAnimation(self.opacity_title, b"opacity")
        self.anim_out_title.setDuration(self.anim_duration)
        self.anim_out_title.setStartValue(1.0)
        self.anim_out_title.setEndValue(0.0)

        self.anim_out_sub = QPropertyAnimation(self.opacity_sub, b"opacity")
        self.anim_out_sub.setDuration(self.anim_duration)
        self.anim_out_sub.setStartValue(1.0)
        self.anim_out_sub.setEndValue(0.0)

        self.anim_out_title.finished.connect(self.on_fade_out_finished)

        self.anim_out_title.start()
        self.anim_out_sub.start()

    def on_fade_out_finished(self):
        self.next_text()
        # 淡入动画
        self.anim_in_title = QPropertyAnimation(self.opacity_title, b"opacity")
        self.anim_in_title.setDuration(self.anim_duration)
        self.anim_in_title.setStartValue(0.0)
        self.anim_in_title.setEndValue(1.0)

        self.anim_in_sub = QPropertyAnimation(self.opacity_sub, b"opacity")
        self.anim_in_sub.setDuration(self.anim_duration)
        self.anim_in_sub.setStartValue(0.0)
        self.anim_in_sub.setEndValue(1.0)

        self.anim_in_title.start()
        self.anim_in_sub.start()

    def update_text(self):
        title, sub = self.texts[self.current_index]
        self.label_title.setText(title)
        self.label_sub.setText(sub)

    def next_text(self):
        self.current_index = (self.current_index + 1) % len(self.texts)
        self.update_text()