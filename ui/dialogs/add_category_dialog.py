from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QTextEdit, QPushButton, QWidget, QFormLayout, QApplication,
                             QGraphicsDropShadowEffect, QComboBox)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QStandardItem, QStandardItemModel
from config import UI_CONFIG
from bson import ObjectId
import qtawesome as qta

from ..components.base_dialog import BaseDialog

class AddCategoryDialog(BaseDialog):
    def __init__(self, parent=None, categories=None, selected_category_id=None):
        super().__init__(parent)
        self.setWindowTitle('添加分类')
        self.setMinimumWidth(450)
        self.categories = categories or []
        self.editing_category_id = None
        self.selected_category_id = selected_category_id  # 当前选中的分类ID
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
        title_label = QLabel('添加分类')
        title_label.setObjectName('dialog-title')
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # 分类名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('请输入分类名称')
        self.name_input.setObjectName('input-field')
        form_layout.addRow('分类名称:', self.name_input)
        
        # 父分类选择
        self.parent_combo = QComboBox()
        self.parent_combo.setObjectName('input-field')
        self.parent_combo.addItem('无 (顶级分类)', None)
        # 加载父分类选项
        self._load_parent_categories()
        form_layout.addRow('父分类:', self.parent_combo)
        
        # 设置样式表，使禁用的选项显示为灰色
        self.parent_combo.setStyleSheet("""
            QComboBox::item:disabled {
                color: #888888;
                background-color: #f0f0f0;
            }
        """)
        
        # 分类图标
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText('请输入Font Awesome图标名称 (例如: fa5s.folder)')
        self.icon_input.setObjectName('input-field')
        form_layout.addRow('分类图标:', self.icon_input)
        
        # 添加FontAwesome链接
        icon_link_layout = QHBoxLayout()
        icon_link_layout.setContentsMargins(0, 0, 0, 0)  # 调整边距以对齐输入框
        icon_link_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 设置左对齐
        icon_link = QLabel('<a href="https://fontawesome.com/search" style="color: #1890ff;">点击查看Font Awesome图标</a>')
        icon_link.setOpenExternalLinks(True)
        icon_link_layout.addWidget(icon_link)
        
        form_layout.addRow('', icon_link_layout)  # 使用空字符串作为标签以对齐链接
        
        # 分类描述
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText('请输入分类描述')
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setObjectName('input-field')
        form_layout.addRow('分类描述:', self.desc_input)
        
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
        
        # 设置样式
        # 所有基础样式已移至BaseDialog中，这里不需要额外的样式定义
        pass
    
    def _load_parent_categories(self):
        """加载父分类选项"""
        if not self.categories:
            return
            
        # 清空现有选项，保留"无 (顶级分类)"
        while self.parent_combo.count() > 1:
            self.parent_combo.removeItem(1)
        
        # 创建自定义模型以支持禁用项
        model = QStandardItemModel()
        # 添加"无 (顶级分类)"选项
        first_item = QStandardItem('无 (顶级分类)')
        first_item.setData(None, Qt.ItemDataRole.UserRole)
        model.appendRow(first_item)
        
        # 获取当前编辑的分类ID和其所有子分类ID（如果有）
        disabled_ids = set()
        if hasattr(self, 'editing_category_id') and self.editing_category_id:
            disabled_ids.add(self.editing_category_id)
            # 添加所有子分类ID
            disabled_ids.update(self._get_all_child_ids(self.editing_category_id))
        
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
            
            # 如果不是当前选中的分类，禁用该选项
            if self.selected_category_id and parent_id != self.selected_category_id:
                parent_item.setEnabled(False)
                parent_item.setSelectable(False)
            
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
                    
                    # 禁用子分类选项
                    child_item.setEnabled(False)
                    child_item.setSelectable(False)
                    
                    model.appendRow(child_item)
        
        # 设置模型到下拉框
        self.parent_combo.setModel(model)
    
    def _get_all_child_ids(self, parent_id):
        """获取指定分类的所有子分类ID"""
        child_ids = set()
        for category in self.categories:
            if str(category.get('parent_id')) == parent_id:
                child_id = str(category.get('_id'))
                child_ids.add(child_id)
                # 递归获取子分类的子分类
                child_ids.update(self._get_all_child_ids(child_id))
        return child_ids
    
    def get_category_data(self, category_id=None):
        """获取表单数据"""
        # 如果没有提供ID，生成新的ID
        if category_id is None:
            category_id = str(ObjectId())
            
        # 获取选中的父分类ID
        parent_id = self.parent_combo.currentData()
        
        # 获取排序值，如果不是有效数字则默认为0
        try:
            order = int(self.order_input.text().strip())
        except ValueError:
            order = 0
            
        return {
            '_id': category_id,
            'name': self.name_input.text().strip(),
            'icon': self.icon_input.text().strip(),
            'description': self.desc_input.toPlainText().strip(),
            'parent_id': parent_id,  # 可能为None（顶级分类）或父分类ID
            'order': order  # 使用表单中的排序值
        }
    
    def set_category_data(self, category_data):
        """设置表单数据，用于编辑现有分类"""
        if category_data:
            # 保存当前编辑的分类ID
            self.editing_category_id = str(category_data.get('_id'))
            
            self.name_input.setText(category_data.get('name', ''))
            self.icon_input.setText(category_data.get('icon', ''))
            self.desc_input.setText(category_data.get('description', ''))
            
            # 设置排序值
            order = category_data.get('order', 0)
            self.order_input.setText(str(order))
            
            # 重新加载父分类选项，以便禁用当前分类及其子分类
            self._load_parent_categories()
            
            # 设置父分类
            parent_id = category_data.get('parent_id')
            if parent_id:
                # 查找父分类在下拉框中的索引
                index = self.parent_combo.findData(str(parent_id), Qt.ItemDataRole.UserRole)
                if index >= 0:
                    self.parent_combo.setCurrentIndex(index)
            else:
                # 设置为顶级分类
                self.parent_combo.setCurrentIndex(0)
            
            # 更新对话框标题
            title_label = self.findChild(QLabel, 'dialog-title')
            if title_label:
                title_label.setText('编辑分类')
                
            # 更新窗口标题
            self.setWindowTitle('编辑分类')
    
    def set_categories(self, categories):
        """设置可用的分类列表，用于加载父分类选项"""
        self.categories = categories
        self._load_parent_categories()