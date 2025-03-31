import os
import json
import pandas as pd
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFileDialog, QWidget, QGraphicsDropShadowEffect,
                            QRadioButton, QButtonGroup, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import qtawesome as qta
from config import UI_CONFIG
from ui.styles.theme_manager import theme_manager
from ..components.base_dialog import BaseDialog

class ExportDialog(BaseDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle('导出数据')
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        self.setup_ui()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None    
    # 重写显示方法，显示遮罩
    def showEvent(self, event):
        # 临时禁用阴影效果，避免 UpdateLayeredWindowIndirect 错误
        had_effect = self.graphicsEffect() is not None
        self.setGraphicsEffect(None)
        
        if self.parent():
            # 获取父窗口的全局位置和大小
            parent_rect = self.parent().geometry()
            # 设置遮罩层的位置和大小
            self.mask.setGeometry(0, 0, parent_rect.width(), parent_rect.height())
            self.mask.show()
            # 将对话框居中显示在父窗口
            parent_center = parent_rect.center()
            self.move(parent_center.x() - self.width() // 2, parent_center.y() - self.height() // 2)
        
        # 调用父类方法
        super().showEvent(event)
        
        # 如果之前有效果，创建一个新的效果
        if had_effect:
            QApplication.instance().processEvents()
            # 创建新的阴影效果而不是尝试重用旧的
            self._setup_shadow()

    def resizeEvent(self, event):
        # 当父窗口大小改变时，更新遮罩层大小
        if self.parent() and self.mask.isVisible():
            parent_rect = self.parent().geometry()
            self.mask.setGeometry(0, 0, parent_rect.width(), parent_rect.height())
        super().resizeEvent(event)
    
    # 重写关闭方法，隐藏遮罩
    def closeEvent(self, event):
        self.mask.hide()
        super().closeEvent(event)
    
    # 重写拒绝和接受方法，确保遮罩被隐藏
    def reject(self):
        self.mask.hide()
        super().reject()
    
    def accept(self):
        self.mask.hide()
        super().accept()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建主容器
        main_container = QWidget(self)
        main_container.setObjectName('dialog-container')
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # 创建标题
        title_layout = QHBoxLayout()
        title_label = QLabel('导出数据')
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
        
        # 导出格式选择
        format_label = QLabel('选择导出格式:')
        main_layout.addWidget(format_label)
        
        # 创建单选按钮组
        self.format_group = QButtonGroup(self)
        
        # 获取当前主题颜色
        theme = theme_manager.get_current_theme()
        text_color = theme['text_color']
        
        # Excel格式
        excel_radio = QRadioButton('Excel格式 (.xlsx)')
        excel_radio.setObjectName('format-radio')
        excel_radio.setChecked(True)  # 默认选中
        excel_radio.setStyleSheet(f"color: {text_color};")
        self.format_group.addButton(excel_radio, 1)
        main_layout.addWidget(excel_radio)
        
        # CSV格式
        csv_radio = QRadioButton('CSV格式 (.csv)')
        csv_radio.setObjectName('format-radio')
        csv_radio.setStyleSheet(f"color: {text_color};")
        self.format_group.addButton(csv_radio, 2)
        main_layout.addWidget(csv_radio)
        
        # JSON格式
        json_radio = QRadioButton('JSON格式 (.json)')
        json_radio.setObjectName('format-radio')
        json_radio.setStyleSheet(f"color: {text_color};")
        self.format_group.addButton(json_radio, 3)
        main_layout.addWidget(json_radio)
        
        main_layout.addStretch()
        
        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setObjectName('cancel-btn')
        cancel_btn.clicked.connect(self.reject)
        
        export_btn = QPushButton('导出')
        export_btn.setObjectName('ok-btn')
        export_btn.clicked.connect(self.export_data)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(export_btn)
        main_layout.addLayout(button_layout)
        
        layout.addWidget(main_container)
        
        # 设置基础样式
        theme = theme_manager.get_current_theme()
        self.setStyleSheet(self._get_base_style() + f"""
            QDialog QRadioButton#format-radio {{
                color: {theme['text_color']} !important;
                font-size: 14px;
                padding: 8px;
                background-color: transparent !important;
            }}
        """)

    
    def export_data(self):
        """导出数据"""
        try:
            # 获取所有分类和网站数据
            categories = self.db.get_all_categories()
            websites = self.db.get_all_websites()
            
            # 确定导出格式
            format_id = self.format_group.checkedId()
            
            if format_id == 1:  # Excel
                self.export_to_excel(categories, websites)
            elif format_id == 2:  # CSV
                self.export_to_csv(categories, websites)
            elif format_id == 3:  # JSON
                self.export_to_json(categories, websites)
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('导出失败')
            msg_box.setText(f'导出数据时发生错误: {str(e)}')
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
    
    def export_to_excel(self, categories, websites):
        """导出数据到Excel文件"""
        try:
            # 选择保存路径
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilter("Excel文件 (*.xlsx)")
            file_dialog.setDefaultSuffix("xlsx")
            file_dialog.selectFile("导航网站数据.xlsx")
            
            if file_dialog.exec():
                save_path = file_dialog.selectedFiles()[0]
                
                try:
                    # 创建分类ID到名称的映射
                    category_map = {str(cat['_id']): cat['name'] for cat in categories}
                    
                    # 转换数据为DataFrame
                    categories_df = pd.DataFrame(categories)
                    
                    # 为网站数据添加分类名称
                    websites_copy = []
                    for website in websites:
                        website_copy = website.copy()
                        if 'category_id' in website_copy and website_copy['category_id']:
                            cat_id = str(website_copy['category_id'])
                            if cat_id in category_map:
                                website_copy['category_name'] = category_map[cat_id]
                        websites_copy.append(website_copy)
                    
                    websites_df = pd.DataFrame(websites_copy)
                    
                    # 处理标签字段，将列表转换为字符串
                    if 'tags' in websites_df.columns:
                        websites_df['tags'] = websites_df['tags'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
                    
                    # 保存到Excel文件
                    with pd.ExcelWriter(save_path) as writer:
                        categories_df.to_excel(writer, sheet_name='categories', index=False)
                        websites_df.to_excel(writer, sheet_name='websites', index=False)
                    
                    from PyQt6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle('导出成功')
                    msg_box.setText(f'数据已成功导出到: {save_path}')
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    msg_box.exec()
                    self.accept()
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    from PyQt6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle('导出失败')
                    msg_box.setText(f'导出Excel文件时发生错误: {str(e)}')
                    msg_box.setDetailedText(error_details)
                    msg_box.setIcon(QMessageBox.Icon.Warning)
                    msg_box.exec()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('导出失败')
            msg_box.setText(f'创建导出对话框时发生错误: {str(e)}')
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
    
    def export_to_csv(self, categories, websites):
        """导出数据到CSV文件"""
        try:
            # 选择保存路径
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilter("CSV文件 (*.csv)")
            file_dialog.setDefaultSuffix("csv")
            file_dialog.selectFile("导航网站数据.csv")
            
            if file_dialog.exec():
                save_path = file_dialog.selectedFiles()[0]
                
                try:
                    # 添加类型字段以区分记录
                    categories_copy = [category.copy() for category in categories]
                    websites_copy = [website.copy() for website in websites]
                    
                    for category in categories_copy:
                        category['type'] = 'category'
                    
                    for website in websites_copy:
                        website['type'] = 'website'
                        # 处理标签字段，将列表转换为字符串
                        if 'tags' in website and isinstance(website['tags'], list):
                            website['tags'] = ', '.join(website['tags'])
                    
                    # 合并记录并保存
                    all_records = categories_copy + websites_copy
                    pd.DataFrame(all_records).to_csv(save_path, index=False)
                    
                    from PyQt6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle('导出成功')
                    msg_box.setText(f'数据已成功导出到: {save_path}')
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    msg_box.exec()
                    self.accept()
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    from PyQt6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle('导出失败')
                    msg_box.setText(f'导出CSV文件时发生错误: {str(e)}')
                    msg_box.setDetailedText(error_details)
                    msg_box.setIcon(QMessageBox.Icon.Warning)
                    msg_box.exec()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('导出失败')
            msg_box.setText(f'创建导出对话框时发生错误: {str(e)}')
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
    
    def export_to_json(self, categories, websites):
        """导出数据到JSON文件"""
        try:
            # 选择保存路径
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilter("JSON文件 (*.json)")
            file_dialog.setDefaultSuffix("json")
            file_dialog.selectFile("导航网站数据.json")
            
            if file_dialog.exec():
                save_path = file_dialog.selectedFiles()[0]
                
                try:
                    # 创建导出数据结构
                    # 深拷贝数据，避免修改原始数据
                    categories_copy = []
                    for category in categories:
                        category_copy = category.copy()
                        # 确保ObjectId被转换为字符串
                        if '_id' in category_copy:
                            category_copy['_id'] = str(category_copy['_id'])
                        if 'parent_id' in category_copy and category_copy['parent_id']:
                            category_copy['parent_id'] = str(category_copy['parent_id'])
                        categories_copy.append(category_copy)
                    
                    websites_copy = []
                    for website in websites:
                        website_copy = website.copy()
                        # 确保ObjectId被转换为字符串
                        if '_id' in website_copy:
                            website_copy['_id'] = str(website_copy['_id'])
                        if 'category_id' in website_copy and website_copy['category_id']:
                            website_copy['category_id'] = str(website_copy['category_id'])
                        websites_copy.append(website_copy)
                    
                    export_data = {
                        'categories': categories_copy,
                        'websites': websites_copy
                    }
                    
                    # 保存到JSON文件
                    with open(save_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                    
                    from PyQt6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle('导出成功')
                    msg_box.setText(f'数据已成功导出到: {save_path}')
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    msg_box.exec()
                    self.accept()
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    from PyQt6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle('导出失败')
                    msg_box.setText(f'导出JSON文件时发生错误: {str(e)}')
                    msg_box.setDetailedText(error_details)
                    msg_box.setIcon(QMessageBox.Icon.Warning)
                    msg_box.exec()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('导出失败')
            msg_box.setText(f'创建导出对话框时发生错误: {str(e)}')
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()