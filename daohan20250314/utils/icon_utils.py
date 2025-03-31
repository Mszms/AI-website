import os
import shutil
import uuid
import sys
from PIL import Image
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QDir

class IconManager:
    def __init__(self):
        # 判断是否是打包环境
        if getattr(sys, 'frozen', False):
            # 如果是打包环境，使用用户数据目录
            self.root_dir = os.path.join(os.path.expanduser('~'), '.daohan_navigator')
            # 确保用户数据目录存在
            os.makedirs(self.root_dir, exist_ok=True)
        else:
            # 如果是开发环境，使用项目根目录
            self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 设置图标存储目录
        self.custom_icons_dir = os.path.join(self.root_dir, 'ui', 'resources', 'icons', 'custom')
        self.default_icons_dir = os.path.join(self.root_dir, 'ui', 'resources', 'icons', 'default')
        
        # 确保目录存在
        os.makedirs(self.custom_icons_dir, exist_ok=True)
        os.makedirs(self.default_icons_dir, exist_ok=True)
    
    def select_icon_file(self, parent=None):
        """打开文件选择对话框，让用户选择图标文件"""
        file_dialog = QFileDialog(parent)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("图片文件 (*.png *.jpg *.jpeg *.ico *.svg)")
        file_dialog.setViewMode(QFileDialog.ViewMode.List)
        file_dialog.setDirectory(QDir.homePath())
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                return selected_files[0]
        return None
    
    def save_icon(self, source_path, website_id):
        """保存图标文件到自定义图标目录
        
        Args:
            source_path: 源图标文件路径
            website_id: 网站ID，用于命名图标文件
            
        Returns:
            str: 保存后的图标文件相对路径（相对于项目根目录）
        """
        if not source_path or not os.path.exists(source_path):
            return None
            
        # 获取文件扩展名
        _, ext = os.path.splitext(source_path)
        if not ext:
            ext = '.png'  # 默认扩展名
        
        # 生成目标文件名
        target_filename = f"{website_id}{ext}"
        target_path = os.path.join(self.custom_icons_dir, target_filename)
        
        try:
            # 复制文件到目标位置
            shutil.copy2(source_path, target_path)
            
            # 返回绝对路径（确保在任何环境下都能找到图标）
            return target_path
        except Exception as e:
            print(f"保存图标文件失败: {e}")
            return None
    
    def get_icon_path(self, icon_value):
        """获取图标路径
        
        Args:
            icon_value: 图标值，可能是Font Awesome图标名、URL或本地路径
            
        Returns:
            str: 图标路径或原始值（如果是Font Awesome图标或URL）
        """
        # 如果是本地路径
        if icon_value and isinstance(icon_value, str):
            # 检查是否是Font Awesome图标
            if icon_value.startswith('fa'):
                return icon_value
            # 检查是否是URL
            if icon_value.startswith(('http://', 'https://', 'data:')):
                return icon_value
            # 检查是否是绝对路径
            if os.path.isabs(icon_value) and os.path.exists(icon_value):
                return icon_value
            # 检查是否是相对路径
            if icon_value.startswith('ui/resources/icons/'):
                # 尝试在项目根目录中查找
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                abs_path = os.path.join(project_root, icon_value)
                if os.path.exists(abs_path):
                    return abs_path
                
                # 如果在项目根目录中找不到，尝试在用户数据目录中查找
                user_data_dir = os.path.join(os.path.expanduser('~'), '.daohan_navigator')
                abs_path = os.path.join(user_data_dir, icon_value)
                if os.path.exists(abs_path):
                    return abs_path
                
                print(f"图标文件不存在: {icon_value}")
                return None
        
        return None
