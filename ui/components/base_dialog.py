from PyQt6.QtWidgets import QDialog, QWidget, QGraphicsDropShadowEffect, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ui.styles.theme_manager import theme_manager

class BaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置窗口属性 - 移除默认边框
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建遮罩层
        self.mask = QWidget(parent)
        self.mask.setObjectName('dialog-mask')
        self.mask.setStyleSheet("#dialog-mask { background-color: rgba(0, 0, 0, 0.5); }")
        # 使用QApplication.primaryScreen()替代已废弃的desktop()方法
        self.mask.setGeometry(parent.geometry() if parent else QApplication.primaryScreen().geometry())
        self.mask.hide()
        
        # 用于窗口拖动
        self.old_pos = None
        
        # 设置基础样式
        self.setStyleSheet(self._get_base_style())
        
    def _setup_shadow(self):
        # 添加阴影效果
        try:
            # 使用更保守的阴影参数，避免 UpdateLayeredWindowIndirect 错误
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(5)  # 进一步减小模糊半径
            shadow.setColor(QColor(0, 0, 0, 10))  # 进一步降低阴影不透明度
            shadow.setOffset(0, 1)  # 使用最小偏移量
            self.setGraphicsEffect(shadow)
        except Exception as e:
            print(f"设置阴影效果失败: {str(e)}")
            # 如果设置阴影失败，不使用阴影效果
            self.setGraphicsEffect(None)
            # 确保透明背景被启用
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    
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
    
    def closeEvent(self, event):
        self.mask.hide()
        super().closeEvent(event)
    
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
    
    def reject(self):
        self.mask.hide()
        super().reject()
    
    def accept(self):
        self.mask.hide()
        super().accept()
    
    def _get_base_style(self):
        # 获取当前主题
        theme = theme_manager.get_current_theme()
        
        # 返回基础对话框样式
        return f"""
            QDialog {{
                background-color: {theme['card_background']};
            }}
            #dialog-container {{
                background-color: {theme['card_background']};
                border-radius: {theme['border_radius']};
                border: 1px solid rgba(0, 0, 0, 0.1);
            }}
            #dialog-title {{
                font-size: 20px;
                font-weight: bold;
                color: {theme['text_color']};
                margin-bottom: 10px;
            }}
            QLabel {{
                color: {theme['text_color']};
                font-size: 14px;
            }}
            #input-field {{
                padding: 10px;
                border: 1px solid {theme['menu_border']};
                border-radius: 8px;
                background-color: {theme['background_color']};
                min-height: 20px;
                color: {theme['text_color']};
            }}
            #input-field:focus {{
                border: 1px solid {theme['primary_color']};
                background-color: {theme['card_background']};
            }}
            #ok-btn {{
                background-color: {theme['primary_color']};
                color: {theme['light_text_color']};
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 80px;
            }}
            #ok-btn:hover {{
                background-color: {theme['secondary_color']};
            }}
            #ok-btn:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
            #cancel-btn {{
                background-color: {theme['background_color']};
                color: {theme['text_color']};
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                min-width: 80px;
            }}
            #cancel-btn:hover {{
                background-color: {theme['hover_color']};
            }}
            #close-btn {{
                background-color: {theme['card_background']};
                border: none;
                padding: 5px;
                border-radius: 4px;
            }}
            #close-btn:hover {{
                background-color: {theme['hover_color']};
            }}
            #dialog-message {{
                font-size: 14px;
                color: {theme['text_color']};
                margin-top: 10px;
                margin-bottom: 20px;
            }}
            #confirm-btn {{
                background-color: #ff4d4f;
                color: {theme['light_text_color']};
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 80px;
            }}
            #confirm-btn:hover {{
                background-color: #ff7875;
            }}
        """
        
    def _get_message_box_style(self):
        # 返回统一的QMessageBox样式
        return """
            QMessageBox {{
                background-color: white;
                padding-left: 5px;
            }}
            QMessageBox QLabel {{
                color: #333333;
                min-width: 300px;
                text-align: center;
                margin: 0;
                padding: 0;
            }}
            QMessageBox QPushButton {{
                background-color: #f0f0f0;
                color: #333333;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            /* 减少 QMessageBox 的左侧空白 */
            QMessageBox QIcon {{
                padding: 0;
                margin: 0;
            }}
            QMessageBox {{
                padding-left: 5px;
            }}
            QMessageBox QLayout {
                margin-left: 5px;
            }
        """
