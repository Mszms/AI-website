# 主窗口样式定义

from ui.styles.theme_manager import theme_manager

def get_main_window_style():
    """
    返回主窗口的样式表
    """
    # 获取当前主题配置
    theme = theme_manager.get_current_theme()
    
    return f"""
        QMainWindow {{
            background-color: {theme['background_color']};
        }}
        #sidebar {{
            background-color: {theme['primary_color']};
            border: none;
        }}
        #logo-widget {{
            background-color: {theme['secondary_color']};
        }}
        #websites-scroll-area {{
            background-color: {theme['background_color']};
            border: none;
        }}
        #websites-container {{
            background-color: {theme['background_color']};
        }}
        QScrollBar:vertical {{
            background-color: {theme['scrollbar_background']};
            width: 4px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {theme['scrollbar_handle']};
            min-height: 20px;
            border-radius: 2px;
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
        #logo-text {{
            color: white;
            font-size: 18px;
            font-weight: bold;
        }}
        #content {{
            background-color: {theme['content_background']};
            border-radius: 16px;
            margin: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        #content:hover {{
            background-color: {theme['content_background']};
            border: 1px solid rgba(255, 255, 255, 0.5);
        }}
        #category-title {{
            font-size: 24px;
            font-weight: bold;
            color: {theme['primary_color_dark']};
            margin-bottom: 10px;
        }}
        #add-website-btn {{
            background-color: transparent;
            border: none;
            padding: 6px;
            border-radius: 6px;
        }}
        #add-website-btn:hover {{
            background-color: {theme['hover_color']};
        }}
        #import-btn, #export-btn {{
            background-color: transparent;
            border: none;
            padding: 6px;
            border-radius: 6px;
        }}
        #import-btn:hover, #export-btn:hover, #theme-btn:hover {{
            background-color: {theme['hover_color']};
        }}
        #search-container {{
            background-color: {theme['search_container_bg']};
            border: 1px solid {theme['search_container_border']};
            border-radius: 20px;
            height: 36px;
            max-width: 250px;
        }}
        #search-input {{
            background-color: transparent;
            border: none;
            height: 36px;
            padding: 0;
            margin: 0 5px;
            color: {theme['text_color']};
        }}
        #search-input:focus {{
            border: none;
            outline: none;
        }}
        #search-input::placeholder {{
            color: {theme['text_color']};
            opacity: 0.7;
        }}
        #search-icon {{
            margin-left: 0px;
        }}
        #search-clear-btn {{
            background: transparent;
            border: none;
            margin-right: 5px;
        }}
        #search-clear-btn:hover {{
            background-color: {theme['hover_color']};
            border-radius: 12px;
        }}
        /* 子分类导航样式 */
        #subcategory-nav {{
            background-color: transparent;
            margin-bottom: 10px;
        }}
        QPushButton.subcategory-item {{
            background-color: {theme['subcategory_bg']};
            border-radius: 6px;
            padding: 6px 12px;
            color: {theme['primary_color']};
            font-weight: 500;
            border: 1px solid {theme['subcategory_border']};
        }}
        QPushButton.subcategory-item:hover {{
            background-color: {theme['subcategory_hover']};
            border: 1px solid {theme['primary_color']};
        }}
        QPushButton.subcategory-item-selected {{
            background-color: {theme['primary_color']};
            color: {theme['light_text_color']};
            border: 1px solid {theme['primary_color']};
        }}
        QMenu {{
            background-color: transparent;
            border: none;
            padding: 5px;
        }}
        QMenu::item {{
            background-color: {theme['menu_background']};
            padding: 8px 20px;
            border-radius: 4px;
            margin: 2px 5px;
        }}
        QMenu::item:selected {{
            background-color: {theme['menu_hover']};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {theme['menu_border']};
            margin: 5px 10px;
        }}
        QMenu::icon {{
            padding-left: 2px;
        }}
        QMenu::indicator {{
            width: 13px;
            height: 13px;
            background-color: transparent;
            border: 1px solid {theme['primary_color']};
            border-radius: 2px;
        }}
        QMenu::indicator:checked {{
            background-color: {theme['primary_color']};
            image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='9' height='9' viewBox='0 0 9 9'%3E%3Cpath fill='white' d='M1 4.5l2 2 5-5'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: center;
        }}
        /* 添加内容面板作为背景 */
        QMenu::content-margins {{
            left: 0px;
            right: 0px;
            top: 0px;
            bottom: 0px;
        }}
        QMenu::panel {{
            background-color: {theme['menu_background']};
            border: 1px solid {theme['menu_border']};
            border-radius: 8px;
            /* 添加阴影效果 */
            box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        /* 主题切换按钮样式 */
        #theme-btn {{
            background-color: transparent;
            border: none;
            padding: 6px;
            border-radius: 6px;
        }}
    """