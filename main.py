import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QMessageBox, \
    QPushButton, QDialog, QFormLayout, QLineEdit, QComboBox, QTextEdit, QDialogButtonBox, QGraphicsDropShadowEffect, QScrollArea, QMenu
from ui.dialogs.add_category_dialog import AddCategoryDialog
from ui.dialogs.add_website_dialog import AddWebsiteDialog
from PyQt6.QtCore import Qt, pyqtSlot, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices, QColor, QPixmap
import qtawesome as qta
import webbrowser
import json
from bson import ObjectId
from database.db_manager import DatabaseManager
from ui.components.category_list import CategoryList
from ui.components.website_card import WebsiteCard
from utils.icon_utils import IconManager
from config import UI_CONFIG
from ui.styles.main_styles import get_main_window_style
from ui.styles.theme_manager import theme_manager
from ui.styles.button_styles import get_subcategory_button_style, get_child_category_button_style

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AI网站导航系统')
        self.setMinimumSize(1200, 800)
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.db = DatabaseManager()
        self.current_category_id = None
        self.current_child_category_id = None
        self.max_cols = 3  # 默认每行显示3个卡片
        self.setup_ui()
        self.load_data()
        
    def resizeEvent(self, event):
        # 根据窗口宽度动态调整每行显示的卡片数量
        width = event.size().width()
        if width < 1200:
            self.max_cols = 3
        elif width < 1400:
            self.max_cols = 3
        elif width < 1600:
            self.max_cols = 4
        elif width < 2000:
            self.max_cols = 5
        else:
            self.max_cols = 6
            
        # 如果已经加载了网站，则重新加载以应用新的布局
        if hasattr(self, 'websites_container') and self.websites_container:
            self.load_websites(self.current_category_id)
            
        # 调用父类方法
        super().resizeEvent(event)

    def setup_ui(self):
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建左侧导航栏
        sidebar = QWidget()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(160)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # 添加Logo
        logo_widget = QWidget()
        logo_widget.setObjectName('logo-widget')
        logo_widget.setFixedHeight(60)
        logo_layout = QHBoxLayout(logo_widget)
        logo_icon = QLabel()
        logo_icon.setPixmap(qta.icon('fa5s.robot', color='white').pixmap(32, 32))
        logo_text = QLabel('AI网站导航')
        logo_text.setObjectName('logo-text')
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        sidebar_layout.addWidget(logo_widget)
        
        # 添加分类列表
        self.category_list = CategoryList()
        self.category_list.category_selected.connect(self.on_category_selected)
        self.category_list.add_category_clicked.connect(self.on_add_category_clicked)
        self.category_list.edit_category_clicked.connect(self.on_edit_category)
        self.category_list.delete_category_clicked.connect(self.on_delete_category)
        sidebar_layout.addWidget(self.category_list)

        # 添加到主布局
        main_layout.addWidget(sidebar)

        # 创建右侧内容区
        content = QWidget()
        content.setObjectName('content')
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加标题和搜索区域
        header_layout = QHBoxLayout()
        self.category_title = QLabel('全部网站')
        self.category_title.setObjectName('category-title')
        header_layout.addWidget(self.category_title)
        header_layout.addStretch()
        
        # 添加搜索框
        search_layout = QHBoxLayout()
        search_layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索网站...')
        self.search_input.setObjectName('search-input')
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        # 添加搜索图标
        search_icon = QLabel()
        search_icon.setPixmap(qta.icon('fa5s.search', color=theme_manager.get_current_theme()['search_icon_color']).pixmap(16, 16))
        search_icon.setObjectName('search-icon')
        
        # 添加清除按钮
        clear_btn = QPushButton()
        clear_btn.setIcon(qta.icon('fa5s.times', color=theme_manager.get_current_theme()['search_icon_color']))
        clear_btn.setObjectName('search-clear-btn')
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(lambda: self.search_input.clear())
        
        # 创建搜索框容器，使用相对布局而非CSS定位
        search_container = QWidget()
        search_container.setObjectName('search-container')
        search_container_layout = QHBoxLayout(search_container)
        search_container_layout.setContentsMargins(10, 0, 10, 0)
        search_container_layout.setSpacing(5)
        
        # 添加搜索图标到左侧
        search_container_layout.addWidget(search_icon)
        search_container_layout.addWidget(self.search_input)
        search_container_layout.addWidget(clear_btn)
        
        # 设置搜索图标和清除按钮的固定大小和对齐方式
        search_icon.setFixedSize(16, 16)
        clear_btn.setFixedSize(28, 28)
        
        # 添加搜索容器到header布局
        header_layout.addWidget(search_container)
        
        # 添加网站按钮
        add_website_btn = QPushButton()
        add_website_btn.setIcon(qta.icon('fa5s.plus', color=theme_manager.get_current_theme()['button_icon_color']))
        add_website_btn.setObjectName('add-website-btn')
        add_website_btn.clicked.connect(self.on_add_website_clicked)
        header_layout.addWidget(add_website_btn)
        
        # 添加导入按钮
        import_btn = QPushButton()
        import_btn.setIcon(qta.icon('fa5s.file-import', color=theme_manager.get_current_theme()['button_icon_color']))
        import_btn.setObjectName('import-btn')
        import_btn.setToolTip('导入网站数据')
        import_btn.clicked.connect(self.on_import_clicked)
        header_layout.addWidget(import_btn)
        
        # 添加导出按钮
        export_btn = QPushButton()
        export_btn.setIcon(qta.icon('fa5s.file-export', color=theme_manager.get_current_theme()['button_icon_color']))
        export_btn.setObjectName('export-btn')
        export_btn.setToolTip('导出网站数据')
        export_btn.clicked.connect(self.on_export_clicked)
        header_layout.addWidget(export_btn)
        
        # 添加主题切换按钮
        theme_btn = QPushButton()
        theme_btn.setIcon(qta.icon('fa5s.palette', color=theme_manager.get_current_theme()['button_icon_color']))
        theme_btn.setObjectName('theme-btn')
        theme_btn.setToolTip('切换主题')
        theme_btn.clicked.connect(self.on_theme_clicked)
        header_layout.addWidget(theme_btn)
        
        content_layout.addLayout(header_layout)
        
        # 添加子分类导航区域
        self.subcategory_nav = QWidget()
        self.subcategory_nav.setObjectName('subcategory-nav')
        self.subcategory_nav.setVisible(False)  # 默认隐藏
        self.subcategory_layout = QHBoxLayout(self.subcategory_nav)
        self.subcategory_layout.setContentsMargins(0, 10, 0, 10)
        self.subcategory_layout.setSpacing(10)
        self.subcategory_items = []  # 存储子分类按钮
        
        content_layout.addWidget(self.subcategory_nav)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName('websites-scroll-area')
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 添加网站卡片网格到滚动区域
        self.websites_container = QWidget()
        self.websites_container.setObjectName('websites-container')
        self.websites_container.setAutoFillBackground(False)
        self.websites_layout = QGridLayout(self.websites_container)
        self.websites_layout.setContentsMargins(0, 20, 0, 0)
        self.websites_layout.setSpacing(20)
        
        scroll_area.setWidget(self.websites_container)
        content_layout.addWidget(scroll_area)
        
        main_layout.addWidget(content)
        
        # 设置样式 - 使用从main_styles.py导入的样式函数
        self.setStyleSheet(get_main_window_style())

    def load_data(self):
        # 加载分类数据
        categories = self.db.get_all_categories()
        self.category_list.load_categories(categories)
        
        # 加载所有网站数据
        self.load_websites()
    
    def on_category_selected(self, category_id):
        self.current_category_id = category_id
        # 更新标题
        if category_id == 'all' or not category_id:
            self.category_title.setText('全部网站')
            # 隐藏子分类导航
            self.subcategory_nav.setVisible(False)
            self.clear_subcategory_nav()
        else:
            category = self.db.get_category(category_id)
            if category:
                self.category_title.setText(category['name'])
                
                # 检查是否有子分类
                child_categories = []
                for cat in self.db.get_all_categories():
                    if cat.get('parent_id') and str(cat.get('parent_id')) == str(category_id):
                        child_categories.append(cat)
                
                # 如果有子分类，显示子分类导航
                if child_categories:
                    self.show_subcategory_nav(child_categories, category_id)
                else:
                    # 如果没有子分类，隐藏子分类导航
                    self.subcategory_nav.setVisible(False)
                    self.clear_subcategory_nav()
            else:
                # 如果找不到分类信息，隐藏子分类导航
                self.subcategory_nav.setVisible(False)
                self.clear_subcategory_nav()
            
        # 加载该分类下的网站
        self.load_websites(category_id)
    
    def on_add_category_clicked(self):
        # 创建添加分类对话框
        dialog = AddCategoryDialog(self)
        if dialog.exec():
            # 获取表单数据
            category_data = dialog.get_category_data()
            # 添加到数据库
            self.db.add_category(category_data)
            # 重新加载分类列表
            self.category_list.load_categories(self.db.get_all_categories())
        
    def on_add_website_clicked(self):
        # 创建添加网站对话框
        dialog = AddWebsiteDialog(self.db.get_all_categories(), self)
        if dialog.exec():
            # 获取表单数据
            website_data = dialog.get_website_data()
            # 添加到数据库
            self.db.add_website(website_data)
            # 重新加载网站列表
            self.load_websites(self.current_category_id)
    
    def on_search_text_changed(self, text):
        # 搜索文本改变时触发
        # 重新加载网站，应用搜索过滤
        self.load_websites(self.current_category_id, search_text=text)
    
    def load_websites(self, category_id=None, search_text=None):
        # 清空现有网站卡片
        for i in reversed(range(self.websites_layout.count())):
            widget = self.websites_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 获取网站数据
        if category_id:
            # 使用递归方法获取分类及其子分类下的所有网站
            websites = self.db.get_websites_by_category_recursive(category_id)
        else:
            websites = self.db.get_all_websites()
        
        # 如果有搜索文本，过滤网站列表
        if search_text and search_text.strip():
            search_text = search_text.lower().strip()
            filtered_websites = []
            for website in websites:
                # 搜索网站名称、描述和标签
                if (search_text in website.get('name', '').lower() or
                    search_text in website.get('description', '').lower() or
                    any(search_text in tag.lower() for tag in website.get('tags', []))):
                    filtered_websites.append(website)
            websites = filtered_websites
        
        # 创建垂直布局容器替换原有的网格布局
        # 保存原有的网格布局引用
        old_layout = self.websites_layout
        
        # 创建新的垂直布局
        new_container = QWidget()
        new_container.setObjectName('websites-container')
        new_layout = QVBoxLayout(new_container)
        new_layout.setContentsMargins(0, 20, 0, 0)
        new_layout.setSpacing(20)
        
        # 如果没有网站，显示空提示
        if not websites:
            empty_label = QLabel('没有找到符合条件的网站')
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet('color: #999; font-size: 16px; margin: 50px 0;')
            new_layout.addWidget(empty_label)
            
            # 将新容器设置为滚动区域的内容
            scroll_area = self.findChild(QScrollArea, 'websites-scroll-area')
            if scroll_area:
                scroll_area.setWidget(new_container)
                self.websites_container = new_container
                self.websites_layout = new_layout
            return
        
        # 判断是否是全部网站模式
        is_all_websites = category_id == 'all' or category_id is None or category_id == ''
        
        if is_all_websites:
            # 全部网站模式：按顶级分类分组展示
            # 获取所有顶级分类
            top_categories = []
            for cat in self.db.get_all_categories():
                if not cat.get('parent_id'):
                    top_categories.append(cat)
            
            # 按顶级分类分组网站
            for top_cat in top_categories:
                top_cat_id = str(top_cat.get('_id'))
                
                # 获取该顶级分类下的所有网站（包括子分类下的网站）
                cat_websites = self.db.get_websites_by_category_recursive(top_cat_id)
                
                # 如果该分类下没有网站，跳过
                if not cat_websites:
                    continue
                
                # 创建分类标题区域
                category_section = QWidget()
                category_section.setObjectName(f'category-section-{top_cat_id}')
                section_layout = QVBoxLayout(category_section)
                section_layout.setContentsMargins(0, 0, 0, 20)
                section_layout.setSpacing(10)
                
                # 创建分类标题和子分类区域
                header_widget = QWidget()
                header_widget.setObjectName(f'header-widget-{top_cat_id}')
                header_layout = QHBoxLayout(header_widget)
                header_layout.setContentsMargins(0, 0, 0, 0)
                header_layout.setSpacing(10)
                
                # 添加分类标题
                title_label = QLabel(top_cat.get('name', '未分类'))
                title_label.setObjectName('category-section-title')
                # 获取当前主题
                theme = theme_manager.get_current_theme()
                title_label.setStyleSheet(f"""
                    font-size: 18px;
                    font-weight: bold;
                    color: {theme['text_color']};
                    padding-bottom: 5px;
                    border-bottom: 2px solid {theme['primary_color']};
                """)
                header_layout.addWidget(title_label)
                
                # 检查是否有子分类
                child_categories = []
                for cat in self.db.get_all_categories():
                    if cat.get('parent_id') and str(cat.get('parent_id')) == top_cat_id:
                        child_categories.append(cat)
                
                # 如果有子分类，添加子分类按钮
                if child_categories:
                    # 添加"全部"按钮
                    all_btn = QPushButton('全部')
                    all_btn.setObjectName(f"child-category-all-{top_cat_id}")
                    all_btn.setProperty("class", "child-category-btn")
                    all_btn.setProperty("category_id", "all")
                    all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    all_btn.clicked.connect(lambda checked, c=top_cat: self.load_websites_by_section(str(c['_id'])))
                    # 使用主题样式函数设置按钮样式
                    from ui.styles.button_styles import get_child_category_button_style
                    all_btn.setStyleSheet(get_child_category_button_style(selected=True))
                    header_layout.addWidget(all_btn)
                    
                    # 添加子分类按钮
                    for child_cat in child_categories:
                        child_btn = QPushButton(child_cat['name'])
                        child_btn.setObjectName(f"child-category-{child_cat['_id']}")
                        child_btn.setProperty("class", "child-category-btn")
                        child_btn.setProperty("category_id", str(child_cat['_id']))
                        child_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                        child_btn.clicked.connect(lambda checked, p=top_cat_id, c=child_cat: self.load_websites_by_section(p, str(c['_id'])))
                        # 使用主题样式函数设置按钮样式
                        from ui.styles.button_styles import get_child_category_button_style
                        child_btn.setStyleSheet(get_child_category_button_style(selected=False))
                        header_layout.addWidget(child_btn)
                
                # 添加弹性空间
                header_layout.addStretch()
                section_layout.addWidget(header_widget)
                
                # 创建网站卡片网格
                cards_widget = QWidget()
                cards_widget.setObjectName(f'cards-widget-{top_cat_id}')
                cards_layout = QGridLayout(cards_widget)
                cards_layout.setContentsMargins(0, 10, 0, 0)
                cards_layout.setSpacing(20)
                
                # 添加网站卡片
                row, col = 0, 0
                max_cols = self.max_cols  # 使用类变量控制每行显示的卡片数量
                
                for website in cat_websites:
                    card = WebsiteCard(website)
                    card.clicked.connect(self.on_website_clicked)
                    card.edit_clicked.connect(self.on_edit_website)
                    card.delete_clicked.connect(self.on_delete_website)
                    card.detail_clicked.connect(self.on_website_detail)
                
                    cards_layout.addWidget(card, row, col)
                    
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
                
                section_layout.addWidget(cards_widget)
                new_layout.addWidget(category_section)
        else:
            # 特定分类模式：只显示网站卡片，不显示分类标题
            # 创建网站卡片网格
            cards_widget = QWidget()
            cards_layout = QGridLayout(cards_widget)
            cards_layout.setContentsMargins(0, 10, 0, 0)
            cards_layout.setSpacing(20)
            
            # 添加网站卡片
            row, col = 0, 0
            max_cols = self.max_cols  # 使用类变量控制每行显示的卡片数量
            
            for website in websites:
                card = WebsiteCard(website)
                card.clicked.connect(self.on_website_clicked)
                card.edit_clicked.connect(self.on_edit_website)
                card.delete_clicked.connect(self.on_delete_website)
                card.detail_clicked.connect(self.on_website_detail)
                
                cards_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            new_layout.addWidget(cards_widget)
        
        # 将新容器设置为滚动区域的内容
        scroll_area = self.findChild(QScrollArea, 'websites-scroll-area')
        if scroll_area:
            scroll_area.setWidget(new_container)
            self.websites_container = new_container
            self.websites_layout = new_layout
    
    @pyqtSlot(str)
    def on_website_clicked(self, url):
        # 打开网站URL
        QDesktopServices.openUrl(QUrl(url))
    
    def on_edit_website(self, website_data):
        # 编辑网站信息
        dialog = AddWebsiteDialog(self.db.get_all_categories(), self)
        dialog.setWindowTitle('编辑网站')
        
        # 预填充表单数据
        dialog.set_website_data(website_data)
        
        if dialog.exec():
            # 获取更新后的表单数据，传递现有ID
            updated_data = dialog.get_website_data(website_data['_id'])
            # 更新数据库
            if self.db.update_website(website_data['_id'], updated_data):
                # 更新成功，显示成功消息
                QMessageBox.information(self, '成功', f'网站 "{website_data["name"]}" 已成功更新')
                # 重新加载网站列表
                self.load_websites(self.current_category_id)
            else:
                # 更新失败，显示错误消息
                QMessageBox.warning(self, '错误', f'更新网站 "{website_data["name"]}" 失败')
    
    def on_edit_category(self, category_data):
        # 创建编辑分类对话框
        dialog = AddCategoryDialog(self)
        
        # 设置可用的分类列表，用于加载父分类选项
        dialog.set_categories(self.db.get_all_categories())
        
        # 检查是否是添加子分类操作
        is_add_child = category_data.get('add_child', False)
        
        if is_add_child:
            # 添加子分类模式
            dialog.setWindowTitle('添加子分类')
            # 预设父分类为当前分类
            parent_id = str(category_data.get('_id'))
            # 查找父分类在下拉框中的索引并设置
            index = dialog.parent_combo.findData(parent_id)
            if index >= 0:
                dialog.parent_combo.setCurrentIndex(index)
            
            # 更新对话框标题
            title_label = dialog.findChild(QLabel, 'dialog-title')
            if title_label:
                title_label.setText('添加子分类')
        else:
            # 普通编辑分类模式
            dialog.setWindowTitle('编辑分类')
            # 预填充表单数据
            dialog.set_category_data(category_data)
        
        if dialog.exec():
            if is_add_child:
                # 添加子分类
                new_category_data = dialog.get_category_data()
                # 添加到数据库
                self.db.add_category(new_category_data)
                # 显示成功消息
                QMessageBox.information(self, '成功', f'子分类 "{new_category_data["name"]}" 已成功添加')
            else:
                # 编辑现有分类
                updated_data = dialog.get_category_data(category_data['_id'])
                # 更新数据库
                if self.db.update_category(category_data['_id'], updated_data):
                    # 更新成功，显示成功消息
                    QMessageBox.information(self, '成功', f'分类 "{category_data["name"]}" 已成功更新')
                else:
                    # 更新失败，显示错误消息
                    QMessageBox.warning(self, '错误', f'更新分类 "{category_data["name"]}" 失败')
            
            # 重新加载分类列表
            self.category_list.load_categories(self.db.get_all_categories())
    
    def on_delete_category(self, category_id):
        # 获取分类信息以显示更详细的确认信息
        category = self.db.get_category(category_id)
        if not category:
            QMessageBox.warning(self, '错误', '找不到要删除的分类信息')
            return
            
        # 使用自定义确认对话框
        from ui.components.confirm_dialog import ConfirmDialog
        
        message = f'确定要删除以下分类吗？\n\n名称: {category["name"]}'
        if category.get('description'):
            message += f'\n描述: {category["description"]}'
        message += '\n\n注意：删除分类将同时删除该分类下的所有网站！'
            
        dialog = ConfirmDialog('确认删除', message, self, icon_name='fa5s.trash-alt', icon_color='#ff4d4f')
        
        if dialog.exec():
            # 删除分类并检查结果
            if self.db.delete_category(category_id):
                # 删除成功，显示成功消息
                QMessageBox.information(self, '成功', f'分类 "{category["name"]}" 及其下的所有网站已成功删除')
                # 重新加载分类列表
                self.category_list.load_categories(self.db.get_all_categories())
                # 如果删除的是当前选中的分类，清空网站列表
                if str(category_id) == str(self.current_category_id):
                    self.current_category_id = None
                    self.category_title.setText('全部网站')
                    self.load_websites(None)
            else:
                # 删除失败，显示错误消息
                QMessageBox.warning(self, '错误', f'删除分类 "{category["name"]}" 失败')
    
    def on_delete_website(self, website_id):
        # 获取网站信息
        website = self.db.get_website(website_id)
        if not website:
            QMessageBox.warning(self, '错误', '找不到要删除的网站信息')
            return
            
        # 使用自定义确认对话框
        from ui.components.confirm_dialog import ConfirmDialog
        
        message = f'确定要删除以下网站吗？\n\n名称: {website["name"]}'
        if website.get('description'):
            message += f'\n描述: {website["description"]}'
        if website.get('url'):
            message += f'\nURL: {website["url"]}'
            
        dialog = ConfirmDialog('确认删除', message, self, icon_name='fa5s.trash-alt', icon_color='#ff4d4f')
        
        if dialog.exec():
            # 删除网站并检查结果
            if self.db.delete_website(website_id):
                # 删除成功，显示成功消息
                QMessageBox.information(self, '成功', f'网站 "{website["name"]}" 已成功删除')
                # 重新加载网站列表
                self.load_websites(self.current_category_id)
            else:
                # 删除失败，显示错误消息
                QMessageBox.warning(self, '错误', f'删除网站 "{website["name"]}" 失败')
    
    def on_import_clicked(self):
        # 创建导入对话框
        from ui.dialogs.import_dialog import ImportDialog
        dialog = ImportDialog(self)
        if dialog.exec():
            # 获取导入的数据
            imported_data = dialog.get_imported_data()
            if imported_data:
                # 导入数据到数据库
                categories_added = 0
                websites_added = 0
                
                # 导入分类
                for category in imported_data.get('categories', []):
                    if self.db.add_category(category):
                        categories_added += 1
                
                # 导入网站
                for website in imported_data.get('websites', []):
                    if self.db.add_website(website):
                        websites_added += 1
                
                # 显示导入结果
                QMessageBox.information(self, '导入成功', 
                                       f'成功导入 {categories_added} 个分类和 {websites_added} 个网站')
                
                # 重新加载数据
                self.category_list.load_categories(self.db.get_all_categories())
                self.load_websites(self.current_category_id)
            else:
                QMessageBox.warning(self, '导入失败', '导入数据格式不正确或为空')
    
    def on_export_clicked(self):
        # 创建导出对话框
        from ui.dialogs.export_dialog import ExportDialog
        dialog = ExportDialog(self.db, self)
        dialog.exec()
        
    def on_theme_clicked(self):
        # 创建主题菜单
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {theme_manager.get_current_theme()['menu_background']};
                border: 1px solid {theme_manager.get_current_theme()['menu_border']};
                border-radius: 8px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 15px;
                border-radius: 4px;
                margin: 2px 5px;
                color: {theme_manager.get_current_theme()['text_color']};
            }}
            QMenu::item:selected {{
                background-color: {theme_manager.get_current_theme()['hover_color']};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {theme_manager.get_current_theme()['menu_border']};
                margin: 5px 10px;
            }}
        """)
        
        # 获取当前主题
        current_theme = theme_manager.get_current_theme()
        
        # 添加默认主题选项
        default_action = menu.addAction('默认主题')
        default_action.setIcon(qta.icon('fa5s.sun', color='#005aea'))
        default_action.setCheckable(True)
        default_action.setChecked(current_theme['theme_name'] == '默认主题')
        default_action.triggered.connect(lambda: self.switch_theme('default'))
        
        # 添加暗夜主题选项
        dark_action = menu.addAction('暗夜主题')
        dark_action.setIcon(qta.icon('fa5s.moon', color='#000000'))
        dark_action.setCheckable(True)
        dark_action.setChecked(current_theme['theme_name'] == '暗夜主题')
        dark_action.triggered.connect(lambda: self.switch_theme('dark'))
        
        # 添加蓝色主题选项
        blue_action = menu.addAction('蓝色主题')
        blue_action.setIcon(qta.icon('fa5s.tint', color='#2196f3'))
        blue_action.setCheckable(True)
        blue_action.setChecked(current_theme['theme_name'] == '蓝色主题')
        blue_action.triggered.connect(lambda: self.switch_theme('blue'))
        
        # 添加绿色主题选项
        green_action = menu.addAction('绿色主题')
        green_action.setIcon(qta.icon('fa5s.leaf', color='#4caf50'))
        green_action.setCheckable(True)
        green_action.setChecked(current_theme['theme_name'] == '绿色主题')
        green_action.triggered.connect(lambda: self.switch_theme('green'))
        
        # 显示菜单
        sender = self.sender()
        menu.exec(sender.mapToGlobal(sender.rect().bottomLeft()))
    
    def switch_theme(self, theme_name):
        # 切换主题
        theme_manager.switch_theme(theme_name)
        
        # 更新应用样式
        self.setStyleSheet(get_main_window_style())
        
        # 更新按钮图标颜色
        self.update_button_icons()
        
        # 更新分类列表样式 - 只更新样式表而不重新创建布局
        category_list = self.findChild(QWidget, 'category-list')
        if category_list:
            # 获取当前主题
            theme = theme_manager.get_current_theme()
            # 只更新样式表，不重新创建布局
            category_list.setStyleSheet(f"""
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
            
            # 更新添加分类按钮图标
            add_btn = category_list.findChild(QPushButton, 'add-category-btn')
            if add_btn:
                add_btn.setIcon(qta.icon('fa5s.plus', color=theme['light_text_color']))
            
            # 刷新当前选中的分类项
            if hasattr(category_list, 'current_selected_item') and category_list.current_selected_item:
                category_list.current_selected_item.set_selected(True)
        
        # 更新所有子分类按钮样式
        from ui.styles.button_styles import get_child_category_button_style
        for btn in self.findChildren(QPushButton):
            if btn.property("class") == "child-category-btn":
                if btn.property("category_id") == "all" and self.current_child_category_id is None:
                    btn.setStyleSheet(get_child_category_button_style(selected=True))
                elif btn.property("category_id") == self.current_child_category_id:
                    btn.setStyleSheet(get_child_category_button_style(selected=True))
                else:
                    btn.setStyleSheet(get_child_category_button_style(selected=False))
        
        # 更新子分类导航区域中的按钮样式
        if self.subcategory_nav and self.subcategory_nav.isVisible():
            from ui.styles.button_styles import get_subcategory_button_style
            for btn in self.subcategory_items:
                if (btn.property("class") == "subcategory-item subcategory-item-selected") or \
                   (btn.objectName() == "subcategory-all" and self.current_child_category_id is None):
                    btn.setStyleSheet(get_subcategory_button_style(selected=True))
                else:
                    btn.setStyleSheet(get_subcategory_button_style(selected=False))
        
        # 重新加载网站卡片以应用新主题
        if self.current_category_id == 'all' or not self.current_category_id:
            # 如果是全部网站模式，重新加载所有网站
            self.load_websites()
        else:
            # 如果是特定分类模式，重新加载当前分类的网站
            self.load_websites(self.current_category_id)
    
    def update_button_icons(self):
        # 获取当前主题颜色
        theme = theme_manager.get_current_theme()
        primary_color = theme['primary_color']
        
        # 更新按钮图标
        add_website_btn = self.findChild(QPushButton, 'add-website-btn')
        if add_website_btn:
            add_website_btn.setIcon(qta.icon('fa5s.plus', color=theme['button_icon_color']))
            
        import_btn = self.findChild(QPushButton, 'import-btn')
        if import_btn:
            import_btn.setIcon(qta.icon('fa5s.file-import', color=theme['button_icon_color']))
            
        export_btn = self.findChild(QPushButton, 'export-btn')
        if export_btn:
            export_btn.setIcon(qta.icon('fa5s.file-export', color=theme['button_icon_color']))
            
        theme_btn = self.findChild(QPushButton, 'theme-btn')
        if theme_btn:
            theme_btn.setIcon(qta.icon('fa5s.palette', color=theme['button_icon_color']))
            
        # 更新搜索图标颜色
        search_icon = self.findChild(QLabel, 'search-icon')
        if search_icon:
            search_icon.setPixmap(qta.icon('fa5s.search', color=theme['search_icon_color']).pixmap(16, 16))
            
        # 更新清除按钮颜色
        clear_btn = self.findChild(QPushButton, 'search-clear-btn')
        if clear_btn:
            clear_btn.setIcon(qta.icon('fa5s.times', color=theme['search_icon_color']))
    
    def load_websites_by_section(self, parent_id, child_id=None):
        """加载分类区域中的子分类网站"""
        # 查找对应的分类区域
        category_section = self.findChild(QWidget, f'category-section-{parent_id}')
        if not category_section:
            return
            
        # 更新按钮样式
        header_widget = category_section.findChild(QWidget, f'header-widget-{parent_id}')
        if header_widget:
            # 找到所有子分类按钮
            child_btns = []
            for i in range(header_widget.layout().count()):
                widget = header_widget.layout().itemAt(i).widget()
                if isinstance(widget, QPushButton) and widget.property("class") == "child-category-btn":
                    child_btns.append(widget)
            
            # 更新按钮样式
            for btn in child_btns:
                if (child_id and btn.property("category_id") == child_id) or \
                   (not child_id and btn.property("category_id") == "all"):
                    # 选中状态
                    btn.setStyleSheet(get_child_category_button_style(selected=True))
                else:
                    # 未选中状态
                    btn.setStyleSheet(get_child_category_button_style(selected=False))
        
        # 保存当前分类ID和子分类ID
        self.current_category_id = parent_id
        self.current_child_category_id = child_id
        
        # 更新网站卡片
        cards_widget = category_section.findChild(QWidget, f'cards-widget-{parent_id}')
        if cards_widget:
            # 清空现有网站卡片
            cards_layout = cards_widget.layout()
            for i in reversed(range(cards_layout.count())):
                widget = cards_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # 获取网站数据
            if child_id:
                # 获取子分类下的网站
                websites = self.db.get_websites_by_category(child_id)
            else:
                # 获取父分类及其所有子分类下的网站
                websites = self.db.get_websites_by_category_recursive(parent_id)
            
            # 添加网站卡片
            row, col = 0, 0
            max_cols = self.max_cols  # 使用类变量控制每行显示的卡片数量
            
            for website in websites:
                card = WebsiteCard(website)
                card.clicked.connect(self.on_website_clicked)
                card.edit_clicked.connect(self.on_edit_website)
                card.delete_clicked.connect(self.on_delete_website)
                card.detail_clicked.connect(self.on_website_detail)
                
                cards_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
    def clear_subcategory_nav(self):
        """清空子分类导航区域"""
        # 清除所有子分类按钮
        for item in self.subcategory_items:
            self.subcategory_layout.removeWidget(item)
            item.deleteLater()
        self.subcategory_items = []
        
        # 清除布局中的所有项目，包括stretch空间
        while self.subcategory_layout.count():
            item = self.subcategory_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def show_subcategory_nav(self, child_categories, parent_id):
        """显示子分类导航"""
        self.clear_subcategory_nav()
        
        # 添加"全部"选项，显示父分类下所有网站
        all_btn = QPushButton("全部")
        all_btn.setObjectName(f"subcategory-all")
        all_btn.setProperty("class", "subcategory-item")
        all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        all_btn.clicked.connect(lambda: self.on_subcategory_clicked(all_btn, parent_id))
        self.subcategory_layout.addWidget(all_btn)
        self.subcategory_items.append(all_btn)
        
        # 默认选中"全部"
        all_btn.setProperty("class", "subcategory-item subcategory-item-selected")
        all_btn.setStyleSheet(get_subcategory_button_style(selected=True))
        
        # 添加子分类按钮
        for category in child_categories:
            btn = QPushButton(category['name'])
            btn.setObjectName(f"subcategory-{category['_id']}")
            btn.setProperty("class", "subcategory-item")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # 修复lambda函数中的闭包问题，将btn作为默认参数传入
            btn.clicked.connect(lambda checked, b=btn, c=category: self.on_subcategory_clicked(b, c['_id']))
            btn.setStyleSheet(get_subcategory_button_style(selected=False))
            self.subcategory_layout.addWidget(btn)
            self.subcategory_items.append(btn)
        
        # 添加弹性空间
        self.subcategory_layout.addStretch()
        
        # 显示子分类导航区
        self.subcategory_nav.setVisible(True)
    
    def on_subcategory_clicked(self, clicked_btn, category_id):
        """处理子分类点击事件"""
        # 更新按钮样式
        for btn in self.subcategory_items:
            if btn != clicked_btn:
                btn.setProperty("class", "subcategory-item")
                btn.setStyleSheet(get_subcategory_button_style(selected=False))
            else:
                btn.setProperty("class", "subcategory-item subcategory-item-selected")
                btn.setStyleSheet(get_subcategory_button_style(selected=True))
        
        # 加载该子分类下的网站
        self.load_websites(category_id)
        
    def on_website_detail(self, website_data):
        # 显示网站详情对话框
        from ui.dialogs.website_detail_dialog import WebsiteDetailDialog
        dialog = WebsiteDetailDialog(website_data, self)
        dialog.exec()

def main():
    app = QApplication(sys.argv)
    # 设置应用图标
    app.setWindowIcon(QIcon('app.ico'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()