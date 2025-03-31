import os
import sys
import PyInstaller.__main__

# 激活虚拟环境
venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'Scripts', 'python.exe')
sys.executable = venv_python
# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 需要包含的数据文件
data_files = [
    ('example_data.json', '.'),  # 示例数据文件，确保可读写
    ('app.ico', '.'),  # 应用图标
    ('ui/resources/icons/custom', 'ui/resources/icons/custom'),  # 自定义图标目录
    ('ui/resources/icons/default', 'ui/resources/icons/default'),  # 默认图标目录
    # 调整qtawesome图标资源路径
    (os.path.join(current_dir, 'venv', 'Lib', 'site-packages', 'qtawesome', 'fonts'), 'qtawesome/fonts'),
    (os.path.join(current_dir, 'venv', 'Lib', 'site-packages', 'qtawesome', '_data'), 'qtawesome/_data')
]

# 构建--add-data参数
add_data_args = []
for src, dst in data_files:
    src_path = os.path.join(current_dir, src)
    if os.path.exists(src_path):
        # 在Windows上，使用分号分隔源和目标
        add_data_args.append(f'--add-data={src_path};{dst}')
    else:
        print(f"警告: 文件或目录 {src_path} 不存在，将被跳过")

# 需要显式包含的库
hidden_imports = [
    '--hidden-import=openpyxl',
    '--hidden-import=openpyxl.cell',
    '--hidden-import=openpyxl.workbook',
    '--hidden-import=openpyxl.reader.excel',
    '--hidden-import=openpyxl.styles',
    '--hidden-import=pymongo',
    '--hidden-import=qtawesome'
]

# 构建PyInstaller命令
pyinstaller_args = [
    'main.py',  # 主脚本
    '--name=AI网站导航系统',  # 应用名称
    '--windowed',  # 使用GUI模式，不显示控制台
    '--onefile',  # 打包为单个exe文件
    '--icon=app.ico',  # 应用图标
    '--clean',  # 清理临时文件
] + add_data_args + hidden_imports

# 打印将要执行的命令
print("正在执行PyInstaller打包命令:")
print(" ".join(pyinstaller_args))

# 执行PyInstaller打包
PyInstaller.__main__.run(pyinstaller_args)

print("\n打包完成!")
print("可执行文件位于 dist 目录下")