import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    """应用程序入口函数"""
    # 创建 Qt 应用程序实例
    app = QApplication(sys.argv)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 启动应用程序事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
