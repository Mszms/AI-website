# AI网站导航系统

## 项目介绍
这是一个基于Python和Qt的AI网站导航桌面系统，提供了便捷的AI相关网站收藏和访问功能。系统采用左侧分类导航栏和右侧网站卡片的布局设计，每个卡片包含网站图标、介绍和标签，支持点击打开网站功能。应用支持数据持久化存储和打包为可执行文件，方便用户使用。

## 主要功能
- 分类导航：左侧提供网站分类导航，支持分类的新增、编辑和删除
- 子分类支持：支持多级分类结构，可以创建父子关系的分类
- 网站卡片：右侧以卡片形式展示网站信息，包含网站图标、名称、描述和标签
- 网站管理：支持新增、编辑和删除网站，可自定义网站图标
- 网站详情：支持查看网站详细信息，包括完整描述和所有标签
- 分类管理：支持新增、编辑和删除分类，可设置分类图标
- 搜索功能：支持按名称搜索网站
- 数据导入导出：支持JSON格式的网站数据导入和导出功能
- 主题切换：支持默认、暗夜、蓝色和绿色四种主题切换，满足不同用户的视觉偏好
- 数据持久化：支持将数据保存到用户本地目录，确保数据不丢失
- 可执行文件打包：支持打包为独立的可执行文件，无需安装Python环境

## 技术栈
- 前端：Python + PyQt6
- 数据存储：本地JSON文件（支持MongoDB配置）
- 图标：使用Font Awesome或自定义图标（qtawesome库）
- 样式管理：主题管理系统，支持多主题切换
- 打包工具：PyInstaller

## 安装与运行

### 环境要求
- Python 3.10+
- PyQt6
- pymongo
- qtawesome
- requests
- pillow
- openpyxl
- pyinstaller（仅打包需要）

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
python main.py
```

### 打包应用
```bash
python build_exe.py
```

## 项目结构
```
.
├── main.py                 # 程序入口
├── requirements.txt        # 项目依赖
├── config.py              # 配置文件
├── database/              # 数据库相关
│   └── db_manager.py      # 数据库管理器
├── models/                # 数据模型
│   ├── category.py        # 分类模型
│   └── website.py         # 网站模型
├── ui/                    # 用户界面
│   ├── components/        # UI组件
│   │   ├── base_dialog.py    # 对话框基类
│   │   ├── category_list.py  # 分类列表组件
│   │   ├── website_card.py   # 网站卡片组件
│   │   └── confirm_dialog.py # 确认对话框
│   ├── dialogs/           # 功能对话框
│   │   ├── add_category_dialog.py  # 添加分类对话框
│   │   ├── add_website_dialog.py   # 添加网站对话框
│   │   ├── import_dialog.py        # 导入数据对话框
│   │   └── export_dialog.py        # 导出数据对话框
│   ├── styles/            # 样式管理
│   │   ├── theme_manager.py  # 主题管理器
│   │   ├── main_styles.py    # 主窗口样式
│   │   └── button_styles.py  # 按钮样式
│   └── resources/         # 资源文件
│       └── icons/         # 图标
└── utils/                # 工具函数
    └── icon_utils.py     # 图标工具函数
```


