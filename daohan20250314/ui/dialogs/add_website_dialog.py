from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QTextEdit, QPushButton, QWidget, QFormLayout, QComboBox,
                             QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap, QStandardItem, QStandardItemModel
from config import UI_CONFIG
from bson import ObjectId
import qtawesome as qta
import os
from PyQt6.QtCore import QSize

from ..components.base_dialog import BaseDialog
from utils.icon_utils import IconManager

class AddWebsiteDialog(BaseDialog):
    def __init__(self, categories=None, parent=None, website_id=None):
        super().__init__(parent)
        self.setWindowTitle('添加网站')
        self.setMinimumWidth(500)
        self.categories = categories or []
        self.website_id = website_id or str(ObjectId())
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
        title_label = QLabel('添加网站')
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
        
        # 添加隐藏的网站ID标签
        self.website_id_hidden = QLabel(self.website_id)
        self.website_id_hidden.setObjectName('website-id-hidden')
        self.website_id_hidden.setVisible(False)
        main_layout.addWidget(self.website_id_hidden)

        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # 网站名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('请输入网站名称')
        self.name_input.setObjectName('input-field')
        form_layout.addRow('网站名称:', self.name_input)
        
        # 网站URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('请输入网站URL (例如: https://www.example.com)')
        self.url_input.setObjectName('input-field')
        form_layout.addRow('网站URL:', self.url_input)
        
        # 网站图标
        icon_layout = QVBoxLayout()
        icon_input_layout = QHBoxLayout()
        
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText('请输入Font Awesome图标名称 (例如: fa5s.globe)')
        self.icon_input.setObjectName('input-field')
        self.icon_input.textChanged.connect(self.update_icon_preview)
        icon_input_layout.addWidget(self.icon_input)
        
        # 添加上传按钮
        upload_btn = QPushButton('上传图标')
        upload_btn.setObjectName('ok-btn')
        upload_btn.clicked.connect(self.upload_icon)
        icon_input_layout.addWidget(upload_btn)
        
        icon_layout.addLayout(icon_input_layout)
        
        # 添加图标预览区域
        preview_layout = QHBoxLayout()
        preview_layout.setContentsMargins(0, 8, 0, 0)
        
        preview_label = QLabel('预览:')
        preview_layout.addWidget(preview_label)
        
        self.icon_preview = QLabel()
        self.icon_preview.setFixedSize(32, 32)
        self.icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_preview.setStyleSheet('border: 1px solid #d9d9d9; border-radius: 4px; background-color: #f5f5f5;')
        preview_layout.addWidget(self.icon_preview)
        preview_layout.addStretch()
        
        icon_layout.addLayout(preview_layout)
        
        # 添加FontAwesome链接
        icon_link_layout = QHBoxLayout()
        icon_link_layout.setContentsMargins(0, 4, 0, 0)
        icon_link = QLabel('<a href="https://fontawesome.com/search" style="color: #1890ff;">点击查看Font Awesome图标</a>')
        icon_link.setOpenExternalLinks(True)
        icon_link_layout.addWidget(icon_link)
        icon_link_layout.addStretch()
        
        icon_layout.addLayout(icon_link_layout)
        form_layout.addRow('网站图标:', icon_layout)
        
        # 分类选择
        self.category_combo = QComboBox()
        self.category_combo.setObjectName('input-field')
        self._load_categories()
        form_layout.addRow('所属分类:', self.category_combo)
        
        # 网站描述
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText('请输入网站描述')
        self.desc_input.setMaximumHeight(160)
        self.desc_input.setObjectName('input-field')
        form_layout.addRow('网站描述:', self.desc_input)

        # 标签
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText('请输入标签，多个标签用逗号分隔')
        self.tags_input.setObjectName('input-field')
        form_layout.addRow('标签:', self.tags_input)

        # 排序值
        self.order_input = QLineEdit()
        self.order_input.setPlaceholderText('请输入排序值（数字越小排序越靠前）')
        self.order_input.setObjectName('input-field')
        self.order_input.setText('0')
        form_layout.addRow('排序值:', self.order_input)

        main_layout.addLayout(form_layout)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setObjectName('cancel-btn')
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton('确定')
        ok_btn.setObjectName('ok-btn')
        ok_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        main_layout.addLayout(button_layout)
        
        layout.addWidget(main_container)
    
    def _load_categories(self):
        """加载分类选项"""
        if not self.categories:
            return
            
        # 清空现有选项
        self.category_combo.clear()
        
        # 创建自定义模型以支持禁用项
        model = QStandardItemModel()
        
        # 获取当前网站的分类ID（如果是编辑模式）
        current_category_id = getattr(self, 'current_category_id', None)
        
        # 添加"无分类"
        first_item = QStandardItem('无分类')
        first_item.setData(None, Qt.ItemDataRole.UserRole)
        model.appendRow(first_item)
        
        # 创建分类ID到分类对象的映射，用于查找父分类
        category_map = {}
        for category in self.categories:
            category_id = str(category.get('_id'))
            category_map[category_id] = category
        
        # 创建父分类到子分类的映射
        parent_to_children = {}
        top_level_categories = []
        
        # 识别顶级分类和子分类
        for category in self.categories:
            if category.get('parent_id'):
                parent_id = str(category.get('parent_id'))
                if parent_id not in parent_to_children:
                    parent_to_children[parent_id] = []
                parent_to_children[parent_id].append(category)
            else:
                # 没有父分类的是顶级分类
                top_level_categories.append(category)
        
        # 先添加顶级分类，然后立即添加其子分类
        for parent_category in top_level_categories:
            parent_id = str(parent_category.get('_id'))
            parent_name = parent_category.get('name', '')
            
            # 创建顶级分类项目并设置数据
            parent_item = QStandardItem(parent_name)
            parent_item.setData(parent_id, Qt.ItemDataRole.UserRole)
            
            # 如果是当前网站的分类，设置为灰色
            if parent_id == current_category_id:
                parent_item.setForeground(QColor('#888888'))
                parent_item.setBackground(QColor('#f0f0f0'))
            
            model.appendRow(parent_item)
            
            # 添加该顶级分类的所有子分类
            if parent_id in parent_to_children:
                for child_category in parent_to_children[parent_id]:
                    child_id = str(child_category.get('_id'))
                    child_name = child_category.get('name', '')
                    # 添加缩进表示层级关系
                    indented_name = f"    {child_name}"
                    
                    # 创建子分类项目并设置数据
                    child_item = QStandardItem(indented_name)
                    child_item.setData(child_id, Qt.ItemDataRole.UserRole)
                    
                    # 如果是当前网站的分类，设置为灰色
                    if child_id == current_category_id:
                        child_item.setForeground(QColor('#888888'))
                        child_item.setBackground(QColor('#f0f0f0'))
                    
                    model.appendRow(child_item)
        
        # 设置模型到下拉框
        self.category_combo.setModel(model)
    
    def get_website_data(self, website_id=None):
        """获取表单数据"""
        # 如果没有提供ID，生成新的ID
        if website_id is None:
            website_id = str(ObjectId())
            
        # 获取选中的分类ID
        category_id = self.category_combo.currentData()
        
        # 获取排序值，如果输入不是数字则默认为0
        try:
            order = int(self.order_input.text().strip())
        except ValueError:
            order = 0
            
        # 处理标签，将输入的标签字符串分割为列表
        tags_text = self.tags_input.text().strip()
        tags = [tag.strip() for tag in tags_text.split(',')] if tags_text else []
        # 移除空标签
        tags = [tag for tag in tags if tag]
            
        return {
            '_id': website_id,
            'name': self.name_input.text().strip(),
            'url': self.url_input.text().strip(),
            'icon': self.icon_input.text().strip(),
            'description': self.desc_input.toPlainText().strip(),
            'category_id': category_id,
            'order': order,  # 使用表单中的排序值
            'tags': tags  # 添加标签字段
        }
    
    def upload_icon(self):
        """处理图标上传功能"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图标文件",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.svg)"
        )
        
        if file_path:
            # 获取当前网站ID，如果是新建网站则生成一个临时ID
            website_id = self.findChild(QLabel, 'website-id-hidden').text() if hasattr(self, 'website_id_hidden') else str(ObjectId())
            
            # 使用IconManager保存图标文件
            icon_manager = IconManager()
            saved_path = icon_manager.save_icon(file_path, website_id)
            
            if saved_path:
                # 将保存后的绝对路径设置到图标输入框
                self.icon_input.setText(saved_path)
                self.update_icon_preview()
            else:
                # 如果保存失败，显示错误信息
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "上传失败", "图标文件保存失败，请重试。")
    
    def update_icon_preview(self, text=None):
        """更新图标预览"""
        icon_text = self.icon_input.text().strip()
        
        if not icon_text:
            # 如果没有图标，显示默认图标
            self.icon_preview.setPixmap(qta.icon('fa5s.globe').pixmap(32, 32))
            return
        
        if icon_text.startswith('fa'):
            # 如果是Font Awesome图标
            try:
                self.icon_preview.setPixmap(qta.icon(icon_text).pixmap(32, 32))
            except Exception:
                # 如果图标名称无效，显示默认图标
                self.icon_preview.setPixmap(qta.icon('fa5s.globe').pixmap(32, 32))
        elif os.path.isabs(icon_text) and os.path.exists(icon_text):
            # 如果是绝对路径且文件存在
            pixmap = QPixmap(icon_text)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(QSize(32, 32), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.icon_preview.setPixmap(pixmap)
            else:
                # 如果图片加载失败，显示默认图标
                self.icon_preview.setPixmap(qta.icon('fa5s.globe').pixmap(32, 32))
        elif icon_text.startswith('ui/resources/icons/'):
            # 尝试在项目根目录中查找
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            abs_path = os.path.join(project_root, icon_text)
            
            # 如果在项目根目录中找不到，尝试在用户数据目录中查找
            if not os.path.exists(abs_path):
                user_data_dir = os.path.join(os.path.expanduser('~'), '.daohan_navigator')
                abs_path = os.path.join(user_data_dir, icon_text)
            
            if os.path.exists(abs_path):
                pixmap = QPixmap(abs_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(QSize(32, 32), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.icon_preview.setPixmap(pixmap)
                else:
                    # 如果图片加载失败，显示默认图标
                    self.icon_preview.setPixmap(qta.icon('fa5s.globe').pixmap(32, 32))
            else:
                # 如果图标文件不存在，显示默认图标
                self.icon_preview.setPixmap(qta.icon('fa5s.globe').pixmap(32, 32))
        else:
            # 如果是其他格式的路径，显示默认图标
            self.icon_preview.setPixmap(qta.icon('fa5s.globe').pixmap(32, 32))

    def set_website_data(self, website_data):
        """设置表单数据，用于编辑现有网站"""
        if website_data:
            self.name_input.setText(website_data.get('name', ''))
            self.url_input.setText(website_data.get('url', ''))
            self.icon_input.setText(website_data.get('icon', ''))
            self.desc_input.setText(website_data.get('description', ''))
            
            # 更新图标预览
            self.update_icon_preview()
            
            # 设置排序值
            self.order_input.setText(str(website_data.get('order', 0)))
            
            # 设置标签
            tags = website_data.get('tags', [])
            if tags:
                self.tags_input.setText(', '.join(tags))
            
            # 保存当前网站的分类ID，用于在_load_categories中标记当前分类为灰色
            category_id = website_data.get('category_id')
            self.current_category_id = str(category_id) if category_id else None
            
            # 重新加载分类列表，以便应用灰色效果
            self._load_categories()
            
            # 设置分类
            if category_id:
                # 查找分类在下拉框中的索引
                index = self.category_combo.findData(str(category_id))
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
            else:
                # 设置为无分类
                self.category_combo.setCurrentIndex(0)
            
            # 更新对话框标题
            title_label = self.findChild(QLabel, 'dialog-title')
            if title_label:
                title_label.setText('编辑网站')
                
            # 更新窗口标题
            self.setWindowTitle('编辑网站')
    
    def set_categories(self, categories):
        """设置可用的分类列表，用于加载分类选项"""
        self.categories = categories
        self._load_categories()