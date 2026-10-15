import os
import sys
import subprocess


def get_python_paths():
    """
    获取系统中可用的 Python 可执行文件路径列表

    Returns:
        list: Python 可执行文件路径列表，如果查找失败则返回空列表
    """
    try:
        # 执行 where 命令查找 Python 路径
        result = subprocess.run(
            ['where', 'python'],
            capture_output=True,
            text=True,
            encoding='gbk',
        )
        # 如果命令执行成功，返回路径列表
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
        return []
    except (FileNotFoundError, Exception):
        # 如果命令不存在或发生其他错误，返回空列表
        return []


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径

    Args:
        relative_path (str): 资源文件相对于项目根目录的路径
        
    Returns:
        str: 资源文件的绝对路径
    """
    # 检查是否由 PyInstaller 打包运行
    if getattr(sys, 'frozen', False):
        # 打包后运行，资源在临时目录中
        base_path = sys._MEIPASS
    else:
        # 开发环境运行，资源在项目根目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 拼接完整路径并返回
    return os.path.join(base_path, relative_path)
