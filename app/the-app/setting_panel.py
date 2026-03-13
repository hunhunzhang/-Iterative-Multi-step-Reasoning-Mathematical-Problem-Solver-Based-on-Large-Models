from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QDoubleSpinBox,
    QFormLayout, QDialogButtonBox
)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("模型设置")
        self.setMinimumWidth(400)
        self.init_ui(current_settings)
        self.set_style()

    def init_ui(self, current_settings):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # 系统提示词
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("输入系统提示词，指导模型的行为。")
        self.prompt_edit.setMinimumHeight(150)
        form_layout.addRow(QLabel("系统提示词:"), self.prompt_edit)

        # 温度参数
        self.temperature_spinbox = QDoubleSpinBox()
        self.temperature_spinbox.setRange(0.0, 2.0)
        self.temperature_spinbox.setSingleStep(0.1)
        form_layout.addRow(QLabel("温度 (Temperature):"), self.temperature_spinbox)
        
        layout.addLayout(form_layout)

        # 如果有当前设置，则加载
        if current_settings:
            self.prompt_edit.setText(current_settings.get("system_prompt", "你是一个专业的数学解题助手。请逐步思考，并给出详细的解题步骤。"))
            self.temperature_spinbox.setValue(current_settings.get("temperature", 0.7))
        else: # 否则使用默认值
            self.prompt_edit.setText("你是一个专业的数学解题助手。请逐步思考，并给出详细的解题步骤。")
            self.temperature_spinbox.setValue(0.7)

        # 确定和取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def set_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QLabel {
                font-size: 13px;
                color: #374151;
            }
            QTextEdit, QDoubleSpinBox {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)

    def get_settings(self):
        """返回当前对话框中的设置"""
        return {
            "system_prompt": self.prompt_edit.toPlainText(),
            "temperature": self.temperature_spinbox.value()
        }