# 配置文件

# MongoDB配置
MONGO_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'db_name': 'ai_navigator',
    'website_collection': 'websites',
    'category_collection': 'categories'
}

# 应用配置
APP_CONFIG = {
    'app_name': 'AI网站导航系统',
    'version': '1.0.0',
    'author': 'AI Navigator Team',
    'default_browser': None,  # None表示使用系统默认浏览器
    'window_size': (1200, 800),
    'sidebar_width': 250,
    'card_width': 280,
    'card_height': 180
}

# 界面样式配置
# 在 UI_CONFIG 字典中添加 primary_color_dark 键
UI_CONFIG = {
    'border_radius': '12px',  # 边框圆角
    'card_shadow': '0 4px 12px rgba(0, 0, 0, 0.08)',  # 卡片阴影
}