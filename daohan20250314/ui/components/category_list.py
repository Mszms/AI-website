from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QMenu
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup, pyqtProperty
from PyQt6.QtGui import QColor
import qtawesome as qta
from config import UI_CONFIG
from ui.styles.theme_manager import theme_manager

class CategoryItem(QWidget):
    clicked = pyqtSignal(str)  # 点击分类时发出信号，传递分类ID
    edit_category = pyqtSignal(dict)  # 编辑分类信号
    delete_category = pyqtSignal(str)  # 删除分类信号
    toggle_children = pyqtSignal(str, bool)  # 切换子分类显示状态信号
    
    def __init__(self, category_data, parent=None, is_child=False, has_children=False):
        super().__init__(parent)
        self.category_data = category_data
        self.is_selected = False
        self.is_child = is_child  # 是否为子分类
        self.is_expanded = False  # 是否展开子分类
        self.has_children = has_children  # 是否有子分类
        # 初始化时设置背景色为透明蓝色，确保alpha为0
        self._background_color = QColor(0, 90, 234, 0)
        self._scale = 1.0
        self.setup_ui()
        self._setup_animations()
        
    # 定义背景色属性
    def _get_background_color(self):
        return self._background_color
        
    def _set_background_color(self, color):
        self._background_color = color
        # 直接应用背景色变化
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # 确保自动填充背景
        self.update()  # 强制重绘
        self.update_style()
        
    background_color = pyqtProperty(QColor, _get_background_color, _set_background_color)
    
    # 定义缩放属性
    def _get_scale(self):
        return self._scale
        
    def _set_scale(self, scale):
        self._scale = scale
        self.setGeometry(self.geometry())  # 触发重绘
        
    scale = pyqtProperty(float, _get_scale, _set_scale)
    
    def _setup_animations(self):
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        # 确保动画组对象有效 - 必须先创建动画组
        if not hasattr(self, 'animation_group') or self.animation_group is None:
            self.animation_group = QParallelAnimationGroup()
        else:
            # 清除现有动画组中的所有动画，避免重复添加
            self.animation_group.clear()
        
        # 背景色动画 - 检查现有动画是否有效，如果无效则重新创建
        if not hasattr(self, 'bg_animation') or self.bg_animation is None:
            self.bg_animation = QPropertyAnimation(self, b'background_color')
            self.bg_animation.setDuration(200)
            self.bg_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 设置初始值和结束值 - 使用主题颜色
        primary_color = QColor(theme['primary_color'])
        # 透明版本的主色调
        transparent_primary = QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 0)
        # 半透明的悬停颜色
        hover_color = QColor(theme['hover_color'])
        hover_color.setAlpha(80)
        
        # 确保动画对象有效后再设置值
        if hasattr(self, 'bg_animation') and self.bg_animation is not None:
            try:
                self.bg_animation.setStartValue(transparent_primary)  # 透明主色调
                self.bg_animation.setEndValue(hover_color)  # 半透明悬停色
                # 安全地添加到动画组
                self.animation_group.addAnimation(self.bg_animation)
            except RuntimeError:
                # 如果动画对象已被删除，重新创建
                self.bg_animation = QPropertyAnimation(self, b'background_color')
                self.bg_animation.setDuration(200)
                self.bg_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                self.bg_animation.setStartValue(transparent_primary)
                self.bg_animation.setEndValue(hover_color)
                self.animation_group.addAnimation(self.bg_animation)
        
        # 缩放动画 - 检查现有动画是否有效，如果无效则重新创建
        if not hasattr(self, 'click_animation') or self.click_animation is None:
            self.click_animation = QPropertyAnimation(self, b'scale')
            self.click_animation.setDuration(100)
            self.click_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            # 设置初始值和结束值
            self.click_animation.setStartValue(1.0)
            self.click_animation.setEndValue(0.98)
        
        # 安全地添加缩放动画到动画组
        if hasattr(self, 'click_animation') and self.click_animation is not None:
            try:
                self.animation_group.addAnimation(self.click_animation)
            except RuntimeError:
                # 如果动画对象已被删除，重新创建
                self.click_animation = QPropertyAnimation(self, b'scale')
                self.click_animation.setDuration(100)
                self.click_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                self.click_animation.setStartValue(1.0)
                self.click_animation.setEndValue(0.98)
                self.animation_group.addAnimation(self.click_animation)
        
    def setup_ui(self):
        self.setObjectName('category-item')
        self.setFixedHeight(40)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        # 如果是子分类，添加缩进
        if self.is_child:
            indent_widget = QWidget()
            indent_widget.setFixedWidth(20)
            layout.addWidget(indent_widget)
        
        # 如果有子分类，添加展开/折叠按钮
        self.toggle_btn = None
        if self.has_children:
            self.toggle_btn = QPushButton()
            self.toggle_btn.setIcon(qta.icon('fa5s.chevron-right', color='white'))
            self.toggle_btn.setObjectName('toggle-btn')
            self.toggle_btn.setFixedSize(16, 16)
            self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.toggle_btn.clicked.connect(self.toggle_children_visibility)
            # 设置透明背景
            self.toggle_btn.setStyleSheet("""QPushButton#toggle-btn {
                background-color: transparent;
                border: none;
            }
            """)
            layout.addWidget(self.toggle_btn)
        elif not self.is_child:  # 如果不是子分类且没有子分类，添加占位
            spacer = QWidget()
            spacer.setFixedWidth(16)
            layout.addWidget(spacer)
        
        # 分类图标
        self.icon_label = QLabel()
        if self.category_data.get('icon'):
            try:
                self.icon_label.setPixmap(qta.icon(self.category_data['icon'], color='white').pixmap(16, 16))
            except Exception:
                # 如果图标名称无效，使用默认图标
                self.icon_label.setPixmap(qta.icon('fa5s.folder', color='white').pixmap(16, 16))
        else:
            self.icon_label.setPixmap(qta.icon('fa5s.folder', color='white').pixmap(16, 16))
        layout.addWidget(self.icon_label)
        
        # 分类名称
        self.name_label = QLabel(self.category_data['name'])
        self.name_label.setObjectName('category-name')
        layout.addWidget(self.name_label)
        layout.addStretch()
        
        # 设置样式
        self.update_style()
        
        # 设置上下文菜单策略
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def toggle_children_visibility(self):
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        self.is_expanded = not self.is_expanded
        # 更新展开/折叠按钮图标
        if self.toggle_btn:
            if self.is_expanded:
                # 使用主题颜色
                icon_color = theme['primary_color'] if self.is_selected else theme['light_text_color']
                self.toggle_btn.setIcon(qta.icon('fa5s.chevron-down', color=icon_color))
            else:
                # 使用主题颜色
                icon_color = theme['primary_color'] if self.is_selected else theme['light_text_color']
                self.toggle_btn.setIcon(qta.icon('fa5s.chevron-right', color=icon_color))
        # 发送信号通知父组件切换子分类显示状态
        self.toggle_children.emit(str(self.category_data['_id']), self.is_expanded)
        
    def show_context_menu(self, pos):
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        # 创建右键菜单
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {theme['menu_background']};
                border: 1px solid {theme['menu_border']};
                border-radius: 8px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 4px;
                margin: 2px 5px;
                color: {theme['text_color']};
            }}
            QMenu::item:selected {{
                background-color: {theme['menu_hover']};
            }}
        """)
        
        # 添加编辑和删除操作
        edit_action = menu.addAction(qta.icon('fa5s.edit', color='#666'), "编辑分类")
        delete_action = menu.addAction(qta.icon('fa5s.trash-alt', color='#d32f2f'), "删除分类")
        
        # 如果是顶级分类，添加"添加子分类"选项
        add_child_action = None
        if not self.is_child:
            add_child_action = menu.addAction(qta.icon('fa5s.plus', color='#666'), "添加子分类")
        
        # 显示菜单并获取用户选择的操作
        action = menu.exec(self.mapToGlobal(pos))
        
        # 处理用户选择
        if action == edit_action:
            self.edit_category.emit(self.category_data)
        elif action == delete_action:
            self.delete_category.emit(str(self.category_data['_id']))
        elif action == add_child_action:
            # 发送编辑信号，但标记为添加子分类
            category_data = self.category_data.copy()
            category_data['add_child'] = True  # 添加标记
            self.edit_category.emit(category_data)
        
    def update_style(self):
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        # 如果选中，根据主题设置背景色和文字颜色
        if self.is_selected:
            bg_color = theme['card_background']  # 使用主题卡片背景色
            text_color = theme['primary_color']  # 选中时文字使用主色调
        else:
            # 未选中时使用主题主色调
            bg_color = theme['primary_color']
            text_color = theme['light_text_color']  # 未选中时文字为浅色
        
        # 直接设置背景色，确保能被应用
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(bg_color))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # 确保自动填充背景
        
        # 使用更高优先级的样式设置
        self.setStyleSheet(f"""
            QWidget#category-item {{  
                background-color: {bg_color} !important;
                border: none;
                border-radius: 8px;
                margin: 0 8px;
            }}
            QLabel#category-name {{
                color: {text_color};
                font-size: 14px;
            }}
        """)
        
        # 应用缩放效果 - 不使用CSS transform
        if hasattr(self, '_scale'):
            # 通过调整大小实现缩放效果
            width = self.width()
            height = self.height()
            self.resize(int(width * self._scale), int(height * self._scale))
    
    def enterEvent(self, event):
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        # 无论是否选中，都显示指针光标
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # 只有在未选中状态下才启动悬停动画
        if not self.is_selected:
            # 确保动画有正确的起始值和结束值
            current_color = self._background_color
            # 使用主题的悬停颜色
            hover_color = QColor(theme['hover_color'])
            # 确保有一定的透明度
            hover_color.setAlpha(80)
            
            self.bg_animation.setStartValue(current_color)
            self.bg_animation.setEndValue(hover_color)
            self.click_animation.setStartValue(1.0)
            self.click_animation.setEndValue(1.02)
            self.animation_group.start()
            
            # 直接设置背景色，确保立即可见
            palette = self.palette()
            palette.setColor(self.backgroundRole(), hover_color)
            self.setPalette(palette)

    def leaveEvent(self, event):
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        # 无论是否选中，都恢复默认光标
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        if not self.is_selected:
            # 确保动画有正确的起始值和结束值
            current_color = self._background_color
            # 使用主题主色调，但完全透明
            primary_color = QColor(theme['primary_color'])
            target_color = QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 0)
            
            self.bg_animation.setStartValue(current_color)
            self.bg_animation.setEndValue(target_color)
            self.click_animation.setStartValue(1.02)
            self.click_animation.setEndValue(1.0)
            self.animation_group.start()
            
            # 直接设置背景色，确保立即可见
            palette = self.palette()
            palette.setColor(self.backgroundRole(), target_color)
            self.setPalette(palette)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 点击动画
            self.click_animation.setStartValue(1.02)
            self.click_animation.setEndValue(0.98)
            self.animation_group.start()
            self.clicked.emit(str(self.category_data['_id']))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 释放动画
            self.click_animation.setStartValue(0.98)
            self.click_animation.setEndValue(1.0)
            self.animation_group.start()

    def set_selected(self, selected):
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        # 停止所有正在运行的动画
        if hasattr(self, 'animation_group') and self.animation_group.state() == QParallelAnimationGroup.State.Running:
            self.animation_group.stop()
            
        self.is_selected = selected
        
        # 重置背景色属性，确保不会残留透明背景
        if selected:
            self._background_color = QColor(theme['card_background'])
        else:
            # 使用主题主色调，但完全透明
            primary_color = QColor(theme['primary_color'])
            self._background_color = QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 0)
        
        # 重新设置动画颜色，确保使用最新主题
        self._setup_animations()
            
        self.update_style()
        
        # 如果被选中，确保图标颜色也更新
        if self.is_selected:
            primary_color = theme['primary_color']
            if self.category_data.get('icon'):
                try:
                    self.icon_label.setPixmap(qta.icon(self.category_data['icon'], color=primary_color).pixmap(16, 16))
                except Exception:
                    # 如果图标名称无效，使用默认图标
                    self.icon_label.setPixmap(qta.icon('fa5s.folder', color=primary_color).pixmap(16, 16))
            else:
                self.icon_label.setPixmap(qta.icon('fa5s.folder', color=primary_color).pixmap(16, 16))
            # 更新展开/折叠按钮图标颜色
            if self.has_children and self.toggle_btn:
                if self.is_expanded:
                    self.toggle_btn.setIcon(qta.icon('fa5s.chevron-down', color=primary_color))
                else:
                    self.toggle_btn.setIcon(qta.icon('fa5s.chevron-right', color=primary_color))
        else:
            light_text_color = theme['light_text_color']
            if self.category_data.get('icon'):
                try:
                    self.icon_label.setPixmap(qta.icon(self.category_data['icon'], color=light_text_color).pixmap(16, 16))
                except Exception:
                    # 如果图标名称无效，使用默认图标
                    self.icon_label.setPixmap(qta.icon('fa5s.folder', color=light_text_color).pixmap(16, 16))
            else:
                self.icon_label.setPixmap(qta.icon('fa5s.folder', color=light_text_color).pixmap(16, 16))
            # 更新展开/折叠按钮图标颜色
            if self.has_children and self.toggle_btn:
                if self.is_expanded:
                    self.toggle_btn.setIcon(qta.icon('fa5s.chevron-down', color=light_text_color))
                else:
                    self.toggle_btn.setIcon(qta.icon('fa5s.chevron-right', color=light_text_color))

    def paintEvent(self, event):
        # 自定义绘制背景
        from PyQt6.QtGui import QPainter, QBrush
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据选中状态或悬停状态设置背景色
        if self.is_selected:
            brush = QBrush(QColor("white"))
        else:
            # 使用当前背景色属性
            brush = QBrush(self._background_color)
        
        # 绘制圆角矩形背景
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)  # 无边框
        painter.drawRoundedRect(self.rect().adjusted(8, 0, -8, 0), 8, 8)  # 应用margin并设置圆角

class CategoryList(QWidget):
    category_selected = pyqtSignal(str)  # 发送分类ID
    add_category_clicked = pyqtSignal()  # 添加分类信号
    edit_category_clicked = pyqtSignal(dict)  # 编辑分类信号，传递分类数据
    delete_category_clicked = pyqtSignal(str)  # 删除分类信号，传递分类ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_selected_item = None  # 跟踪当前选中的项
        self.setup_ui()
        self.setObjectName('category-list')  # 设置对象名，便于在主窗口中查找
        
    def setup_ui(self):
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        # 检查是否已有布局，如果有则先清除
        if self.layout():
            # 删除所有子部件
            for i in reversed(range(self.layout().count())):
                item = self.layout().itemAt(i)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif item.layout():
                    # 如果是子布局，也需要清除
                    sub_layout = item.layout()
                    for j in reversed(range(sub_layout.count())):
                        sub_widget = sub_layout.itemAt(j).widget()
                        if sub_widget:
                            sub_widget.deleteLater()
            
            # 清除旧布局
            old_layout = self.layout()
            QWidget().setLayout(old_layout)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建分类标题
        title_widget = QWidget()
        title_widget.setObjectName('category-title-widget')
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(16, 8, 16, 8)
        
        title_label = QLabel('分类导航')
        title_label.setObjectName('category-title-label')
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 添加分类按钮
        add_btn = QPushButton()
        add_btn.setIcon(qta.icon('fa5s.plus', color=theme['light_text_color']))
        add_btn.setObjectName('add-category-btn')
        add_btn.setFixedSize(24, 24)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_category_clicked)
        title_layout.addWidget(add_btn)
        
        layout.addWidget(title_widget)
        
        # 创建分类列表滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName('category-scroll-area')
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 创建分类列表容器
        self.category_container = QWidget()
        self.category_container.setObjectName('category-container')
        self.category_layout = QVBoxLayout(self.category_container)
        self.category_layout.setContentsMargins(0, 0, 0, 0)
        self.category_layout.setSpacing(0)
        self.category_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.category_container)
        layout.addWidget(scroll_area)
        
        # 设置样式 - 使用主题颜色
        self.setStyleSheet(f"""
            #category-title-widget {{
                background-color: {theme['secondary_color']};
            }}
            #category-title-label {{
                color: {theme['light_text_color']};
                font-size: 16px;
                font-weight: bold;
            }}
            #add-category-btn {{
                background-color: transparent;
                border: none;
            }}
            #add-category-btn:hover {{
                background-color: {theme['hover_color']};
                border-radius: 12px;
            }}
            #category-scroll-area {{
                background-color: transparent;
                border: none;
            }}
            #category-container {{
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {theme['scrollbar_background']};
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme['scrollbar_handle']};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['scrollbar_handle_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
    
    def load_categories(self, categories):
        # 保存分类数据，以便在右键菜单中使用
        self.categories = categories
        self.category_items = {}  # 使用字典保存所有分类项的引用，键为分类ID
        self.expanded_categories = set()  # 记录已展开的分类
        
        # 清空现有分类
        for i in reversed(range(self.category_layout.count())):
            widget = self.category_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 添加"全部分类"选项
        all_category_data = {
            '_id': 'all',  # 使用特殊ID表示全部分类
            'name': '全部网站',
            'icon': 'fa5s.globe',
            'description': '显示所有网站'
        }
        all_category_item = CategoryItem(all_category_data)
        # 确保点击"全部网站"时发送正确的信号
        all_category_item.clicked.connect(lambda category_id: self.on_category_item_clicked(all_category_item, ""))
        # 禁用右键菜单
        all_category_item.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.category_layout.addWidget(all_category_item)
        self.category_items['all'] = all_category_item
        
        # 构建分类树结构
        category_tree = {}
        for category in categories:
            category_id = str(category.get('_id'))
            parent_id = category.get('parent_id')
            
            if not parent_id:  # 顶级分类
                if category_id not in category_tree:
                    category_tree[category_id] = []
            else:  # 子分类
                parent_id = str(parent_id)
                if parent_id not in category_tree:
                    category_tree[parent_id] = []
                category_tree[parent_id].append(category)
            
            # 对每个父分类下的子分类按order字段排序
            for parent_id in category_tree:
                category_tree[parent_id] = sorted(category_tree[parent_id], key=lambda x: x.get('order', 0))
        
        # 添加顶级分类
        for category in categories:
            category_id = str(category.get('_id'))
            parent_id = category.get('parent_id')
            
            if not parent_id:  # 只添加顶级分类
                has_children = category_id in category_tree and len(category_tree[category_id]) > 0
                category_item = CategoryItem(category, has_children=has_children)
                category_item.clicked.connect(lambda cid, item=category_item: 
                                             self.on_category_item_clicked(item, cid))
                category_item.edit_category.connect(self.edit_category_clicked)
                category_item.delete_category.connect(self.delete_category_clicked)
                category_item.toggle_children.connect(self.toggle_children_visibility)
                self.category_layout.addWidget(category_item)
                self.category_items[category_id] = category_item
                
                # 如果该分类已展开，显示其子分类
                if category_id in self.expanded_categories:
                    self.show_child_categories(category_id, category_tree)
        
        # 默认选中"全部网站"
        if 'all' in self.category_items:
            self.on_category_item_clicked(self.category_items['all'], "")
    
    def toggle_children_visibility(self, category_id, is_expanded):
        """切换子分类显示状态"""
        if is_expanded:
            # 记录展开状态
            self.expanded_categories.add(category_id)
            # 构建分类树
            category_tree = {}
            for category in self.categories:
                cat_id = str(category.get('_id'))
                parent_id = category.get('parent_id')
                
                if not parent_id:  # 顶级分类
                    if cat_id not in category_tree:
                        category_tree[cat_id] = []
                else:  # 子分类
                    parent_id = str(parent_id)
                    if parent_id not in category_tree:
                        category_tree[parent_id] = []
                    category_tree[parent_id].append(category)
            
            # 显示子分类
            self.show_child_categories(category_id, category_tree)
        else:
            # 移除展开状态
            self.expanded_categories.discard(category_id)
            # 隐藏子分类
            self.hide_child_categories(category_id)
    
    def show_child_categories(self, parent_id, category_tree):
        """显示指定父分类下的所有子分类"""
        if parent_id not in category_tree:
            return
            
        # 获取父分类在布局中的索引
        parent_index = -1
        for i in range(self.category_layout.count()):
            widget = self.category_layout.itemAt(i).widget()
            if isinstance(widget, CategoryItem) and str(widget.category_data.get('_id')) == parent_id:
                parent_index = i
                break
                
        if parent_index == -1:
            return
            
        # 添加子分类
        for i, child_category in enumerate(category_tree[parent_id]):
            child_id = str(child_category.get('_id'))
            has_children = child_id in category_tree and len(category_tree[child_id]) > 0
            
            child_item = CategoryItem(child_category, is_child=True, has_children=has_children)
            child_item.clicked.connect(lambda cid, item=child_item: 
                                     self.on_category_item_clicked(item, cid))
            child_item.edit_category.connect(self.edit_category_clicked)
            child_item.delete_category.connect(self.delete_category_clicked)
            child_item.toggle_children.connect(self.toggle_children_visibility)
            
            # 在父分类后插入子分类
            self.category_layout.insertWidget(parent_index + i + 1, child_item)
            self.category_items[child_id] = child_item
            
            # 如果该子分类也已展开，递归显示其子分类
            if child_id in self.expanded_categories:
                child_item.is_expanded = True
                if child_item.toggle_btn:
                    child_item.toggle_btn.setIcon(qta.icon('fa5s.chevron-down', color='white' if not child_item.is_selected else UI_CONFIG['primary_color']))
                self.show_child_categories(child_id, category_tree)
    
    def hide_child_categories(self, parent_id):
        """隐藏指定父分类下的所有子分类"""
        # 找出所有子分类
        child_ids = []
        for category in self.categories:
            if str(category.get('parent_id')) == str(parent_id):
                child_id = str(category.get('_id'))
                child_ids.append(child_id)
                # 递归处理子分类的子分类
                self.expanded_categories.discard(child_id)  # 移除展开状态
                self.hide_child_categories(child_id)
        
        # 从布局中移除子分类
        for child_id in child_ids:
            if child_id in self.category_items:
                child_item = self.category_items[child_id]
                self.category_layout.removeWidget(child_item)
                child_item.deleteLater()
                del self.category_items[child_id]

    def on_category_item_clicked(self, clicked_item, category_id):
        # 清除所有分类的选中状态
        for item_id, item in self.category_items.items():
            if item != clicked_item:
                item.set_selected(False)
        
        # 设置当前点击项的选中状态
        clicked_item.set_selected(True)
        
        # 保存当前选中的项，以便在主题切换时更新
        self.current_selected_item = clicked_item
        
        # 发送分类选择信号
        self.category_selected.emit(category_id)

    def create_category_item(self, category, is_all_category=False):
        # 创建分类项容器
        item = QWidget()
        item.setObjectName('category-item')
        item.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 创建布局
        layout = QHBoxLayout(item)
        layout.setContentsMargins(16, 8, 16, 8)
        
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        # 创建图标 - 使用主题颜色
        icon_name = category.get('icon', 'fa5s.folder')
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon_name, color=theme['light_text_color']).pixmap(16, 16))
        layout.addWidget(icon_label)
        
        # 创建名称标签
        name_label = QLabel(category['name'])
        name_label.setObjectName('category-name')
        layout.addWidget(name_label)
        layout.addStretch()
        
        # 如果不是"全部分类"，添加编辑和删除按钮
        if not is_all_category:
            # 编辑按钮 - 使用主题颜色
            edit_btn = QPushButton()
            edit_btn.setIcon(qta.icon('fa5s.edit', color=theme['light_text_color']))
            edit_btn.setObjectName('category-edit-btn')
            edit_btn.setFixedSize(24, 24)
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda: self.edit_category_clicked.emit(category))
            layout.addWidget(edit_btn)
            
            # 删除按钮 - 使用主题颜色
            delete_btn = QPushButton()
            delete_btn.setIcon(qta.icon('fa5s.trash-alt', color=theme['light_text_color']))
            delete_btn.setObjectName('category-delete-btn')
            delete_btn.setFixedSize(24, 24)
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(lambda: self.delete_category_clicked.emit(str(category['_id'])))
            layout.addWidget(delete_btn)
        
        # 设置点击事件
        item.mousePressEvent = lambda event: self.on_category_clicked(event, category['_id'])
        
        # 设置样式 - 使用主题颜色
        item.setStyleSheet("""
            #category-item {{
                background-color: transparent;
                border-radius: 4px;
            }}
            #category-item:hover {{
                background-color: {theme['hover_color']};
            }}
            #category-name {{
                color: {theme['light_text_color']};
                font-size: 14px;
            }}
            #category-edit-btn, #category-delete-btn {{
                background-color: transparent;
                border: none;
                padding: 2px;
            }}
            #category-edit-btn:hover, #category-delete-btn:hover {{
                background-color: {theme['hover_color']};
                border-radius: 12px;
            }}
        """)
        
        return item
    
    def on_category_clicked(self, event, category_id):
        if event.button() == Qt.MouseButton.LeftButton:
            self.category_selected.emit(category_id)

    def contextMenuEvent(self, event):
        # 获取点击位置
        pos = event.pos()
        
        # 将点击位置转换为滚动区域内的坐标
        scroll_area = self.findChild(QScrollArea)
        if not scroll_area:
            return
            
        # 获取滚动区域内的容器
        container_pos = self.category_container.mapFrom(self, pos)
        
        # 遍历所有分类项，检查点击位置是否在某个分类项内
        for i in range(self.category_layout.count()):
            item_widget = self.category_layout.itemAt(i).widget()
            if item_widget and item_widget.geometry().contains(container_pos):
                # 找到了点击的分类项
                
                # 检查是否是"全部分类"项（第一个项目）
                if i == 0:
                    return  # 不为"全部分类"显示右键菜单
                
                # 获取分类数据
                category_data = None
                for j, category in enumerate(self.categories):
                    if j + 1 == i:  # +1 是因为第一个是"全部分类"
                        category_data = category
                        break
                
                if not category_data:
                    return
                
                # 创建右键菜单
                context_menu = QMenu(self)
                
                # 设置窗口标志和属性
                context_menu.setWindowFlag(Qt.WindowType.FramelessWindowHint)
                context_menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                # 在Windows下，自带的阴影效果仍然是直角，需要设置去除阴影效果
                context_menu.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint)
                
                # 获取当前主题
                theme = theme_manager.get_current_theme()
                
                # 添加菜单项 - 使用主题颜色
                edit_action = context_menu.addAction(qta.icon('fa5s.edit', color=theme['primary_color']), '编辑分类')
                delete_action = context_menu.addAction(qta.icon('fa5s.trash-alt', color='#ff4d4f'), '删除分类')
                
                # 显示菜单并获取选择的操作
                action = context_menu.exec(event.globalPos())
                
                # 处理选择的操作
                if action == edit_action:
                    self.edit_category_clicked.emit(category_data)
                elif action == delete_action:
                    self.delete_category_clicked.emit(str(category_data['_id']))
                
                return