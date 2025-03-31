from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import qtawesome as qta
from PyQt6.QtWidgets import QApplication

from .base_dialog import BaseDialog

class ConfirmDialog(BaseDialog):
    def __init__(self, title, message, parent=None, icon_name='fa5s.question-circle', icon_color='#ff4d4f'):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setup_ui(title, message, icon_name, icon_color)
        
    def setup_ui(self, title, message, icon_name, icon_color):
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建主容器
        main_container = QWidget(self)
        main_container.setObjectName('dialog-container')
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # 应用阴影效果到主容器
        if hasattr(self, 'graphicsEffect') and self.graphicsEffect():
            main_container.setGraphicsEffect(self.graphicsEffect())
            self.setGraphicsEffect(None)  # 移除对话框本身的阴影效果
        
        # 标题栏布局
        title_layout = QHBoxLayout()
        
        # 标题图标
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon(icon_name, color=icon_color).pixmap(24, 24))
        title_layout.addWidget(title_icon)
        
        # 标题文本
        title_label = QLabel(title)
        title_label.setObjectName('dialog-title')
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton()
        close_btn.setObjectName('close-btn')
        close_btn.setIcon(qta.icon('fa5s.times', color='#666666'))
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        main_layout.addLayout(title_layout)
        
        # 消息文本
        message_label = QLabel(message)
        message_label.setObjectName('dialog-message')
        message_label.setWordWrap(True)
        main_layout.addWidget(message_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_btn = QPushButton('取消')
        cancel_btn.setObjectName('cancel-btn')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # 确认按钮
        confirm_btn = QPushButton('确认删除')
        confirm_btn.setObjectName('confirm-btn')
        confirm_btn.clicked.connect(self.accept)
        button_layout.addWidget(confirm_btn)
        
        main_layout.addLayout(button_layout)
        
        layout.addWidget(main_container)
        
        # 设置样式
        # 设置特定于确认对话框的样式
        self.setStyleSheet(self._get_base_style() + """

        """)