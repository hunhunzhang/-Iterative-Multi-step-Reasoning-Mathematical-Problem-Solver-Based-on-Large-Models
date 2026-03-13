from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit,
    QHBoxLayout, QMessageBox, QSplitter, QFrame, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from llm_service import DeepSeekService
from setting_panel import SettingsDialog

class MetricsPanel(QFrame):
    """用于实时显示指标的侧边栏面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.set_style()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("实时指标")
        title.setFont(QFont("sans-serif", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        # Token 相关标签
        self.current_prompt_tokens_label = QLabel("0")
        self.current_completion_tokens_label = QLabel("0")
        self.current_total_tokens_label = QLabel("0")
        self.total_prompt_tokens_label = QLabel("0")
        self.total_completion_tokens_label = QLabel("0")
        self.total_total_tokens_label = QLabel("0")
        
        # 成本和时间标签
        self.current_cost_label = QLabel("$0.0000")
        self.total_cost_label = QLabel("$0.0000")
        self.current_time_label = QLabel("0.00 s")
        self.total_time_label = QLabel("0.00 s")

        # 添加当前迭代 Token 信息
        current_section = QLabel("当前迭代")
        current_section.setFont(QFont("sans-serif", 12, QFont.Weight.Bold))
        current_section.setStyleSheet("color: #374151; margin-top: 10px;")
        form_layout.addRow(current_section)
        
        form_layout.addRow("Prompt Tokens:", self.current_prompt_tokens_label)
        form_layout.addRow("Completion Tokens:", self.current_completion_tokens_label)
        form_layout.addRow("Total Tokens:", self.current_total_tokens_label)
        form_layout.addRow("花费:", self.current_cost_label)
        form_layout.addRow("耗时:", self.current_time_label)
        
        form_layout.addRow(self.create_separator())
        
        # 添加总计 Token 信息
        total_section = QLabel("总计")
        total_section.setFont(QFont("sans-serif", 12, QFont.Weight.Bold))
        total_section.setStyleSheet("color: #374151; margin-top: 10px;")
        form_layout.addRow(total_section)
        
        form_layout.addRow("Prompt Tokens:", self.total_prompt_tokens_label)
        form_layout.addRow("Completion Tokens:", self.total_completion_tokens_label)
        form_layout.addRow("Total Tokens:", self.total_total_tokens_label)
        form_layout.addRow("总花费:", self.total_cost_label)
        form_layout.addRow("总耗时:", self.total_time_label)

        layout.addLayout(form_layout)
        layout.addStretch()

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #e5e7eb; margin: 5px 0;")
        return line

    def set_style(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            MetricsPanel {
                background-color: #f8fafc;
                border-left: 1px solid #e5e7eb;
            }
            QLabel {
                font-size: 13px;
                color: #374151;
            }
        """)

    def update_metrics(self, metrics):
        """用新数据更新所有指标标签"""
        # 当前迭代指标
        self.current_prompt_tokens_label.setText(str(metrics.get("current_prompt_tokens", 0)))
        self.current_completion_tokens_label.setText(str(metrics.get("current_completion_tokens", 0)))
        self.current_total_tokens_label.setText(str(metrics.get("current_total_tokens", 0)))
        self.current_cost_label.setText(f"${metrics.get('current_cost', 0):.6f}")
        self.current_time_label.setText(f"{metrics.get('current_time', 0):.2f} s")
        
        # 总计指标
        self.total_prompt_tokens_label.setText(str(metrics.get("total_prompt_tokens", 0)))
        self.total_completion_tokens_label.setText(str(metrics.get("total_completion_tokens", 0)))
        self.total_total_tokens_label.setText(str(metrics.get("total_tokens", 0)))
        self.total_cost_label.setText(f"${metrics.get('total_cost', 0):.6f}")
        self.total_time_label.setText(f"{metrics.get('total_time', 0):.2f} s")

