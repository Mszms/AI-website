# 按钮样式定义

from ui.styles.theme_manager import theme_manager

def get_subcategory_button_style(selected=False):
    """
    返回子分类按钮的样式表
    
    Args:
        selected: 是否为选中状态
    """
    # 获取当前主题配置
    theme = theme_manager.get_current_theme()
    
    if selected:
        return f"""
            background-color: {theme['subcategory_selected']};
            color: {theme['subcategory_selected_text_color']};
            border: 1px solid {theme['subcategory_selected']};
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: 500;
        """
    else:
        return f"""
            background-color: {theme['subcategory_bg']};
            border-radius: 6px;
            padding: 6px 12px;
            color: {theme['subcategory_text_color']};
            font-weight: 500;
            border: 1px solid {theme['subcategory_border']};
        """

def get_child_category_button_style(selected=False):
    """
    返回子分类按钮的样式表（小尺寸版本）
    
    Args:
        selected: 是否为选中状态
    """
    # 获取当前主题配置
    theme = theme_manager.get_current_theme()
    
    if selected:
        return f"""
            background-color: {theme['subcategory_selected']};
            border-radius: 4px;
            padding: 4px 8px;
            color: {theme['subcategory_selected_text_color']};
            font-size: 12px;
            border: 1px solid {theme['subcategory_selected']};
        """
    else:
        return f"""
            background-color: {theme['subcategory_bg']};
            border-radius: 4px;
            padding: 4px 8px;
            color: {theme['subcategory_text_color']};
            font-size: 12px;
            border: 1px solid {theme['subcategory_border']};
        """