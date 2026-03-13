import sys
import math
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush, QRadialGradient

class DynamicWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2D动态组件演示")
        self.resize(600, 600)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)  # 关键：背景透明
        
        # 动画参数
        self.angle = 0
        self.float_offset = 0
        self.triangle_angles = [0, 90, 180, 270]  # 4个三角形的初始角度
        
        # 启动动画定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)  # 30ms刷新

    def update_animation(self):
        self.angle = (self.angle + 1) % 360
        self.float_offset = 5 * math.sin(math.radians(self.angle * 2))
        # 转速更慢
        self.triangle_angles = [(a + 0.2) % 360 for a in self.triangle_angles]
        self.update()

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置坐标系中心为窗口中心
        center = QPointF(self.width()/2, self.height()/2)
        painter.translate(center)
        
        # 移除背景绘制
        # self.draw_background(painter)
        
        # 绘制中心双三角形
        self.draw_double_triangle(painter)
        
        # 绘制四个旋转三角形
        self.draw_orbiting_triangles(painter)
        
    def draw_background(self, painter):
        # 渐变背景
        gradient = QRadialGradient(0, 0, self.width()/2)
        gradient.setColorAt(0, QColor(30, 30, 50))
        gradient.setColorAt(1, QColor(10, 10, 20))
        painter.fillRect(-self.width()//2, -self.height()//2, 
                        self.width(), self.height(), QBrush(gradient))
    
    def draw_double_triangle(self, painter):
        size = 60
        y_offset = self.float_offset
        
        # 上三角形（橙红色）
        painter.setBrush(QColor(200, 80, 50, 200))
        painter.setPen(Qt.PenStyle.NoPen)
        top_triangle = [
            QPointF(0, -size + y_offset),
            QPointF(-size, size + y_offset),
            QPointF(size, size + y_offset)
        ]
        painter.drawPolygon(top_triangle)
        
        # 下三角形（深红色）
        painter.setBrush(QColor(150, 50, 30, 200))
        bottom_triangle = [
            QPointF(0, size - y_offset),
            QPointF(-size, -size - y_offset),
            QPointF(size, -size - y_offset)
        ]
        painter.drawPolygon(bottom_triangle)

    def draw_orbiting_triangles(self, painter):
        orbit_radius = 100  # 距离更近
        tri_size = 80       # 三角形更大
        color_start = (255, 120, 40)   # 橙红
        color_end = (120, 30, 20)      # 深红
        for i, angle in enumerate(self.triangle_angles):
            real_angle = (angle + self.angle) % 360
            t = real_angle / 360  # 角度归一化到0~1
            r = int(color_start[0] * (1 - t) + color_end[0] * t)
            g = int(color_start[1] * (1 - t) + color_end[1] * t)
            b = int(color_start[2] * (1 - t) + color_end[2] * t)
            color = QColor(r, g, b, 220)

            rad = math.radians(real_angle)
            x = orbit_radius * math.cos(rad)
            y = orbit_radius * math.sin(rad)
            points = [
                QPointF(x, y - tri_size),
                QPointF(x - tri_size * 0.5, y + tri_size * 0.7),
                QPointF(x + tri_size * 0.5, y + tri_size * 0.7)
            ]
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(points)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicWidget()
    window.show()
    sys.exit(app.exec())