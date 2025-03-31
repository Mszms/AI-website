from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, pyqtProperty
from PyQt6.QtGui import QPixmap, QColor
import qtawesome as qta
import os
from ui.styles.theme_manager import theme_manager

class WebsiteCard(QWidget):
    clicked = pyqtSignal(str)  # 点击卡片时发出信号，传递网站URL
    edit_clicked = pyqtSignal(dict)  # 编辑按钮点击信号
    delete_clicked = pyqtSignal(str)  # 删除按钮点击信号
    detail_clicked = pyqtSignal(dict)  # 详情按钮点击信号

    def __init__(self, website_data, parent=None):
        super().__init__(parent)
        self.website_data = website_data
        self._card_hover = 0.0
        self._card_scale = 1.0
        self._setup_shadow()
        self.setup_ui()
        self._setup_animations()
        
        # 默认隐藏编辑、详情和删除按钮
        self.detail_btn.setVisible(False)
        self.edit_btn.setVisible(False)
        self.delete_btn.setVisible(False)
        
        # 设置鼠标跟踪，以便接收鼠标进入和离开事件
        self.setMouseTracking(True)
        
    # 定义卡片悬停属性
    def _get_card_hover(self):
        return self._card_hover
        
    def _set_card_hover(self, value):
        self._card_hover = value
        self._update_hover_effect()
        
    card_hover = pyqtProperty(float, _get_card_hover, _set_card_hover)
    
    # 定义卡片缩放属性
    def _get_card_scale(self):
        return self._card_scale
        
    def _set_card_scale(self, value):
        self._card_scale = value
        self._update_scale_effect()
        
    card_scale = pyqtProperty(float, _get_card_scale, _set_card_scale)
    
    def _update_hover_effect(self):
        # 根据悬停值更新阴影和上浮效果
        if hasattr(self, 'graphicsEffect') and self.graphicsEffect():
            shadow = self.graphicsEffect()
            # 插值计算阴影参数
            blur = 20 + 8 * self._card_hover  # 20到28
            alpha = int(40 + 20 * self._card_hover)  # 40到60，确保是整数
            offset = 4 + 2 * self._card_hover  # 4到6
            shadow.setBlurRadius(blur)
            shadow.setColor(QColor(0, 0, 0, alpha))
            shadow.setOffset(0, offset)
            
            # 上浮效果通过margin实现
            margin = 2 * self._card_hover
            self.setContentsMargins(0, 0, 0, int(margin))
    
    def _update_scale_effect(self):
        # 更新缩放效果 - 使用QTransform代替CSS transform
        if hasattr(self, '_card_scale'):
            # 使用几何变换代替CSS transform
            original_width = 280
            original_height = 180
            self.resize(int(original_width * self._card_scale), int(original_height * self._card_scale))
    
    def _setup_animations(self):
        # 卡片悬停动画
        self.hover_animation = QPropertyAnimation(self, b'card_hover')
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        # 设置初始值和结束值
        self.hover_animation.setStartValue(0.0)
        self.hover_animation.setEndValue(1.0)
        
        # 卡片点击动画
        self.click_animation = QPropertyAnimation(self, b'card_scale')
        self.click_animation.setDuration(100)
        self.click_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        # 设置初始值和结束值
        self.click_animation.setStartValue(1.0)
        self.click_animation.setEndValue(1.2)
        
        # 动画组
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.hover_animation)
        self.animation_group.addAnimation(self.click_animation)
    
    def _setup_shadow(self):
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def setup_ui(self):
        # 设置卡片样式
        self.setObjectName('website-card')
        self.setFixedSize(280, 180)
        # 直接设置背景色 - 确保在设置样式表之前设置
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)  # 允许样式表设置背景
        self.setAutoFillBackground(True)  # 确保背景自动填充
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(255, 255, 255))
        self.setPalette(palette)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # 顶部布局：网站图标和操作按钮
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)
        
        # 网站图标
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)  # 确保图标标签有固定大小
        icon_label.setObjectName('website-icon')
        icon = self.website_data.get('icon')
        try:
            if icon:
                if not icon.startswith('http'):
                    if icon.startswith('fa'):
                        # 使用qtawesome图标
                        icon_label.setPixmap(qta.icon(icon, color=theme_manager.get_current_theme()['website_icon_color']).pixmap(18, 18))
                    elif os.path.isabs(icon) and os.path.exists(icon):
                        # 处理绝对路径
                        pixmap = QPixmap(icon)
                        if not pixmap.isNull():
                            icon_label.setPixmap(pixmap.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        else:
                            print(f"无法加载图标文件: {icon}")
                            icon_label.setPixmap(qta.icon('fa5s.globe', color=theme_manager.get_current_theme()['website_icon_color']).pixmap(18, 18))
                    elif icon.startswith('ui/resources/icons/'):
                        # 使用本地图标文件
                        # 尝试在项目根目录中查找
                        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        abs_path = os.path.join(project_root, icon)
                        
                        # 如果在项目根目录中找不到，尝试在用户数据目录中查找
                        if not os.path.exists(abs_path):
                            user_data_dir = os.path.join(os.path.expanduser('~'), '.daohan_navigator')
                            abs_path = os.path.join(user_data_dir, icon)
                        
                        if os.path.exists(abs_path):
                            pixmap = QPixmap(abs_path)
                            if not pixmap.isNull():
                                icon_label.setPixmap(pixmap.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                            else:
                                print(f"无法加载图标文件: {abs_path}")
                                icon_label.setPixmap(qta.icon('fa5s.globe', color=theme_manager.get_current_theme()['website_icon_color']).pixmap(18, 18))
                        else:
                            print(f"图标文件不存在: {abs_path}")
                            icon_label.setPixmap(qta.icon('fa5s.globe', color=theme_manager.get_current_theme()['website_icon_color']).pixmap(18, 18))
                    else:
                        # 无效的图标路径
                        print(f"无效的图标路径格式: {icon}")
                        icon_label.setPixmap(qta.icon('fa5s.globe', color=theme_manager.get_current_theme()['website_icon_color']).pixmap(18, 18))
                else:
                    # 使用默认图标（暂不支持网络图标）
                    icon_label.setPixmap(qta.icon('fa5s.globe', color=theme_manager.get_current_theme()['website_icon_color']).pixmap(18, 18))
            else:
                # 没有图标，使用默认图标
                icon_label.setPixmap(qta.icon('fa5s.globe', color=theme_manager.get_current_theme()['website_icon_color']).pixmap(18, 18))
        except Exception as e:
            print(f"加载图标失败: {e}")
            # 加载失败时使用默认图标
            icon_label.setPixmap(qta.icon('fa5s.globe', color=theme_manager.get_current_theme()['website_icon_color']).pixmap(18, 18))
        top_layout.addWidget(icon_label)
        
        # 网站名称
        name_text = self.website_data['name']
        # 截断过长的名称文本，最多显示20个字符
        if len(name_text) > 20:
            name_text = name_text[:20] + '...'
        name_label = QLabel(name_text)
        name_label.setObjectName('website-name')
        top_layout.addWidget(name_label)
        top_layout.addStretch()
        
        # 操作按钮组
        self.detail_btn = QPushButton()
        self.detail_btn.setFixedSize(28, 28)  # 设置按钮固定大小
        self.detail_btn.setIcon(qta.icon('fa5s.info-circle', color='#666666'))
        self.detail_btn.clicked.connect(lambda: self.detail_clicked.emit(self.website_data))
        
        self.edit_btn = QPushButton()
        self.edit_btn.setFixedSize(28, 28)  # 设置按钮固定大小
        self.edit_btn.setIcon(qta.icon('fa5s.edit', color='#666666'))
        self.edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.website_data))
        
        self.delete_btn = QPushButton()
        self.delete_btn.setFixedSize(28, 28)  # 设置按钮固定大小
        self.delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#666666'))
        self.delete_btn.clicked.connect(lambda: self.delete_clicked.emit(str(self.website_data['_id'])))
        
        top_layout.addWidget(self.detail_btn)
        top_layout.addWidget(self.edit_btn)
        top_layout.addWidget(self.delete_btn)
        layout.addLayout(top_layout)
        
        # 网站描述
        if self.website_data.get('description'):
            desc_text = self.website_data['description']
            # 截断过长的描述文本，最多显示40个字符
            if len(desc_text) > 40:
                desc_text = desc_text[:40] + '...'
            desc_label = QLabel(desc_text)
            desc_label.setObjectName('website-description')
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # 底部布局：标签
        if self.website_data.get('tags'):
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(6)
            for tag in self.website_data['tags']:
                tag_label = QLabel(tag)
                tag_label.setObjectName('website-tag')
                tags_layout.addWidget(tag_label)
            tags_layout.addStretch()
            layout.addLayout(tags_layout)
        
        layout.addStretch()
        
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        # 设置样式
        self.setStyleSheet(f"""
            #website-card {{
                background-color: {theme['card_background']} !important;
                border-radius: 12px;
                border: 1px solid {theme['menu_border'] if theme['theme_name'] == '暗夜主题' else 'rgba(0, 0, 0, 0.08)'};
                position: relative; /* 添加相对定位 */
            }}
            #website-name {{
                font-size: 16px;
                font-weight: 600;
                color: {theme['text_color']};
                letter-spacing: 0.3px;
            }}
            #website-description {{
                color: {theme['text_color']};
                font-size: 12px;
                margin-top: 6px;
                line-height: 1.8;
                opacity: 0.9;
            }}
            #website-tag {{
                background-color: {theme['tag_background']};
                color: {theme['primary_color']};
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 12px;
                margin-right: 6px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            #website-icon {{
                background-color: {theme['tag_background']};
                border-radius: 16px;
                padding: 7px;
            }}
            QPushButton {{
                border: none;
                padding: 4px;
                border-radius: 8px;
                background-color: transparent;
                position: relative; /* 添加相对定位 */
            }}
            QPushButton:hover {{
                background-color: rgba(30, 136, 229, 0.15);
            }}
            QLabel {{
                position: relative; /* 为所有标签添加相对定位 */
            }}
        """)

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # 显示编辑、详情和删除按钮
        self.detail_btn.setVisible(True)
        self.edit_btn.setVisible(True)
        self.delete_btn.setVisible(True)
        # 悬停动画 - 轻微上浮效果，使用与_setup_animations中相同的值范围
        self.hover_animation.setStartValue(0.0)
        self.hover_animation.setEndValue(1.0)
        self.click_animation.setStartValue(1.0)  # 确保缩放动画也有正确的值
        self.click_animation.setEndValue(1.2)  # 确保缩放动画也有正确的值
        self.animation_group.start()

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        # 隐藏编辑、详情和删除按钮
        self.detail_btn.setVisible(False)
        self.edit_btn.setVisible(False)
        self.delete_btn.setVisible(False)
        # 恢复原始状态，使用与_setup_animations中相同的值范围
        self.hover_animation.setStartValue(1.0)
        self.hover_animation.setEndValue(0.0)
        self.click_animation.setStartValue(1.2)  # 确保缩放动画也有正确的值
        self.click_animation.setEndValue(1.0)  # 确保缩放动画也有正确的值
        self.animation_group.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 点击动画 - 缩小效果
            self.click_animation.setStartValue(1.0)
            self.click_animation.setEndValue(1.2)
            self.animation_group.start()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 释放动画 - 恢复大小
            self.click_animation.setStartValue(1.2)
            self.click_animation.setEndValue(1.0)
            self.animation_group.start()
            
            # 检查事件源，如果不是来自按钮的事件才发出clicked信号
            # 这样可以避免点击编辑或删除按钮时同时打开网站
            child = self.childAt(event.position().toPoint())
            if not isinstance(child, QPushButton):
                self.clicked.emit(self.website_data['url'])