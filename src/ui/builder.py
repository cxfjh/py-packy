from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QWidget,
    QLineEdit, QPushButton, QCheckBox
)


class UIBuilder:
    """UI 构建工具类"""

    @staticmethod
    def create_group(title):
        """
        创建分组框

        Args:
            title: 分组框标题
            
        Returns:
            QGroupBox: 创建的分组框控件
        """
        group = QGroupBox(title)

        # 设置标题加粗样式
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        return group

    @staticmethod
    def hbox_wrap(widgets):
        """
        将多个控件包装到水平布局
        
        Args:
            widgets: 要添加到布局中的控件列表
            
        Returns:
            QWidget: 包含水平布局的容器控件
        """
        hbox = QHBoxLayout()

        for widget in widgets:
            hbox.addWidget(widget)

        hbox.setContentsMargins(0, 0, 0, 0)
        container = QWidget()
        container.setLayout(hbox)
        return container

    @staticmethod
    def create_file_input(label, callback):
        """
        创建文件输入控件
        
        Args:
            label: 控件的提示文本
            callback: 浏览按钮点击时的回调函数
            
        Returns:
            tuple: (QLineEdit, QPushButton) - 文本输入框和浏览按钮
        """
        edit = QLineEdit()
        edit.setToolTip(label)
        btn = QPushButton("浏览...")
        btn.clicked.connect(callback)
        return edit, btn

    @classmethod
    def create_check_group(cls, title, items, mapping):
        """
        创建复选框分组

        Args:
            title: 分组框标题
            items: 复选框项列表，格式为 [(文本, 是否选中), ...]
            mapping: 配置项映射字典，包含 param 和 tip 信息
            
        Returns:
            QGroupBox: 包含复选框的分组框
        """
        group = cls.create_group(title)
        layout = QVBoxLayout()

        # 创建并添加复选框
        for text, checked in items:
            cb = QCheckBox(text)
            cb.setChecked(checked)

            # 设置提示信息
            if text in mapping and "tip" in mapping[text]:
                cb.setToolTip(mapping[text]["tip"])
            layout.addWidget(cb)

        group.setLayout(layout)
        return group
