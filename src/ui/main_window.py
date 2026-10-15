import os
import time
import shutil
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCheckBox, QLineEdit, QFileDialog, QTextEdit,
    QFormLayout, QSpinBox, QScrollArea, QListWidget, QMessageBox, QLabel
)

from src.utils.helpers import get_python_paths, get_resource_path
from src.core.config import ConfigManager
from src.core.workers import PackageWorker, UnzipWorker, InstallWorker
from src.core.persistence import ConfigPersistence
from src.ui.builder import UIBuilder


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        # 初始化核心组件
        self.import_config_btn = None
        self.save_config_btn = None
        self.export_config_btn = None
        self.config = ConfigManager()
        self.ui = UIBuilder()
        self.persistence = ConfigPersistence()

        # 工作线程引用
        self.install_thread = None
        self.pack_thread = None
        self.unzip_thread = None

        # 路径变量
        self.main_file = ""
        self.icon_file = ""
        self.folders = []
        self.files = []

        # UI 控件引用 - 基本设置
        self.main_edit = None
        self.icon_edit = None
        self.py_env_edit = None
        self.output_edit = None
        self.temp_edit = None
        self.log_edit = None

        # UI 控件引用 - 配置分组
        self.plugin_group = None
        self.mode_group = None
        self.py_flag_group = None
        self.exclude_group = None

        # UI 控件引用 - 自定义插件
        self.custom_plugin_name_edit = None
        self.custom_plugin_param_edit = None
        self.custom_plugin_list = None

        # UI 控件引用 - 文件列表
        self.folder_list = None
        self.file_list = None

        # UI 控件引用 - 编译选项
        self.use_mingw = None
        self.use_lto = None
        self.jobs_spin = None

        # UI 控件引用 - 版本信息
        self.product_name_edit = None
        self.file_ver_edit = None
        self.product_ver_edit = None
        self.file_desc_edit = None
        self.copyright_edit = None
        self.trademark_edit = None

        # UI 控件引用 - 按钮
        self.generate_btn = None
        self.run_btn = None
        self.init_btn = None

        # 初始化界面
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 设置窗口基本属性
        self.setWindowTitle("PyPacky")
        self.setGeometry(100, 100, 750, 800)

        # 设置窗口图标
        logo_path = get_resource_path(r"static/logo.ico")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # 启用拖拽支持
        self.setAcceptDrops(True)
        self.setFont(QFont("Microsoft YaHei", 10))

        # 创建中心窗口
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # 创建滚动区域（容纳所有配置选项）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 创建各个配置区域
        self.create_settings(scroll_layout)  # 基本设置
        self.create_plugins(scroll_layout)  # 插件设置
        self.create_custom_plugins(scroll_layout)  # 自定义插件
        self.create_modes(scroll_layout)  # 打包模式
        self.create_folder_section(scroll_layout)  # 文件夹打包
        self.create_file_section(scroll_layout)  # 文件打包
        self.create_compile_options(scroll_layout)  # 编译选项
        self.create_py_flags(scroll_layout)  # Python 标志
        self.create_excludes(scroll_layout)  # 排除设置
        self.create_version_info(scroll_layout)  # 版本信息

        scroll_layout.addStretch()  # 添加弹性空间

        # 创建按钮区域（在滚动区域外）
        self.create_buttons(main_layout)

        # 创建日志显示区域
        self.create_log_section(main_layout)

        # 创建页脚信息
        self.create_footer(main_layout)

        # 加载上次保存的配置
        self.load_saved_config()

    def create_settings(self, layout):
        """
        创建基本设置区域
        
        Args:
            layout: 父布局，用于添加分组框
        """
        group = self.ui.create_group("基本设置")
        form = QFormLayout()

        # 创建文件输入控件
        self.main_edit, main_btn = self.ui.create_file_input("主 Python 文件", self.select_main_file)
        self.icon_edit, icon_btn = self.ui.create_file_input("图标文件 (.ico)", self.select_icon_file)
        self.py_env_edit, env_btn = self.ui.create_file_input("Python 环境", self.select_python_env)

        # 自动检测 Python 路径
        paths = get_python_paths()
        if paths:
            self.py_env_edit.setText(paths[0])

        # 创建其他输入控件
        self.output_edit = QLineEdit("app.exe")
        self.temp_edit = QLineEdit()

        # 自动生成临时目录按钮
        gen_temp_btn = QPushButton("自动生成")
        gen_temp_btn.clicked.connect(self.gen_temp_dir)

        # 添加到表单布局
        form.addRow("主文件:", self.ui.hbox_wrap([self.main_edit, main_btn]))
        form.addRow("ICO 图标:", self.ui.hbox_wrap([self.icon_edit, icon_btn]))
        form.addRow("输出文件名:", self.output_edit)
        form.addRow("临时目录:", self.ui.hbox_wrap([self.temp_edit, gen_temp_btn]))
        form.addRow("Python 环境:", self.ui.hbox_wrap([self.py_env_edit, env_btn]))

        group.setLayout(form)
        layout.addWidget(group)

    def create_plugins(self, layout):
        """
        创建插件设置区域
        
        Args:
            layout: 父布局
        """
        items = [
            ("Tkinter 支持", False),
            ("PySide6 支持", False),
            ("PyQt6 支持", False),
            ("Numpy 支持", False),
            ("Pandas 支持", False),
            ("Matplotlib 支持", False),
            ("Django 支持", False),
            ("Multiprocessing 支持", False),
        ]
        self.plugin_group = self.ui.create_check_group("启用插件", items, self.config.plugins)
        layout.addWidget(self.plugin_group)

    def create_modes(self, layout):
        """
        创建打包模式区域
        
        Args:
            layout: 父布局
        """
        items = [
            ("独立运行", True),
            ("单文件 EXE", True),
            ("减少体积", True),
            ("移除临时文件", True),
            ("禁用控制台", False),
            ("管理员权限", False),
            ("远程桌面访问", False),
        ]
        self.mode_group = self.ui.create_check_group("打包模式", items, self.config.modes)
        layout.addWidget(self.mode_group)

    def create_folder_section(self, layout):
        """
        创建文件夹打包区域

        Args:
            layout: 父布局
        """
        group = self.ui.create_group("打包文件夹")
        vbox = QVBoxLayout()

        self.folder_list = QListWidget()
        add_btn = QPushButton("添加文件夹")
        remove_btn = QPushButton("移除选中")

        add_btn.clicked.connect(self.add_folder)
        remove_btn.clicked.connect(self.remove_folder)

        vbox.addWidget(self.folder_list)
        vbox.addWidget(add_btn)
        vbox.addWidget(remove_btn)
        group.setLayout(vbox)
        layout.addWidget(group)

    def create_file_section(self, layout):
        """
        创建文件打包区域

        Args:
            layout: 父布局
        """
        group = self.ui.create_group("打包文件")
        vbox = QVBoxLayout()

        self.file_list = QListWidget()
        add_btn = QPushButton("添加文件")
        remove_btn = QPushButton("移除选中")

        add_btn.clicked.connect(self.add_file)
        remove_btn.clicked.connect(self.remove_file)

        vbox.addWidget(self.file_list)
        vbox.addWidget(add_btn)
        vbox.addWidget(remove_btn)
        group.setLayout(vbox)
        layout.addWidget(group)

    def create_compile_options(self, layout):
        """
        创建编译选项区域

        Args:
            layout: 父布局
        """
        group = self.ui.create_group("编译选项")
        form = QFormLayout()

        self.use_mingw = QCheckBox("使用 Mingw 编译器")
        self.use_mingw.setChecked(False)

        self.use_lto = QCheckBox("启用 LTO (链接时优化)")
        self.use_lto.setChecked(True)

        self.jobs_spin = QSpinBox()
        self.jobs_spin.setRange(1, os.cpu_count() or 4)
        self.jobs_spin.setValue(min(12, os.cpu_count() or 4))

        form.addRow(self.use_mingw)
        form.addRow(self.use_lto)
        form.addRow("并行任务数:", self.jobs_spin)
        group.setLayout(form)
        layout.addWidget(group)

    def create_py_flags(self, layout):
        """
        创建 Python 标志区域

        Args:
            layout: 父布局
        """
        items = [("禁用断言", False), ("静态哈希", False)]
        self.py_flag_group = self.ui.create_check_group("Python 标志", items, self.config.py_flags)
        layout.addWidget(self.py_flag_group)

    def create_excludes(self, layout):
        """
        创建排除设置区域

        Args:
            layout: 父布局
        """
        items = [
            ("排除 setuptools", False),
            ("排除 pydoc", False),
            ("排除 IPython", False),
        ]
        self.exclude_group = self.ui.create_check_group("排除设置", items, self.config.excludes)
        layout.addWidget(self.exclude_group)

    def create_version_info(self, layout):
        """
        创建版本信息区域

        Args:
            layout: 父布局
        """
        group = self.ui.create_group("版本信息")
        form = QFormLayout()

        self.product_name_edit = QLineEdit()
        self.product_name_edit.setPlaceholderText("PyPacky")

        self.file_ver_edit = QLineEdit()
        self.file_ver_edit.setPlaceholderText("0.1.0")

        self.product_ver_edit = QLineEdit()
        self.product_ver_edit.setPlaceholderText("0.1.0")

        self.file_desc_edit = QLineEdit()
        self.file_desc_edit.setPlaceholderText("Python 打包工具")

        self.copyright_edit = QLineEdit()
        self.copyright_edit.setPlaceholderText("2025 PyPacky. All rights reserved.")

        self.trademark_edit = QLineEdit()
        self.trademark_edit.setPlaceholderText("PyPacky is a trademark of cxfjh.")

        form.addRow("产品名称:", self.product_name_edit)
        form.addRow("文件版本:", self.file_ver_edit)
        form.addRow("产品版本:", self.product_ver_edit)
        form.addRow("文件描述:", self.file_desc_edit)
        form.addRow("版权信息:", self.copyright_edit)
        form.addRow("商标信息:", self.trademark_edit)

        group.setLayout(form)
        layout.addWidget(group)

    def create_buttons(self, layout):
        """
        创建按钮区域

        Args:
            layout: 父布局
        """
        hbox = QHBoxLayout()

        hbox.addStretch()  # 左侧弹性空间

        # 配置管理按钮
        self.save_config_btn = QPushButton("保存配置")
        self.export_config_btn = QPushButton("导出配置")
        self.import_config_btn = QPushButton("导入配置")

        hbox.addWidget(self.save_config_btn)
        hbox.addWidget(self.export_config_btn)
        hbox.addWidget(self.import_config_btn)

        # 主要操作按钮
        self.generate_btn = QPushButton("生成命令")
        self.run_btn = QPushButton("执行打包")
        self.init_btn = QPushButton("配置环境")

        hbox.addWidget(self.generate_btn)
        hbox.addWidget(self.run_btn)
        hbox.addWidget(self.init_btn)

        hbox.addStretch()  # 右侧弹性空间

        layout.addLayout(hbox)

        # 绑定按钮点击事件
        self.generate_btn.clicked.connect(self.gen_cmd)
        self.run_btn.clicked.connect(self.run_package)
        self.init_btn.clicked.connect(self.init_env)
        self.save_config_btn.clicked.connect(self.save_config)
        self.export_config_btn.clicked.connect(self.export_config)
        self.import_config_btn.clicked.connect(self.import_config)

    def create_log_section(self, layout):
        """
        创建日志显示区域
        
        Args:
            layout: 父布局
        """
        group = self.ui.create_group("打包日志")
        vbox = QVBoxLayout()

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("Consolas", 10))
        self.log_edit.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; padding: 6px;")
        self.log_edit.append("提示：可以将 .py 文件或 .ico 文件直接拖拽到窗口中")
        self.log_edit.append("提示：也可以拖拽其他文件到窗口中，它们会被添加到打包列表")

        vbox.addWidget(self.log_edit)
        group.setLayout(vbox)
        group.setMinimumHeight(220)
        layout.addWidget(group)

    def create_custom_plugins(self, layout):
        """
        创建自定义插件区域

        Args:
            layout: 父布局
        """
        group = self.ui.create_group("自定义插件")
        vbox = QVBoxLayout()

        # 输入行：名称 + 参数
        hbox_input = QHBoxLayout()
        self.custom_plugin_name_edit = QLineEdit()
        self.custom_plugin_name_edit.setPlaceholderText("插件名称")
        self.custom_plugin_param_edit = QLineEdit()
        self.custom_plugin_param_edit.setPlaceholderText("pyqt6")
        add_custom_btn = QPushButton("添加插件")
        add_custom_btn.clicked.connect(self.add_custom_plugin)

        hbox_input.addWidget(QLabel("名称："))
        hbox_input.addWidget(self.custom_plugin_name_edit)
        hbox_input.addWidget(QLabel("参数："))
        hbox_input.addWidget(self.custom_plugin_param_edit)
        hbox_input.addWidget(add_custom_btn)

        # 插件列表
        self.custom_plugin_list = QListWidget()
        remove_custom_btn = QPushButton("移除选中插件")
        remove_custom_btn.clicked.connect(self.remove_custom_plugin)

        vbox.addLayout(hbox_input)
        vbox.addWidget(self.custom_plugin_list)
        vbox.addWidget(remove_custom_btn)
        group.setLayout(vbox)
        layout.addWidget(group)

    @staticmethod
    def create_footer(layout):
        """
        创建页脚信息
        
        Args:
            layout: 父布局
        """
        label = QLabel()
        url = "https://github.com/cxfjh/PyPacky"
        label.setText(
            f'<span style="font-size: 9pt;">当前版本: v0.1.0</span>'
            f'<br><span style="font-size: 9pt;">联系作者: 2449579731@qq.com</span><br>'
            f'<span style="font-size: 9pt;">开源仓库: </span>'
            f'<a href="{url}" style="font-size: 9pt; color: #1a73e8; text-decoration: underline;">{url}</a>',
        )
        label.setOpenExternalLinks(True)
        label.setStyleSheet("margin: 8px 12px 8px 0;")
        layout.addWidget(label)

    def dragEnterEvent(self, event):
        """
        拖拽进入事件处理

        Args:
            event: 拖拽事件对象
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """
        拖拽释放事件处理
        
        Args:
            event: 拖拽事件对象
        """
        for url in event.mimeData().urls():
            path = url.toLocalFile()

            if path.endswith(".py"):
                # Python 文件：设置为主文件
                self.main_file = path
                self.main_edit.setText(path)
                self.log_edit.append(f"已拖入主文件: {path}")
            elif path.endswith(".ico"):
                # 图标文件：设置为图标
                self.icon_file = path
                self.icon_edit.setText(path)
                self.log_edit.append(f"已拖入图标文件: {path}")
            else:
                # 其他文件：添加到打包列表
                if path not in self.files:
                    self.files.append(path)
                    self.file_list.addItem(os.path.basename(path))
                    self.log_edit.append(f"已添加打包文件: {os.path.basename(path)}")
                else:
                    self.log_edit.append(f"文件已存在: {os.path.basename(path)}")

    def select_main_file(self):
        """选择主文件"""
        path, _ = QFileDialog.getOpenFileName(self, "选择主 Python 文件", "", "Python Files (*.py)")
        if path:
            self.main_file = path
            self.main_edit.setText(path)

    def select_icon_file(self):
        """选择图标文件"""
        path, _ = QFileDialog.getOpenFileName(self, "选择图标文件", "", "Icon Files (*.ico)")
        if path:
            self.icon_file = path
            self.icon_edit.setText(path)

    def select_python_env(self):
        """选择 Python 环境"""
        path, _ = QFileDialog.getOpenFileName(self, "选择 Python 环境", "", "Python Environments (*.exe)")
        if path:
            self.py_env_edit.setText(path)

    def add_folder(self):
        """添加文件夹"""
        path = QFileDialog.getExistingDirectory(self, "选择要打包的文件夹")
        if path and path not in self.folders:
            self.folders.append(path)
            self.folder_list.addItem(path)
        elif path:
            QMessageBox.information(self, "提示", "该文件夹已添加")

    def remove_folder(self):
        """移除选中的文件夹"""
        row = self.folder_list.currentRow()
        if row >= 0:
            item = self.folder_list.takeItem(row)
            self.folders.remove(item.text())

    def add_file(self):
        """添加文件"""
        path, _ = QFileDialog.getOpenFileName(self, "选择要打包的文件")
        if path and path not in self.files:
            self.files.append(path)
            self.file_list.addItem(os.path.basename(path))
        elif path:
            QMessageBox.information(self, "提示", "该文件已添加")

    def remove_file(self):
        """移除选中的文件"""
        row = self.file_list.currentRow()
        if row >= 0:
            self.file_list.takeItem(row)
            self.files.pop(row)

    def gen_temp_dir(self):
        """生成临时目录路径"""
        if not self.main_edit.text().strip():
            QMessageBox.warning(self, "提示", "请先选择主文件")
            return

        base_name = os.path.splitext(os.path.basename(self.main_edit.text().strip()))[0]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        new_dir = f"{{TEMP}}/{timestamp}_{base_name}"
        self.temp_edit.setText(new_dir)

    def init_env(self):
        """初始化环境"""
        QMessageBox.information(
            self,
            "提示",
            "请确保 PyPacky.exe 同级目录有 Nuitka.zip 环境包<br>"
            "<a href='https://github.com/cxfjh/PyPacky/releases/tag/v0.1.0'>Github 下载</a><br>"
            "<a href='https://www.123865.com/s/IzrNjv-lfA7A'>123 云盘下载</a><br>",
            QMessageBox.StandardButton.Ok,
        )

        # 检查 ZIP 包是否存在
        zip_path = "Nuitka.zip"
        if not os.path.exists(zip_path):
            QMessageBox.critical(self, "错误", "Nuitka.zip 环境包不存在")
            return

        # 准备目标路径
        user_home = os.path.expanduser("~")
        target_dir = os.path.join(user_home, "AppData", "Local", "Nuitka")
        self.log_edit.append(f"解压目标目录：{target_dir}")

        # 处理已存在目录
        if os.path.exists(target_dir):
            reply = QMessageBox.question(
                self,
                "目录已存在",
                f"目标目录 {target_dir} 已存在，是否覆盖？\n（覆盖会删除原有文件）",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                QMessageBox.information(self, "取消", "解压已取消")
                return
            shutil.rmtree(target_dir, ignore_errors=True)

        os.makedirs(target_dir, exist_ok=True)
        self.set_buttons(False)

        # 启动解压线程
        self.unzip_thread = UnzipWorker(zip_path, target_dir)
        self.unzip_thread.progress_signal.connect(self.on_unzip_progress)
        self.unzip_thread.finish_signal.connect(self.on_unzip_finish)

        self.log_edit.append("启动后台解压线程...")
        self.unzip_thread.start()

    def on_unzip_progress(self, progress, file_name):
        """
        更新解压进度

        Args:
            progress: 解压进度百分比
            file_name: 当前解压的文件名
        """
        if progress % 10 == 0 or progress == 100:
            self.log_edit.append(f"解压进度：{float(progress):.1f}% | 已解压：{file_name}")

    def on_unzip_finish(self, success, msg):
        """
        解压完成回调

        Args:
            success: 是否解压成功
            msg: 结果消息
        """
        self.set_buttons(True)

        if success:
            self.log_edit.append("Nuitka 环境包解压完成！")
            QMessageBox.information(self, "成功", "环境初始化完成，可开始打包！")
        else:
            self.log_edit.append(f"解压失败：{msg}")

            # 清理不完整的解压目录
            target_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Nuitka")
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, ignore_errors=True)
                self.log_edit.append("清理不完整解压目录")

            # 根据错误类型提供解决方案
            error_msg = f"解压失败：{msg}\n"
            if "权限" in msg:
                error_msg += "解决方案：右键以管理员身份运行 PyPacky.exe"
            elif "损坏" in msg:
                error_msg += "解决方案：重新下载 ZIP 格式环境包并验证完整性"
            else:
                error_msg += "解决方案：\n1. 以管理员身份运行 PyPacky\n2. 检查 Nuitka.zip 是否完整\n3. 手动解压到目标目录"

            QMessageBox.critical(self, "错误", error_msg)

    def run_package(self):
        """执行打包"""
        # 获取 Python 环境路径
        py_env = self.py_env_edit.text().strip() or "python"

        # 创建安装检查线程
        self.install_thread = InstallWorker(py_env)
        self.install_thread.log_signal.connect(self.update_log)
        self.install_thread.finish_signal.connect(self.on_install_finish)

        # 禁用按钮防止重复点击
        self.set_buttons(False)
        self.install_thread.start()

    def on_install_finish(self, success):
        """
        安装检查完成回调
        
        Args:
            success: Nuitka 是否已安装或安装成功
        """
        self.set_buttons(True)
        if success:
            self.continue_package()
        else:
            QMessageBox.critical(self, "错误", "Nuitka 未安装且安装失败")

    def continue_package(self):
        """继续打包"""
        cmd = self.gen_cmd()
        if not cmd:
            return

        self.log_edit.append("\n开始打包...\n")
        self.set_buttons(False)

        self.pack_thread = PackageWorker(cmd)
        self.pack_thread.log_signal.connect(self.update_log)
        self.pack_thread.finished.connect(self.on_package_finish)
        self.pack_thread.start()

    def on_package_finish(self):
        """打包完成回调"""
        self.log_edit.append("\n打包流程结束")
        self.set_buttons(True)

    def gen_cmd(self):
        """
        生成打包命令
        
        Returns:
            list: Nuitka 命令参数列表，如果主文件未选择则返回 None
        """
        # 检查主文件是否已选择
        if not self.main_edit.text().strip():
            self.log_edit.append("请先选择主 Python 文件")
            return None

        # 构建基础命令
        py_env = self.py_env_edit.text().strip()
        if py_env:
            cmd = [py_env, "-m", "nuitka"]
        else:
            cmd = ["python", "-m", "nuitka"]

        # 设置输出目录
        output_dir = os.path.dirname(self.main_edit.text().strip())
        cmd.append(f"--output-dir={output_dir}")

        # 添加内置插件参数
        for cb in self.plugin_group.findChildren(QCheckBox):
            if cb.isChecked() and cb.text() in self.config.plugins:
                cmd.append(f"--enable-plugin={self.config.plugins[cb.text()]['param']}")

        # 添加自定义插件参数
        for name, param in self.config.custom_plugins.items():
            cmd.append(f"--enable-plugin={param}")
            self.log_edit.append(f"启用自定义插件：{name} (--enable-plugin={param})")

        # 添加打包模式参数
        for cb in self.mode_group.findChildren(QCheckBox):
            if cb.isChecked() and cb.text() in self.config.modes:
                cmd.append(self.config.modes[cb.text()]["param"])

        # 添加图标参数
        if self.icon_edit.text().strip():
            cmd.append(f"--windows-icon-from-ico={self.icon_edit.text().strip()}")

        # 添加文件夹参数
        for folder in self.folders:
            folder_name = os.path.basename(folder)
            cmd.append(f"--include-data-dir={folder}={folder_name}")

        # 添加文件参数
        for file_path in self.files:
            file_name = os.path.basename(file_path)
            cmd.append(f"--include-data-files={file_path}={file_name}")

        # 添加编译选项参数
        if self.use_mingw.isChecked():
            cmd.append("--mingw64")
        if self.use_lto.isChecked():
            cmd.append("--lto=yes")
        cmd.append(f"--jobs={self.jobs_spin.value()}")

        # 添加 Python 标志参数
        for cb in self.py_flag_group.findChildren(QCheckBox):
            if cb.isChecked() and cb.text() in self.config.py_flags:
                cmd.append(self.config.py_flags[cb.text()]["param"])

        # 添加排除设置参数
        for cb in self.exclude_group.findChildren(QCheckBox):
            if cb.isChecked() and cb.text() in self.config.excludes:
                cmd.append(self.config.excludes[cb.text()]["param"])

        # 添加版本信息参数
        if self.product_name_edit.text().strip():
            cmd.append(f"--product-name={self.product_name_edit.text().strip()}")
        if self.file_ver_edit.text().strip():
            cmd.append(f"--file-version={self.file_ver_edit.text().strip()}")
        if self.product_ver_edit.text().strip():
            cmd.append(f"--product-version={self.product_ver_edit.text().strip()}")
        if self.file_desc_edit.text().strip():
            cmd.append(f"--file-description={self.file_desc_edit.text().strip()}")
        if self.copyright_edit.text().strip():
            cmd.append(f"--copyright={self.copyright_edit.text().strip()}")
        if self.trademark_edit.text().strip():
            cmd.append(f"--trademarks={self.trademark_edit.text().strip()}")

        # 添加临时目录参数
        temp_dir = self.temp_edit.text().strip()
        if temp_dir:
            cmd.append(f"--onefile-tempdir-spec={temp_dir}")

        # 添加输出文件名参数
        output_name = self.output_edit.text().strip()
        if output_name:
            cmd.append(f"--output-filename={output_name}")

        # 添加主文件路径
        cmd.append(self.main_edit.text().strip())

        # 显示生成的命令
        cmd_str = " ".join(cmd)
        self.log_edit.clear()
        self.log_edit.append("生成的打包命令:\n")
        self.log_edit.append(cmd_str)

        return cmd

    def add_custom_plugin(self):
        """添加自定义插件"""
        name = self.custom_plugin_name_edit.text().strip()
        param = self.custom_plugin_param_edit.text().strip()

        if not name or not param:
            QMessageBox.warning(self, "提示", "插件名称和参数不能为空！")
            return

        if name in self.config.custom_plugins:
            QMessageBox.warning(self, "提示", "该插件名称已存在！")
            return

        # 存储自定义插件
        self.config.custom_plugins[name] = param

        # 添加到列表显示
        self.custom_plugin_list.addItem(f"{name} (--enable-plugin={param})")

        # 清空输入框
        self.custom_plugin_name_edit.clear()
        self.custom_plugin_param_edit.clear()
        self.log_edit.append(f"已添加自定义插件：{name} (参数：{param})")

    def remove_custom_plugin(self):
        """移除选中的自定义插件"""
        current_item = self.custom_plugin_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请选择要移除的插件！")
            return

        # 提取插件名称
        item_text = current_item.text()
        name = item_text.split(" (")[0]

        # 从配置中移除
        if name in self.config.custom_plugins:
            del self.config.custom_plugins[name]

        # 从列表中移除
        self.custom_plugin_list.takeItem(self.custom_plugin_list.currentRow())
        self.log_edit.append(f"已移除自定义插件：{name}")

    def update_log(self, text):
        """
        更新日志显示
        
        Args:
            text: 要显示的日志文本
        """
        self.log_edit.append(text.strip())

    def set_buttons(self, enabled):
        """
        设置按钮可用状态
        
        Args:
            enabled: True 启用按钮，False 禁用按钮
        """
        self.run_btn.setEnabled(enabled)
        self.generate_btn.setEnabled(enabled)
        self.init_btn.setEnabled(enabled)

    def collect_config_data(self):
        """
        收集当前界面配置数据
        
        Returns:
            dict: 完整的配置数据字典
        """
        # 收集插件启用状态
        plugins = { }
        for cb in self.plugin_group.findChildren(QCheckBox):
            if cb.text() in self.config.plugins:
                plugins[cb.text()] = cb.isChecked()

        # 收集打包模式状态
        modes = { }
        for cb in self.mode_group.findChildren(QCheckBox):
            if cb.text() in self.config.modes:
                modes[cb.text()] = cb.isChecked()

        # 收集 Python 标志状态
        py_flags = { }
        for cb in self.py_flag_group.findChildren(QCheckBox):
            if cb.text() in self.config.py_flags:
                py_flags[cb.text()] = cb.isChecked()

        # 收集排除设置状态
        excludes = { }
        for cb in self.exclude_group.findChildren(QCheckBox):
            if cb.text() in self.config.excludes:
                excludes[cb.text()] = cb.isChecked()

        # 收集文件夹列表
        folders = []
        for i in range(self.folder_list.count()):
            folders.append(self.folder_list.item(i).text())

        # 收集文件列表
        files = []
        for i in range(self.file_list.count()):
            files.append(self.files[i])

        # 收集自定义插件
        custom_plugins = dict(self.config.custom_plugins)

        # 组装完整配置数据
        config_data = {
            "main_file": self.main_edit.text().strip(),
            "icon_file": self.icon_edit.text().strip(),
            "python_env": self.py_env_edit.text().strip(),
            "output_filename": self.output_edit.text().strip(),
            "temp_dir": self.temp_edit.text().strip(),
            "plugins": plugins,
            "modes": modes,
            "py_flags": py_flags,
            "excludes": excludes,
            "folders": folders,
            "files": files,
            "custom_plugins": custom_plugins,
            "use_mingw": self.use_mingw.isChecked(),
            "use_lto": self.use_lto.isChecked(),
            "jobs": self.jobs_spin.value(),
            "version_info": {
                "product_name": self.product_name_edit.text().strip(),
                "file_version": self.file_ver_edit.text().strip(),
                "product_version": self.product_ver_edit.text().strip(),
                "file_description": self.file_desc_edit.text().strip(),
                "copyright": self.copyright_edit.text().strip(),
                "trademarks": self.trademark_edit.text().strip(),
            },
        }

        return config_data

    def apply_config_data(self, config_data):
        """应用配置数据到界面
        
        将配置字典中的数据应用到对应的 UI 控件，
        恢复用户之前的配置选择。
        
        Args:
            config_data: 配置数据字典
        """
        # 应用基本设置
        if "main_file" in config_data and config_data["main_file"]:
            self.main_edit.setText(config_data["main_file"])
            self.main_file = config_data["main_file"]

        if "icon_file" in config_data and config_data["icon_file"]:
            self.icon_edit.setText(config_data["icon_file"])
            self.icon_file = config_data["icon_file"]

        if "python_env" in config_data and config_data["python_env"]:
            self.py_env_edit.setText(config_data["python_env"])

        if "output_filename" in config_data:
            self.output_edit.setText(config_data["output_filename"])

        if "temp_dir" in config_data:
            self.temp_edit.setText(config_data["temp_dir"])

        # 应用插件状态
        if "plugins" in config_data:
            for cb in self.plugin_group.findChildren(QCheckBox):
                if cb.text() in config_data["plugins"]:
                    cb.setChecked(config_data["plugins"][cb.text()])

        # 应用模式状态
        if "modes" in config_data:
            for cb in self.mode_group.findChildren(QCheckBox):
                if cb.text() in config_data["modes"]:
                    cb.setChecked(config_data["modes"][cb.text()])

        # 应用 Python 标志状态
        if "py_flags" in config_data:
            for cb in self.py_flag_group.findChildren(QCheckBox):
                if cb.text() in config_data["py_flags"]:
                    cb.setChecked(config_data["py_flags"][cb.text()])

        # 应用排除设置状态
        if "excludes" in config_data:
            for cb in self.exclude_group.findChildren(QCheckBox):
                if cb.text() in config_data["excludes"]:
                    cb.setChecked(config_data["excludes"][cb.text()])

        # 应用文件夹列表（只添加存在的路径）
        if "folders" in config_data:
            self.folder_list.clear()
            self.folders.clear()
            for folder in config_data["folders"]:
                if os.path.exists(folder):
                    self.folders.append(folder)
                    self.folder_list.addItem(folder)

        # 应用文件列表（只添加存在的路径）
        if "files" in config_data:
            self.file_list.clear()
            self.files.clear()
            for file_path in config_data["files"]:
                if os.path.exists(file_path):
                    self.files.append(file_path)
                    self.file_list.addItem(os.path.basename(file_path))

        # 应用自定义插件
        if "custom_plugins" in config_data:
            self.custom_plugin_list.clear()
            self.config.custom_plugins.clear()
            for name, param in config_data["custom_plugins"].items():
                self.config.custom_plugins[name] = param
                self.custom_plugin_list.addItem(f"{name} (--enable-plugin={param})")

        # 应用编译选项
        if "use_mingw" in config_data:
            self.use_mingw.setChecked(config_data["use_mingw"])

        if "use_lto" in config_data:
            self.use_lto.setChecked(config_data["use_lto"])

        if "jobs" in config_data:
            self.jobs_spin.setValue(config_data["jobs"])

        # 应用版本信息
        if "version_info" in config_data:
            vi = config_data["version_info"]
            if "product_name" in vi:
                self.product_name_edit.setText(vi["product_name"])
            if "file_version" in vi:
                self.file_ver_edit.setText(vi["file_version"])
            if "product_version" in vi:
                self.product_ver_edit.setText(vi["product_version"])
            if "file_description" in vi:
                self.file_desc_edit.setText(vi["file_description"])
            if "copyright" in vi:
                self.copyright_edit.setText(vi["copyright"])
            if "trademarks" in vi:
                self.trademark_edit.setText(vi["trademarks"])

    def save_config(self):
        """保存配置到默认配置文件"""
        config_data = self.collect_config_data()
        if self.persistence.save_config(config_data):
            self.log_edit.append("配置已保存")
            QMessageBox.information(self, "成功", "配置已保存")
        else:
            QMessageBox.critical(self, "错误", "配置保存失败")

    def export_config(self):
        """导出配置到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出配置",
            "",
            "JSON 配置文件 (*.json)",
        )

        if not file_path:
            return

        config_data = self.collect_config_data()
        success, message = self.persistence.export_config(file_path, config_data)

        if success:
            self.log_edit.append(f"配置已导出到: {file_path}")
            QMessageBox.information(self, "成功", f"配置已导出到:\n{file_path}")
        else:
            QMessageBox.critical(self, "错误", message)

    def import_config(self):
        """从文件导入配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入配置",
            "",
            "JSON 配置文件 (*.json)",
        )

        if not file_path:
            return

        success, data, message = self.persistence.import_config(file_path)

        if success:
            self.apply_config_data(data)
            self.log_edit.append(f"配置已从 {file_path} 导入")
            QMessageBox.information(self, "成功", "配置导入成功")
        else:
            QMessageBox.critical(self, "错误", message)

    def load_saved_config(self):
        """加载保存的配置"""
        config_data = self.persistence.load_config()
        if config_data:
            self.apply_config_data(config_data)
            self.log_edit.append("已加载上次保存的配置")