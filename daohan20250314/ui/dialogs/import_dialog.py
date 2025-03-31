import os
import json
import pandas as pd
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFileDialog, QTextEdit, QWidget, QGraphicsDropShadowEffect,
                            QTabWidget, QMessageBox, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import qtawesome as qta
from bson import ObjectId
from config import UI_CONFIG

from ..components.base_dialog import BaseDialog
from ui.styles.theme_manager import theme_manager

class ImportDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('导入数据')
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # 初始化导入的数据
        self.imported_data = None
        
        self.setup_ui()
    

    def _is_valid_object_id(self, id_str):
        """检查字符串是否为有效的ObjectId格式"""
        if not isinstance(id_str, str):
            return False
        try:
            # 检查是否为24位十六进制字符串
            if len(id_str) != 24:
                return False
            # 尝试转换为ObjectId
            ObjectId(id_str)
            return True
        except Exception:
            return False
    
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
        title_label = QLabel('导入数据')
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
        
        # 创建选项卡
        tab_widget = QTabWidget()
        tab_widget.setObjectName('tab-widget')
        
        # 文件导入选项卡
        file_tab = QWidget()
        file_layout = QVBoxLayout(file_tab)
        
        # 文件选择区域
        file_select_layout = QHBoxLayout()
        self.file_path_label = QLabel('未选择文件')
        self.file_path_label.setObjectName('file-path-label')
        file_select_layout.addWidget(self.file_path_label, 1)
        
        browse_btn = QPushButton('浏览...')
        browse_btn.setObjectName('browse-btn')
        browse_btn.clicked.connect(self.browse_file)
        file_select_layout.addWidget(browse_btn)
        
        file_layout.addLayout(file_select_layout)
        
        # 文件预览区域
        preview_label = QLabel('文件预览:')
        file_layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setObjectName('preview-text')
        file_layout.addWidget(self.preview_text)
        
        # 添加文件导入选项卡
        tab_widget.addTab(file_tab, '从文件导入')
        
        # 模板选项卡
        template_tab = QWidget()
        template_layout = QVBoxLayout(template_tab)
        
        template_info = QLabel('下载并使用以下模板文件进行数据导入:')
        template_layout.addWidget(template_info)
        
        # Excel模板
        excel_btn = QPushButton('下载Excel模板')
        excel_btn.setIcon(qta.icon('fa5s.file-excel', color=theme_manager.get_current_theme()['primary_color']))
        excel_btn.setObjectName('template-btn')
        excel_btn.clicked.connect(lambda: self.download_template('excel'))
        template_layout.addWidget(excel_btn)
        
        # CSV模板
        csv_btn = QPushButton('下载CSV模板')
        csv_btn.setIcon(qta.icon('fa5s.file-csv', color=theme_manager.get_current_theme()['primary_color']))
        csv_btn.setObjectName('template-btn')
        csv_btn.clicked.connect(lambda: self.download_template('csv'))
        template_layout.addWidget(csv_btn)
        
        # JSON模板
        json_btn = QPushButton('下载JSON模板')
        json_btn.setIcon(qta.icon('fa5s.file-code', color=theme_manager.get_current_theme()['primary_color']))
        json_btn.setObjectName('template-btn')
        json_btn.clicked.connect(lambda: self.download_template('json'))
        template_layout.addWidget(json_btn)
        template_layout.addStretch()
        
        # 添加模板选项卡
        tab_widget.addTab(template_tab, '下载模板')
        
        main_layout.addWidget(tab_widget)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setObjectName('cancel-btn')
        cancel_btn.clicked.connect(self.reject)
        
        self.import_btn = QPushButton('导入')
        self.import_btn.setObjectName('ok-btn')
        self.import_btn.setEnabled(False)  # 初始禁用导入按钮
        self.import_btn.clicked.connect(self.import_data)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.import_btn)
        main_layout.addLayout(button_layout)
        
        layout.addWidget(main_container)
        
        # 设置基础样式
        theme = theme_manager.get_current_theme()
        self.setStyleSheet(self._get_base_style() + f"""
            #file-path-label {{
                padding: 10px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f9f9f9;
                color: {theme['browse_btn_text_color']};
            }}
            #preview-text {{
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f9f9f9;
                font-family: monospace;
                color: {theme['browse_btn_text_color']};
            }}
            #browse-btn, #template-btn {{
                background-color: #f0f0f0;
                color: {theme['browse_btn_text_color']};
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
            }}
            #browse-btn:hover, #template-btn:hover {{
                background-color: #e0e0e0;
            }}
            QTabWidget::pane {{
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                top: -1px;
            }}
            QTabBar::tab {{
                background-color: #f0f0f0;
                color: {theme['browse_btn_text_color']};
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                border-bottom: 1px solid white;
            }}""")

    
    def browse_file(self):
        """打开文件选择对话框"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("数据文件 (*.xlsx *.xls *.csv *.json)")
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.file_path_label.setText(file_path)
            self.preview_file(file_path)
    
    def detect_file_encoding(self, file_path):
        """检测文件编码"""
        # 尝试使用chardet自动检测编码
        try:
            import chardet
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
            
            detected_encoding = result['encoding']
            confidence = result['confidence']
            
            if detected_encoding and confidence > 0.7:
                return detected_encoding, confidence
        except ImportError:
            pass
        except Exception:
            pass
        
        # 如果自动检测失败，尝试预设的编码列表
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'latin1']
        for encoding in encodings:
            try:
                # 使用二进制模式读取文件的前几行进行编码测试
                with open(file_path, 'rb') as f:
                    raw_data = f.read(1024)  # 读取前1KB进行测试
                
                # 尝试解码
                raw_data.decode(encoding)
                return encoding, 1.0
            except UnicodeDecodeError:
                continue
        
        return None, 0.0
    
    def preview_file(self, file_path):
        """预览文件内容"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                # 预览Excel文件
                df = pd.read_excel(file_path)
                self.preview_text.setText(df.head(10).to_string())
                self.parse_excel_data(file_path)
            elif file_ext == '.csv':
                # 检测CSV文件编码
                encoding, confidence = self.detect_file_encoding(file_path)
                
                if encoding:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        if confidence < 1.0:
                            self.preview_text.setText(f"自动检测到编码: {encoding} (置信度: {confidence:.2f})\n\n{df.head(10).to_string()}")
                        else:
                            self.preview_text.setText(f"使用 {encoding} 编码成功读取文件:\n\n{df.head(10).to_string()}")
                        self.parse_csv_data(file_path, encoding)
                    except Exception as e:
                        self.preview_text.setText(f"使用 {encoding} 编码读取文件失败: {str(e)}")
                        self.import_btn.setEnabled(False)
                        self.imported_data = None
                        return
                else:
                    # 如果所有尝试都失败
                    self.preview_text.setText("无法识别文件编码，请尝试将文件保存为UTF-8编码格式后再导入。")
                    self.import_btn.setEnabled(False)
                    self.imported_data = None
                    return
            elif file_ext == '.json':
                # 检测JSON文件编码
                encoding, _ = self.detect_file_encoding(file_path)
                
                if encoding:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            data = json.load(f)
                        self.preview_text.setText(f"使用 {encoding} 编码成功读取文件:\n\n{json.dumps(data, indent=2, ensure_ascii=False)[:1000]}...")
                        self.parse_json_data(file_path, encoding)
                    except Exception as e:
                        self.preview_text.setText(f"使用 {encoding} 编码读取文件失败: {str(e)}")
                        self.import_btn.setEnabled(False)
                        self.imported_data = None
                        return
                else:
                    # 如果所有编码都失败
                    self.preview_text.setText("无法识别文件编码，请尝试将文件保存为UTF-8编码格式后再导入。")
                    self.import_btn.setEnabled(False)
                    self.imported_data = None
                    return
            
            # 启用导入按钮
            self.import_btn.setEnabled(True)
            
        except Exception as e:
            self.preview_text.setText(f"预览文件失败: {str(e)}")
            self.import_btn.setEnabled(False)
            self.imported_data = None
    
    def process_categories(self, categories):
        """处理分类数据，统一处理parent_id和_id字段"""
        category_name_to_id = {}
        category_id_map = {}
        
        # 首先处理顶级分类（parent_id为None的分类）
        for category in categories:
            if ('parent_id' not in category) or (category['parent_id'] is None or 
                                               (isinstance(category['parent_id'], str) and category['parent_id'] == '') or 
                                               (hasattr(pd, 'isna') and pd.isna(category['parent_id']))):
                category['parent_id'] = None
                # 如果没有_id，创建一个
                if '_id' not in category or (hasattr(pd, 'isna') and pd.isna(category.get('_id'))):
                    category['_id'] = str(ObjectId())
                else:
                    category['_id'] = str(category['_id'])
                
                category_name_to_id[category['name']] = category['_id']
                category_id_map[category['_id']] = category['_id']
        
        # 然后处理子分类
        for category in categories:
            if 'parent_id' in category and category['parent_id'] and \
               not (hasattr(pd, 'isna') and pd.isna(category['parent_id'])) and \
               not (isinstance(category['parent_id'], str) and category['parent_id'] == ''):
                parent_id = category['parent_id']
                
                # 如果parent_id是字符串但不是ObjectId格式，则视为分类名称
                if isinstance(parent_id, str) and not self._is_valid_object_id(parent_id):
                    if parent_id in category_name_to_id:
                        category['parent_id'] = category_name_to_id[parent_id]
                    else:
                        # 如果找不到父分类，设为None
                        category['parent_id'] = None
                # 如果parent_id是ObjectId格式，检查是否存在
                elif isinstance(parent_id, str) and self._is_valid_object_id(parent_id):
                    if parent_id in category_id_map:
                        category['parent_id'] = parent_id
                    else:
                        # 如果找不到父分类ID，设为None
                        category['parent_id'] = None
                
                # 如果没有_id，创建一个
                if '_id' not in category or (hasattr(pd, 'isna') and pd.isna(category.get('_id'))):
                    category['_id'] = str(ObjectId())
                else:
                    category['_id'] = str(category['_id'])
                
                category_name_to_id[category['name']] = category['_id']
                category_id_map[category['_id']] = category['_id']
        
        return categories, category_name_to_id, category_id_map
    
    def process_websites(self, websites, category_name_to_id, category_id_map, create_missing_categories=False):
        """处理网站数据，统一处理category_id和tags字段"""
        processed_categories = []
        
        for website in websites:
            # 处理标签字段
            if 'tags' in website and isinstance(website['tags'], str) and website['tags'] and not (hasattr(pd, 'isna') and pd.isna(website['tags'])):
                website['tags'] = [tag.strip() for tag in website['tags'].split(',') if tag.strip()]
            
            # 处理category_name字段，将其转换为category_id
            if 'category_name' in website and website['category_name'] and not (hasattr(pd, 'isna') and pd.isna(website['category_name'])):
                category_name = website['category_name']
                
                # 尝试精确匹配
                if category_name in category_name_to_id:
                    website['category_id'] = category_name_to_id[category_name]
                elif create_missing_categories:
                    # 如果没有找到精确匹配，创建一个新的分类
                    new_category_id = str(ObjectId())
                    new_category = {
                        '_id': new_category_id,
                        'name': category_name,
                        'icon': '',
                        'description': '',
                        'parent_id': None
                    }
                    processed_categories.append(new_category)
                    category_name_to_id[category_name] = new_category_id
                    category_id_map[new_category_id] = new_category_id
                    website['category_id'] = new_category_id
                
                # 删除category_name字段
                del website['category_name']
            # 处理category_id字段，确保它存在于分类中
            elif 'category_id' in website and website['category_id'] and not (hasattr(pd, 'isna') and pd.isna(website['category_id'])):
                category_id = str(website['category_id'])
                if self._is_valid_object_id(category_id) and category_id not in category_id_map:
                    # 如果找不到对应的分类ID，设为None
                    website['category_id'] = None
        
        return websites, processed_categories
    
    def validate_category(self, category, categories):
        """验证单个分类数据"""
        if 'name' not in category or not category['name']:
            return False, '分类数据缺少必要字段: name'
        
        # 验证parent_id字段
        if 'parent_id' in category and category['parent_id']:
            # 检查父分类是否存在 - 支持ID和名称两种情况
            parent_id = category['parent_id']
            
            # 如果parent_id是字符串但不是ObjectId格式，则视为分类名称
            if isinstance(parent_id, str) and not self._is_valid_object_id(parent_id):
                parent_name = parent_id
                parent_exists = any(c['name'] == parent_name for c in categories)
                if not parent_exists:
                    return False, f'分类 "{category["name"]}" 的父分类 "{parent_name}" 不存在'
            # 如果parent_id是ObjectId格式，则检查ID是否存在
            elif self._is_valid_object_id(parent_id):
                parent_exists = any(str(c.get('_id', '')) == str(parent_id) for c in categories)
                if not parent_exists:
                    return False, f'分类 "{category["name"]}" 的父分类ID "{parent_id}" 不存在'
        
        return True, ''
    
    def validate_website(self, website, categories):
        """验证单个网站数据"""
        if 'name' not in website or not website['name']:
            return False, '网站数据缺少必要字段: name'
        if 'url' not in website or not website['url']:
            return False, '网站数据缺少必要字段: url'
        
        # 验证category_id或category_name字段
        if 'category_id' in website and website['category_id']:
            category_id = website['category_id']
            # 检查分类ID是否存在
            category_exists = any(str(c.get('_id', '')) == str(category_id) for c in categories)
            if not category_exists:
                return False, f'网站 "{website["name"]}" 的分类ID "{category_id}" 不存在'
        elif 'category_name' in website and website['category_name']:
            category_name = website['category_name']
            category_exists = any(c['name'] == category_name for c in categories)
            if not category_exists:
                return False, f'网站 "{website["name"]}" 的分类 "{category_name}" 不存在'
        
        return True, ''
    
    def parse_csv_data(self, file_path, encoding='utf-8'):
        """解析CSV文件数据"""
        try:
            # 读取CSV文件
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                # 获取列名
                headers = list(df.columns)
            except UnicodeDecodeError:
                # 如果指定编码失败，尝试使用GBK编码
                df = pd.read_csv(file_path, encoding='gbk')
                encoding = 'gbk'
                # 获取列名
                headers = list(df.columns)
                self.preview_text.append(f"使用GBK编码成功读取文件")
            
            # 区分分类和网站数据
            categories = []
            websites = []
            
            # 检查是否为分类模板文件
            is_category_template = any(col in headers for col in ['name', 'icon', 'description']) and any(col in headers for col in ['parent_id'])
            is_website_template = any(col in headers for col in ['name', 'url', 'description']) and any(col in headers for col in ['category_name'])
            
            # 如果已经有导入的数据，合并处理
            if self.imported_data:
                categories.extend(self.imported_data.get('categories', []))
                websites.extend(self.imported_data.get('websites', []))
            
            if is_category_template and not is_website_template:
                # 处理分类模板文件
                for _, row in df.iterrows():
                    record = row.to_dict()
                    # 确保数据完整性
                    if 'name' in record and record['name'] and not pd.isna(record['name']):
                        categories.append(record)
                self.preview_text.append(f"从分类模板文件中提取了 {len(categories)} 个分类记录")
            elif is_website_template:
                # 处理网站模板文件
                for _, row in df.iterrows():
                    record = row.to_dict()
                    # 确保数据完整性
                    if 'name' in record and record['name'] and not pd.isna(record['name']):
                        websites.append(record)
                self.preview_text.append(f"从网站模板文件中提取了 {len(websites)} 个网站记录")
            else:
                # 处理常规导出文件（包含type字段）
                for _, row in df.iterrows():
                    record = row.to_dict()
                    
                    # 根据记录类型字段区分
                    if 'type' in record:
                        if record['type'] == 'category':
                            # 移除type字段
                            del record['type']
                            categories.append(record)
                        elif record['type'] == 'website':
                            # 移除type字段
                            del record['type']
                            websites.append(record)
            
            # 处理分类数据
            processed_categories, category_name_to_id, category_id_map = self.process_categories(categories)
            
            # 处理网站数据
            processed_websites, new_categories = self.process_websites(websites, category_name_to_id, category_id_map, True)
            
            # 合并新创建的分类
            if new_categories:
                processed_categories.extend(new_categories)
            
            self.imported_data = {
                'categories': processed_categories,
                'websites': processed_websites
            }
            
            # 显示导入数据统计
            self.preview_text.append(f"\n当前已导入 {len(processed_categories)} 个分类和 {len(processed_websites)} 个网站")
            self.preview_text.append("\n提示：您可以继续导入其他文件，数据将会自动合并。")
            
        except Exception as e:
            self.preview_text.setText(f"解析CSV文件失败: {str(e)}")
            self.imported_data = None
    
    def parse_excel_data(self, file_path):
        """解析Excel文件数据"""
        try:
            # 读取分类和网站数据
            categories_df = pd.read_excel(file_path, sheet_name='categories')
            websites_df = pd.read_excel(file_path, sheet_name='websites')
            
            # 转换为字典列表
            categories = categories_df.to_dict('records')
            websites = websites_df.to_dict('records')
            
            # 处理分类数据
            processed_categories, category_name_to_id, category_id_map = self.process_categories(categories)
            
            # 处理网站数据
            processed_websites, _ = self.process_websites(websites, category_name_to_id, category_id_map)
            
            self.imported_data = {
                'categories': processed_categories,
                'websites': processed_websites
            }
            
        except Exception as e:
            self.preview_text.setText(f"解析Excel文件失败: {str(e)}")
            self.imported_data = None
    
    def parse_json_data(self, file_path, encoding='utf-8'):
        """解析JSON文件数据"""
        try:
            # 读取JSON文件
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            
            # 检查数据格式
            if not isinstance(data, dict) or 'categories' not in data or 'websites' not in data:
                self.preview_text.setText("JSON文件格式不正确，请确保包含'categories'和'websites'字段")
                self.imported_data = None
                return
            
            categories = data['categories']
            websites = data['websites']
            
            # 处理分类数据
            processed_categories, category_name_to_id, category_id_map = self.process_categories(categories)
            
            # 处理网站数据
            processed_websites, _ = self.process_websites(websites, category_name_to_id, category_id_map)
            
            self.imported_data = {
                'categories': processed_categories,
                'websites': processed_websites
            }
            
        except Exception as e:
            self.preview_text.setText(f"解析JSON文件失败: {str(e)}")
            self.imported_data = None
    
    def download_template(self, template_type):
        """下载模板文件"""
        try:
            # 创建示例数据 - 添加顶级分类和子分类结构
            categories = [
                {'name': '搜索引擎', 'icon': 'fa5s.search', 'description': '各类搜索引擎', 'parent_id': None},  # 顶级分类
                {'name': '国内搜索', 'icon': 'fa5s.globe-asia', 'description': '中国搜索引擎', 'parent_id': '搜索引擎'},  # 子分类
                {'name': '国外搜索', 'icon': 'fa5s.globe-americas', 'description': '国际搜索引擎', 'parent_id': '搜索引擎'},  # 子分类
                {'name': 'AI工具', 'icon': 'fa5s.robot', 'description': '人工智能相关工具', 'parent_id': None},  # 顶级分类
                {'name': 'AI聊天', 'icon': 'fa5s.comments', 'description': 'AI聊天工具', 'parent_id': 'AI工具'},  # 子分类
                {'name': 'AI绘画', 'icon': 'fa5s.paint-brush', 'description': 'AI绘画工具', 'parent_id': 'AI工具'}  # 子分类
            ]
            
            websites = [
                {
                    'name': '百度', 
                    'url': 'https://www.baidu.com', 
                    'description': '中文搜索引擎', 
                    'category_name': '国内搜索',  # 使用子分类名称
                    'icon': 'fa5s.search', 
                    'tags': '搜索,中文,百度'
                },
                {
                    'name': '谷歌', 
                    'url': 'https://www.google.com', 
                    'description': '全球最大的搜索引擎', 
                    'category_name': '国外搜索',  # 使用子分类名称
                    'icon': 'fa5s.search', 
                    'tags': '搜索,国际,谷歌'
                },
                {
                    'name': 'ChatGPT', 
                    'url': 'https://chat.openai.com', 
                    'description': 'OpenAI开发的AI聊天机器人', 
                    'category_name': 'AI聊天',  # 使用子分类名称
                    'icon': 'fa5s.robot', 
                    'tags': 'AI,聊天,OpenAI'
                },
                {
                    'name': 'Midjourney', 
                    'url': 'https://www.midjourney.com', 
                    'description': 'AI图像生成工具', 
                    'category_name': 'AI绘画',  # 使用子分类名称
                    'icon': 'fa5s.paint-brush', 
                    'tags': 'AI,绘画,图像生成'
                }
            ]
            
            # 选择保存路径
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            
            if template_type == 'excel':
                file_dialog.setNameFilter("Excel文件 (*.xlsx)")
                file_dialog.setDefaultSuffix("xlsx")
                default_name = "导航网站导入模板.xlsx"
            elif template_type == 'csv':
                file_dialog.setNameFilter("CSV文件 (*.csv)")
                file_dialog.setDefaultSuffix("csv")
                default_name = "导航网站导入模板.csv"
            else:  # json
                file_dialog.setNameFilter("JSON文件 (*.json)")
                file_dialog.setDefaultSuffix("json")
                default_name = "导航网站导入模板.json"
            
            file_dialog.selectFile(default_name)
            
            if file_dialog.exec():
                save_path = file_dialog.selectedFiles()[0]
                
                if template_type == 'excel':
                    # 创建Excel文件，分类和网站分别放在不同的sheet
                    with pd.ExcelWriter(save_path) as writer:
                        pd.DataFrame(categories).to_excel(writer, sheet_name='categories', index=False)
                        pd.DataFrame(websites).to_excel(writer, sheet_name='websites', index=False)
                
                elif template_type == 'csv':
                    # 创建两个CSV文件 - 一个用于分类，一个用于网站
                    base_path = os.path.splitext(save_path)[0]
                    categories_path = f"{base_path}_categories.csv"
                    websites_path = f"{base_path}_websites.csv"
                    
                    pd.DataFrame(categories).to_csv(categories_path, index=False)
                    pd.DataFrame(websites).to_csv(websites_path, index=False)
                    
                    QMessageBox.information(self, '成功', 
                                          f'模板文件已保存到:\n{categories_path}\n{websites_path}')
                    return
                
                else:  # json
                    # 创建JSON文件
                    with open(save_path, 'w', encoding='utf-8') as f:
                        json.dump({'categories': categories, 'websites': websites}, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, '成功', f'模板文件已保存到: {save_path}')
                
        except Exception as e:
                QMessageBox.warning(self, '错误', f'创建模板文件失败: {str(e)}')
    
    def import_data(self):
        """导入数据"""
        if not self.imported_data:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('错误')
            msg_box.setText('没有有效的导入数据')
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
            return
        
        # 验证数据
        if not self.validate_imported_data():
            return
        
        # 接受对话框
        self.accept()
    
    def validate_imported_data(self):
        """验证导入的数据"""
        # 检查分类数据
        for category in self.imported_data.get('categories', []):
            valid, error_msg = self.validate_category(category, self.imported_data.get('categories', []))
            if not valid:
                msg_box = QMessageBox
                msg_box.setWindowTitle('错误')
                msg_box.setText('分类数据缺少必要字段: name')
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.exec()
                return False
            
            # 验证parent_id字段
            if 'parent_id' in category and category['parent_id'] and \
               not (hasattr(pd, 'isna') and pd.isna(category['parent_id'])) and \
               not (isinstance(category['parent_id'], str) and category['parent_id'] == ''):
                # 检查父分类是否存在 - 支持ID和名称两种情况
                parent_id = category['parent_id']
                
                # 如果parent_id是字符串但不是ObjectId格式，则视为分类名称
                if isinstance(parent_id, str) and not self._is_valid_object_id(parent_id):
                    parent_name = parent_id
                    parent_exists = any(c['name'] == parent_name for c in self.imported_data.get('categories', []))
                    if not parent_exists:
                        msg_box = QMessageBox
                        msg_box.setWindowTitle('错误')
                        msg_box.setText(f'分类 "{category["name"]}" 的父分类 "{parent_name}" 不存在')
                        msg_box.setIcon(QMessageBox.Icon.Warning)
                        msg_box.exec()
                        return False
                # 如果parent_id是ObjectId格式，则检查ID是否存在
                elif self._is_valid_object_id(parent_id):
                    parent_exists = any(str(c.get('_id', '')) == str(parent_id) for c in self.imported_data.get('categories', []))
                    if not parent_exists:
                        msg_box = QMessageBox
                        msg_box.setWindowTitle('错误')
                        msg_box.setText(f'分类 "{category["name"]}" 的父分类ID "{parent_id}" 不存在')
                        msg_box.setIcon(QMessageBox.Icon.Warning)
                        msg_box.exec()
                        return False
        
        # 检查网站数据
        for website in self.imported_data.get('websites', []):
            valid, error_msg = self.validate_website(website, self.imported_data.get('categories', []))
            if not valid:
                msg_box = QMessageBox
                msg_box.setWindowTitle('错误')
                msg_box.setText(error_msg)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.exec()
                return False
        
        # 检查网站数据
        for website in self.imported_data.get('websites', []):
            valid, error_msg = self.validate_website(website, self.imported_data.get('categories', []))
            if not valid:
                msg_box = QMessageBox
                msg_box.setWindowTitle('错误')
                msg_box.setText(error_msg)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.exec()
                return False
        
        return True
    
    def get_imported_data(self):
        """获取导入的数据"""
        return self.imported_data