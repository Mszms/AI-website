from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QScrollArea
from PyQt6.QtCore import Qt
import qtawesome as qta
from ui.components.base_dialog import BaseDialog
from config import UI_CONFIG
from ui.styles.theme_manager import theme_manager
class WebsiteDetailDialog(BaseDialog):
    def __init__(self, website_data, parent=None):
        super().__init__(parent)
        self.website_data = website_data
        self.setWindowTitle('网站详情')
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.setup_ui()
    
    def setup_ui(self):
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
        
        # 创建标题
        title_layout = QHBoxLayout()
        title_label = QLabel('网站详情')
        title_label.setObjectName('dialog-title')
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 添加关闭按钮
        close_btn = QPushButton()
        close_btn.setIcon(qta.icon('fa5s.times', color='#666666'))
        close_btn.setObjectName('close-btn')
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        main_layout.addLayout(title_layout)
        
        # 网站信息区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(16)
        
        # 网站名称和图标
        header_layout = QHBoxLayout()
        
        # 网站图标
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon = self.website_data.get('icon')
        if icon and icon.startswith('fa'):
            icon_label.setPixmap(qta.icon(icon, color=theme_manager.get_current_theme()['website_icon_color']).pixmap(32, 32))
        else:
            icon_label.setPixmap(qta.icon('fa5s.globe', color=theme_manager.get_current_theme()['website_icon_color']).pixmap(32, 32))
        header_layout.addWidget(icon_label)
        
        # 网站名称
        name_label = QLabel(self.website_data.get('name', ''))
        name_label.setObjectName('website-name')
        name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        info_layout.addLayout(header_layout)
        
        # 网站URL
        if self.website_data.get('url'):
            url_layout = QHBoxLayout()
            url_title = QLabel('网站地址:')
            url_title.setStyleSheet("font-weight: bold;")
            url_layout.addWidget(url_title)
            
            url_value = QLabel(self.website_data.get('url'))
            url_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            url_layout.addWidget(url_value)
            url_layout.addStretch()
            
            info_layout.addLayout(url_layout)
        
        # 网站描述
        if self.website_data.get('description'):
            desc_layout = QVBoxLayout()
            desc_title = QLabel('网站描述:')
            desc_title.setStyleSheet("font-weight: bold;")
            desc_layout.addWidget(desc_title)
            
            # 创建滚动区域用于长文本
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
            
            desc_content = QWidget()
            desc_content_layout = QVBoxLayout(desc_content)
            
            desc_value = QLabel(self.website_data.get('description'))
            desc_value.setStyleSheet("color: #666666;")
            desc_value.setWordWrap(True)
            desc_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            desc_content_layout.addWidget(desc_value)
            desc_content_layout.addStretch()
            
            scroll_area.setWidget(desc_content)
            desc_layout.addWidget(scroll_area)
            
            info_layout.addLayout(desc_layout)
        
        # 分类信息
        if self.website_data.get('category_name'):
            category_layout = QHBoxLayout()
            category_title = QLabel('所属分类:')
            category_title.setStyleSheet("font-weight: bold;")
            category_layout.addWidget(category_title)
            
            category_value = QLabel(self.website_data.get('category_name'))
            category_layout.addWidget(category_value)
            category_layout.addStretch()
            
            info_layout.addLayout(category_layout)
        
        # 标签信息
        if self.website_data.get('tags'):
            tags_layout = QHBoxLayout()
            tags_title = QLabel('标签:')
            tags_title.setStyleSheet("font-weight: bold;")
            tags_layout.addWidget(tags_title)
            
            tags_value = QLabel(', '.join(self.website_data.get('tags')))
            tags_layout.addWidget(tags_value)
            tags_layout.addStretch()
            
            info_layout.addLayout(tags_layout)
        
        main_layout.addLayout(info_layout)
        main_layout.addStretch()
        
        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton('确定')
        ok_btn.setObjectName('ok-btn')
        ok_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(ok_btn)
        main_layout.addLayout(button_layout)
        
        layout.addWidget(main_container)