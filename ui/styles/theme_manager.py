# 主题管理器

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
import json

# 默认主题配置
DEFAULT_THEME = {
    'primary_color': '#005aea',  # 主色调
    'secondary_color': '#004ed6',  # 次要色调
    'background_color': '#f5f6fa',  # 背景色
    'content_background': 'rgba(255, 255, 255, 0.95)',  # 内容区背景色
    'text_color': '#333333',  # 文本颜色
    'light_text_color': 'white',  # 浅色文本
    'browse_btn_text_color':'#333333',  # 浏览按钮文本颜色
    'border_radius': '12px',  # 边框圆角
    'card_shadow': '0 4px 12px rgba(0, 0, 0, 0.08)',  # 卡片阴影
    'primary_color_dark': '#0052cc',  # 深色主色调
    'card_background': 'white',  # 卡片背景色
    'tag_background': 'rgba(227, 242, 253, 0.7)',  # 标签背景色
    'hover_color': 'rgba(0, 90, 234, 0.15)',  # 悬停颜色
    'menu_background': 'white',  # 菜单背景色
    'menu_hover': '#f0f0f0',  # 菜单悬停色
    'menu_border': '#e0e0e0',  # 菜单边框色
    'scrollbar_background': '#f0f0f0',  # 滚动条背景色
    'scrollbar_handle': '#92adff',  # 滚动条滑块色
    'scrollbar_handle_hover': '#5f87ff',  # 滚动条滑块悬停色
    'search_container_bg': 'white',  # 搜索框背景色
    'search_container_border': '#e0e0e0',  # 搜索框边框色
    'subcategory_bg': '#ffffff',  # 子分类背景色
    'subcategory_border': '#92adff',  # 子分类边框色
    'subcategory_hover': '#ebf6fe',  # 子分类悬停色
    'subcategory_selected': '#005aea',  # 子分类选中色
    'website_icon_color': '#005aea',  # 网站卡片图标颜色
    'subcategory_text_color': '#005aea',  # 子分类文本颜色
    'subcategory_selected_text_color':'#ffffff',  # 子分类选中文本颜色
    'search_icon_color': '#005aea',  # 搜索图标颜色
    'button_icon_color': '#005aea',  # 按钮图标颜色
    'theme_name': '默认主题'  # 主题名称
}

# 暗夜主题配置
DARK_THEME = {
    'primary_color': '#000000',  # 主色调
    'secondary_color': '#000000',  # 次要色调
    'background_color': '#121212',  # 背景色
    'content_background': 'rgba(30, 30, 30, 0.95)',  # 内容区背景色
    'text_color': '#ffffff',  # 文本颜色
    'light_text_color': '#f5f5f5',  # 浅色文本
    'browse_btn_text_color':'#333333',  # 浏览按钮文本颜色
    'border_radius': '12px',  # 边框圆角
    'card_shadow': '0 4px 12px rgba(0, 0, 0, 0.2)',  # 卡片阴影
    'primary_color_dark': '#ffffff',  # 深色主色调
    'card_background': '#1e1e1e',  # 卡片背景色
    'tag_background': 'rgba(255, 255, 255, 1)',  # 标签背景色
    'hover_color': 'rgba(255, 255, 255, 0.2)',  # 悬停颜色
    'menu_background': '#2d2d2d',  # 菜单背景色
    'menu_hover': '#3d3d3d',  # 菜单悬停色
    'menu_border': '#444444',  # 菜单边框色
    'scrollbar_background': '#2a2a2a',  # 滚动条背景色
    'scrollbar_handle': '#555555',  # 滚动条滑块色
    'scrollbar_handle_hover': '#777777',  # 滚动条滑块悬停色
    'search_container_bg': '#2d2d2d',  # 搜索框背景色
    'search_container_border': '#444444',  # 搜索框边框色
    'subcategory_bg': '#2d2d2d',  # 子分类背景色
    'subcategory_border': '#444444',  # 子分类边框色
    'subcategory_hover': '#ffffff',  # 子分类悬停色
    'subcategory_selected': '#ffffff',  # 子分类选中色
    'website_icon_color': '#000000',  # 网站卡片图标颜色
    'subcategory_text_color': '#ffffff',  # 子分类文本颜色  
    'subcategory_selected_text_color':'#333333',  # 子分类选中文本颜色
    'search_icon_color': '#ffffff',  # 搜索图标颜色
    'button_icon_color': '#ffffff',  # 按钮图标颜色
    'theme_name': '暗夜主题'  # 主题名称
}