class UserInterface(QWidget):
    def __init__(self, parent=None, username="用户"):
        super().__init__(parent)
        self.main_window = parent
        self.username = username
        self.llm_service = DeepSeekService(self)
        self.llm_service.iteration_complete.connect(self.handle_iteration_complete)

        self.model_settings = {
            "system_prompt": """你是一个用于解决数学问题的多智能体系统中的推理智能体。整个推理过程被分解为多个迭代步骤，由多个专业智能体共同完成。每次被调用时，你必须根据提供的上下文执行恰好一个操作。
操作（每次响应选择一个）：
初始思考
触发条件：没有之前的思考或总结（全新的开始）
操作：在<think>标签内阐述初始推理过程
token最大长度限制：{100}
总结生成
触发条件：存在之前的思考并且还需要进一步推理
操作：在<summary>标签内提供总结
要求：
捕捉所有关键的推理要点和当前状态
确保总结是自包含的，以便下一个智能体使用
token最大长度限制：{50}
继续推理
触发条件：前一个智能体提供了总结，但没有附带思考过程
操作：在<think>标签内继续推理过程
要求：
仅基于提供的总结进行推理
有意义地推进推理过程
除非为了清晰起见，否则不要重复之前的工作
token最大长度限制：{50}
最终答案
触发条件：推理过程已完成
操作：在<answer>标签内提供答案
要求：
仅包含最简洁的最终的数值或文本结果
只有在确信问题已完全解决时才使用
关键指导原则：
中文友好系统：以中文思维理解问题，并使用中文进行回答
单一操作规则：每个响应恰好包含一个操作，不得合并多个操作
总结的重要性：下一个智能体仅接收总结和原始问题，而不是完整的思考历史
完成阈值：只有在解决方案完整且经过验证时，才提供最终答案
推理的连贯性：每个步骤必须逻辑上基于之前的工作，并朝着解决方案推进
流程：
初始思考 → 总结 → 继续推理 → 总结 → ... → 最终答案
在提供最终答案后，流程终止。""",
            "temperature": 0.7
        }
        
        # 初始化指标数据
        self.metrics_data = {
            "current_prompt_tokens": 0,
            "current_completion_tokens": 0,
            "current_total_tokens": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "current_cost": 0.0,
            "total_cost": 0.0,
            "current_time": 0.0,
            "total_time": 0.0
        }
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 中间聊天区
        chat_widget = self.create_chat_widget()
        splitter.addWidget(chat_widget)

        # 右侧指标面板
        self.metrics_panel = MetricsPanel()
        splitter.addWidget(self.metrics_panel)

        # 设置初始尺寸比例
        splitter.setSizes([800, 250])
        splitter.setCollapsible(0, False) # 防止聊天区被完全折叠

        main_layout.addWidget(splitter)
        self.setStyleSheet("background-color: #ffffff;")
        
        # 初始化指标显示
        self.update_metrics_display()

    def create_chat_widget(self):
        """创建聊天界面的主部件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("sans-serif", 12))
        self.chat_display.setStyleSheet("background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px;")
        layout.addWidget(self.chat_display, 1)

        input_layout = QHBoxLayout()
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("请输入你的数学问题...")
        self.user_input.setFont(QFont("sans-serif", 11))
        self.user_input.setStyleSheet("padding: 10px; border: 1px solid #d1d5db; border-radius: 8px;")
        self.user_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.user_input)

        settings_button = QPushButton("设置")
        settings_button.setFont(QFont("sans-serif", 11))
        settings_button.setStyleSheet("""
            QPushButton { background-color: #6b7280; color: white; padding: 10px 20px; border-radius: 8px; border: none; }
            QPushButton:hover { background-color: #4b5563; }
        """)
        settings_button.clicked.connect(self.open_settings_dialog)
        input_layout.addWidget(settings_button)

        send_button = QPushButton("发送")
        send_button.setFont(QFont("sans-serif", 11, QFont.Weight.Bold))
        send_button.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; padding: 10px 20px; border-radius: 8px; border: none; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)
        
        layout.addLayout(input_layout)
        return widget

    def update_metrics_display(self):
        """使用当前数据更新指标面板"""
        self.metrics_panel.update_metrics(self.metrics_data)

    def open_settings_dialog(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self, self.model_settings)
        if dialog.exec():
            self.model_settings = dialog.get_settings()
            self.append_message("System", "<font color='green'>设置已更新。</font>")

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        if hasattr(self, 'llm_service') and self.llm_service:
            self.llm_service.stop_iteration()
        event.accept()

    def send_message(self):
        user_text = self.user_input.text().strip()
        if not user_text:
            return
        max_iterations = 50
        
        # 停止之前的迭代（如果有的话）
        if hasattr(self, 'llm_service') and self.llm_service:
            self.llm_service.stop_iteration()

        self.append_message("You", user_text)
        self.user_input.clear()
        
        # 重置指标数据（开始新问题）
        self.metrics_data = {
            "current_prompt_tokens": 0,
            "current_completion_tokens": 0,
            "current_total_tokens": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "current_cost": 0.0,
            "total_cost": 0.0,
            "current_time": 0.0,
            "total_time": 0.0
        }

        self.update_metrics_display()

        self.append_message("DeepSeek", "<i>正在思考中...</i>")
        
        api_key = "sk-EEQLw6Rp2J64TGqc056fF8F3D3A748A8B28dC6C6DdDc33A2"
        base_url = "https://api.bltcy.ai/v1/chat/completions"

        self.llm_service.start_iterative_response(
            api_key,
            base_url,
            self.model_settings["system_prompt"],
            user_text,
            self.model_settings["temperature"],
            max_iterations
        ) 

    def handle_iteration_complete(self, response, is_final, metrics):
        """处理每次迭代完成的响应"""
        # 更新指标数据
        self.metrics_data.update(metrics)
        self.update_metrics_display()
    
        # 移除"正在思考中..."的消息
        current_html = self.chat_display.toHtml()
        last_p_index = current_html.rfind('<p ')
        if last_p_index != -1 and "正在思考中" in current_html[last_p_index:]:
            self.chat_display.setHtml(current_html[:last_p_index])

        # 显示当前迭代的响应
        iteration_info = f"第 {self.llm_service.current_iteration} 次迭代"
        if is_final:
            iteration_info += " (最终答案)"
        
        # 添加指标信息到响应中
        metrics_info = (f"Prompt: {metrics['current_prompt_tokens']}, "
                       f"Completion: {metrics['current_completion_tokens']}, "
                       f"Total: {metrics['current_total_tokens']}, "
                       f"花费: ${metrics['current_cost']:.6f}, "
                       f"耗时: {metrics['current_time']:.2f}s")
               
        self.append_message("DeepSeek", f"<b>{iteration_info}:</b> <small>({metrics_info})</small><br>{response}")    

    def handle_llm_error(self, error_message):
        QMessageBox.critical(self, "API 错误", error_message)
        current_html = self.chat_display.toHtml()
        last_p_index = current_html.rfind('<p ')
        if last_p_index != -1:
            self.chat_display.setHtml(current_html[:last_p_index])
        self.append_message("System", f"<font color='red'>错误: {error_message}</font>")

    def append_message(self, sender, message):
        sender_color = "#3b82f6" if sender == "You" else "#10b981"
        if sender == "System":
            sender_color = "#6b7280"
            
        formatted_message = f'<p style="margin-bottom: 10px;"><b><font color="{sender_color}">{sender}:</font></b><br>{message.replace(chr(10), "<br>")}</p>'
        self.chat_display.append(formatted_message)
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_username(self, username):
        self.username = username

    def logout(self):
        """退出登录返回登录界面"""
        reply = QMessageBox.question(
            self, '确认退出', '确定要退出登录吗?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes and self.main_window:
            self.main_window.show_login_interface()