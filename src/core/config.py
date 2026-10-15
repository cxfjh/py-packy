class ConfigManager:
    """管理打包的所有配置选项"""

    def __init__(self):
        # 插件配置：定义支持的第三方库插件
        self.plugins = {
            "Tkinter 支持": {
                "param": "tk-inter",
                "tip": "启用 Tkinter 插件",
            },
            "PySide6 支持": {
                "param": "pyside6",
                "tip": "启用 PySide6 插件",
            },
            "PyQt6 支持": {
                "param": "pyqt6",
                "tip": "启用 PyQt6 插件",
            },
            "Numpy 支持": {
                "param": "numpy",
                "tip": "Numpy 优化支持",
            },
            "Pandas 支持": {
                "param": "pandas",
                "tip": "Pandas 优化支持",
            },
            "Matplotlib 支持": {
                "param": "matplotlib",
                "tip": "Matplotlib 优化支持",
            },
            "Django 支持": {
                "param": "django",
                "tip": "Django 框架支持",
            },
            "Multiprocessing 支持": {
                "param": "multiprocessing",
                "tip": "多进程支持",
            },
        }

        # 自定义插件：用户可动态添加的插件
        self.custom_plugins = { }

        # 打包模式配置：定义不同的打包选项
        self.modes = {
            "独立运行": {
                "param": "--standalone",
                "tip": "打包所有依赖",
            },
            "单文件 EXE": {
                "param": "--onefile",
                "tip": "生成单文件 exe",
            },
            "减少体积": {
                "param": "--enable-plugin=anti-bloat",
                "tip": "移除不必要依赖",
            },
            "移除临时文件": {
                "param": "--remove-output",
                "tip": "清理中间文件",
            },
            "禁用控制台": {
                "param": "--windows-console-mode=disable",
                "tip": "隐藏控制台窗口",
            },
            "管理员权限": {
                "param": "--windows-uac-admin",
                "tip": "需要管理员权限运行",
            },
            "远程桌面访问": {
                "param": "--windows-uac-uiaccess",
                "tip": "远程桌面访问权限",
            },
        }

        # Python 标志配置：控制 Python 运行时行为
        self.py_flags = {
            "禁用断言": {
                "param": "--python-flag=no_asserts",
                "tip": "移除 assert 语句",
            },
            "静态哈希": {
                "param": "--python-flag=static_hashes",
                "tip": "使用静态哈希",
            },
        }

        # 排除项配置：指定打包时排除的模块
        self.excludes = {
            "排除 setuptools": {
                "param": "--noinclude-setuptools-mode=error",
                "tip": "排除 setuptools",
            },
            "排除 pydoc": {
                "param": "--noinclude-pydoc-mode=warning",
                "tip": "排除 pydoc",
            },
            "排除 IPython": {
                "param": "--noinclude-IPython-mode=error",
                "tip": "排除 IPython",
            },
        }