# 蓝色主题配置
BLUE_THEME = {
    'primary_color': '#2196f3',  # 主色调
    'secondary_color': '#1e88e5',  # 次要色调
    'background_color': '#e3f2fd',  # 背景色
    'content_background': 'rgba(255, 255, 255, 0.95)',  # 内容区背景色
    'text_color': '#333333',  # 文本颜色
    'light_text_color': 'white',  # 浅色文本
    'browse_btn_text_color':'#333333',  # 浏览按钮文本颜色
    'border_radius': '12px',  # 边框圆角
    'card_shadow': '0 4px 12px rgba(33, 150, 243, 0.15)',  # 卡片阴影
    'primary_color_dark': '#1976d2',  # 深色主色调
    'card_background': 'white',  # 卡片背景色
    'tag_background': 'rgba(33, 150, 243, 0.15)',  # 标签背景色
    'hover_color': 'rgba(33, 150, 243, 0.15)',  # 悬停颜色
    'menu_background': 'white',  # 菜单背景色
    'menu_hover': '#e3f2fd',  # 菜单悬停色
    'menu_border': '#bbdefb',  # 菜单边框色
    'scrollbar_background': '#e3f2fd',  # 滚动条背景色
    'scrollbar_handle': '#90caf9',  # 滚动条滑块色
    'scrollbar_handle_hover': '#64b5f6',  # 滚动条滑块悬停色
    'search_container_bg': 'white',  # 搜索框背景色
    'search_container_border': '#bbdefb',  # 搜索框边框色
    'subcategory_bg': 'white',  # 子分类背景色
    'subcategory_border': '#bbdefb',  # 子分类边框色
    'subcategory_hover': '#e3f2fd',  # 子分类悬停色
    'subcategory_selected': '#2196f3',  # 子分类选中色
    'website_icon_color': '#2196f3',  # 网站卡片图标颜色
    'subcategory_text_color': '#2196f3',  # 子分类文本颜色
    'subcategory_selected_text_color': '#ffffff' , # 子分类选中文本颜色
    'search_icon_color': '#2196f3',  # 搜索图标颜色
    'button_icon_color': '#2196f3',  # 按钮图标颜色
    'theme_name': '蓝色主题'  # 主题名称
}

# 绿色主题配置
GREEN_THEME = {
    'primary_color': '#4caf50',  # 主色调
    'secondary_color': '#43a047',  # 次要色调
    'background_color': '#e8f5e9',  # 背景色
    'content_background': 'rgba(255, 255, 255, 0.95)',  # 内容区背景色
    'text_color': '#333333',  # 文本颜色
    'light_text_color': 'white',  # 浅色文本
    'browse_btn_text_color':'#333333',  # 浏览按钮文本颜色
    'border_radius': '12px',  # 边框圆角
    'card_shadow': '0 4px 12px rgba(76, 175, 80, 0.15)',  # 卡片阴影
    'primary_color_dark': '#388e3c',  # 深色主色调
    'card_background': 'white',  # 卡片背景色
    'tag_background': 'rgba(76, 175, 80, 0.15)',  # 标签背景色
    'hover_color': 'rgba(76, 175, 80, 0.15)',  # 悬停颜色
    'menu_background': 'white',  # 菜单背景色
    'menu_hover': '#e8f5e9',  # 菜单悬停色
    'menu_border': '#c8e6c9',  # 菜单边框色
    'scrollbar_background': '#e8f5e9',  # 滚动条背景色
    'scrollbar_handle': '#a5d6a7',  # 滚动条滑块色
    'scrollbar_handle_hover': '#81c784',  # 滚动条滑块悬停色
    'search_container_bg': 'white',  # 搜索框背景色
    'search_container_border': '#c8e6c9',  # 搜索框边框色
    'subcategory_bg': 'white',  # 子分类背景色
    'subcategory_border': '#c8e6c9',  # 子分类边框色
    'subcategory_hover': '#e8f5e9',  # 子分类悬停色
    'subcategory_selected':'#4caf50',  # 子分类选中色
    'website_icon_color': '#4caf50',  # 网站卡片图标颜色
    'subcategory_text_color': '#4caf50',  # 子分类文本颜色
    'subcategory_selected_text_color': '#ffffff' , # 子分类选中文本颜色
    'search_icon_color': '#4caf50',  # 搜索图标颜色
    'button_icon_color': '#4caf50',  # 按钮图标颜色
    'theme_name': '绿色主题'  # 主题名称
}

class ThemeManager:
    def __init__(self):
        self.settings = QSettings('AINavigator', 'AIWebsiteNavigator')
        self.current_theme = self.load_theme()
        
    def load_theme(self):
        # 从设置中加载主题，如果没有则使用默认主题
        theme_name = self.settings.value('theme', 'default')
        if theme_name == 'dark':
            return DARK_THEME
        elif theme_name == 'blue':
            return BLUE_THEME
        elif theme_name == 'green':
            return GREEN_THEME
        return DEFAULT_THEME
    
    def save_theme(self, theme_name):
        # 保存主题设置
        self.settings.setValue('theme', theme_name)
        self.settings.sync()
    
    def switch_theme(self, theme_name):
        # 切换主题
        if theme_name == 'dark':
            self.current_theme = DARK_THEME
            self.save_theme('dark')
        elif theme_name == 'blue':
            self.current_theme = BLUE_THEME
            self.save_theme('blue')
        elif theme_name == 'green':
            self.current_theme = GREEN_THEME
            self.save_theme('green')
        else:
            self.current_theme = DEFAULT_THEME
            self.save_theme('default')
        return self.current_theme
    
    def get_current_theme(self):
        # 获取当前主题
        return self.current_theme
        
    def get_all_themes(self):
        # 获取所有可用主题
        return {
            'default': DEFAULT_THEME,
            'dark': DARK_THEME,
            'blue': BLUE_THEME,
            'green': GREEN_THEME
        }

# 创建全局主题管理器实例
theme_manager = ThemeManager()