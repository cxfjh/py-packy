import os
import sys
import zipfile
import subprocess
from PySide6.QtCore import Signal, QThread


class PackageWorker(QThread):
    """
    执行打包命令的工作线程

    Signals:
        log_signal: 发送日志文本信号，用于更新界面日志显示
    """

    log_signal = Signal(str)

    def __init__(self, cmd_list):
        """
        初始化打包工作线程
        
        Args:
            cmd_list: Nuitka 打包命令参数列表
        """
        super().__init__()
        self.cmd_list = cmd_list

    def run(self):
        """执行打包命令"""
        try:
            # 清理命令参数中的引号
            clean_cmd = [arg.strip('"\'') for arg in self.cmd_list]
            self.log_signal.emit(f"执行命令: {' '.join(clean_cmd)}")

            # 配置 subprocess.Popen 参数
            popen_kwargs = {
                'stdin': subprocess.PIPE,
                'stdout': subprocess.PIPE,
                'stderr': subprocess.STDOUT,
                'text': True,
                'shell': False,
                'cwd': os.getcwd(),
            }

            # Windows 平台：创建无窗口进程
            if sys.platform == "win32":
                popen_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

            # 启动子进程
            process = subprocess.Popen(clean_cmd, **popen_kwargs)

            # 自动应答交互式提示
            process.stdin.write("Yes\n")
            process.stdin.flush()

            # 实时读取并发送输出日志
            while process.poll() is None:
                output = process.stdout.readline()
                if output:
                    self.log_signal.emit(output.strip())

            # 读取剩余输出
            remaining = process.stdout.read()
            if remaining:
                self.log_signal.emit(remaining.strip())

            # 关闭 stdin
            process.stdin.close()

            # 发送完成信息
            self.log_signal.emit(f"\n打包完成，返回代码: {process.returncode}")
        except FileNotFoundError:
            self.log_signal.emit("系统找不到指定的文件。请检查 Python 环境路径是否正确。")
        except Exception as e:
            self.log_signal.emit(f"打包错误: {str(e)}")


class UnzipWorker(QThread):
    """
    解压 ZIP 文件的工作线程

    Signals:
        progress_signal: 发送进度信号 (进度百分比, 当前文件名)
        finish_signal: 发送完成信号 (是否成功, 消息)
    """
    progress_signal = Signal(float, str)
    finish_signal = Signal(bool, str)

    def __init__(self, zip_path, target_dir):
        """
        初始化解压工作线程
        
        Args:
            zip_path: ZIP 文件路径
            target_dir: 解压目标目录
        """
        super().__init__()
        self.zip_path = zip_path
        self.target_dir = target_dir

    def run(self):
        """执行解压操作"""
        try:
            # 检查 ZIP 文件是否存在
            if not os.path.exists(self.zip_path):
                self.finish_signal.emit(False, "ZIP 文件不存在")
                return

            # 打开并解压 ZIP 文件
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                files = zip_ref.namelist()
                total = len(files)
                success = 0

                # 逐个解压文件
                for file_path in files:
                    # 检查是否请求中断
                    if self.isInterruptionRequested():
                        self.finish_signal.emit(False, "用户取消了解压")
                        return

                    # 解压单个文件
                    zip_ref.extract(file_path, self.target_dir)
                    success += 1

                    # 发送进度信号
                    progress = (success / total) * 100
                    file_name = os.path.basename(file_path)
                    self.progress_signal.emit(progress, file_name)

            # 验证解压完整性：检查 GCC 编译器目录
            gcc_dir = os.path.join(self.target_dir, "Nuitka", "Cache", "downloads", "gcc")
            if not os.path.exists(gcc_dir) or not os.listdir(gcc_dir):
                self.finish_signal.emit(False, "解压文件不完整，未找到 GCC 编译器目录")
                return

            # 解压成功
            self.finish_signal.emit(True, "解压成功")
        except Exception as e:
            # 处理异常
            self.finish_signal.emit(False, f"解压失败: {str(e)}")


class InstallWorker(QThread):
    """
    安装 Nuitka 的工作线程

    Signals:
        log_signal: 发送日志文本信号
        finish_signal: 发送完成信号 (是否成功, 消息)
    """
    log_signal = Signal(str)
    finish_signal = Signal(bool, str)

    def __init__(self, python_path):
        """
        初始化安装工作线程
        
        Args:
            python_path: Python 可执行文件路径
        """
        super().__init__()
        self.python_path = python_path

    def run(self):
        """执行 Nuitka 安装操作"""
        try:
            # 检查 Nuitka 是否已安装
            self.log_signal.emit("检查 Nuitka 是否已安装...")
            check_cmd = [self.python_path, "-m", "nuitka", "--version"]
            
            check_result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if check_result.returncode == 0:
                # Nuitka 已安装
                self.log_signal.emit("Nuitka 已安装，无需重复安装")
                self.finish_signal.emit(True, "Nuitka 已安装")
                return

            # Nuitka 未安装，开始安装
            self.log_signal.emit("Nuitka 未安装，开始安装...")
            install_cmd = [
                self.python_path, "-m", "pip", "install", "nuitka",
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
            ]

            self.log_signal.emit(f"执行命令: {' '.join(install_cmd)}")

            # 执行安装命令
            install_result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # 发送安装输出日志
            if install_result.stdout:
                for line in install_result.stdout.split('\n'):
                    if line.strip():
                        self.log_signal.emit(line.strip())

            # 检查安装结果
            if install_result.returncode == 0:
                self.log_signal.emit("Nuitka 安装成功")
                self.finish_signal.emit(True, "Nuitka 安装成功")
            else:
                self.log_signal.emit("Nuitka 安装失败")
                if install_result.stderr:
                    self.log_signal.emit(install_result.stderr)
                self.finish_signal.emit(False, "Nuitka 安装失败")

        except Exception as e:
            # 处理异常
            self.log_signal.emit(f"安装过程出错: {str(e)}")
            self.finish_signal.emit(False, f"安装失败: {str(e)}")