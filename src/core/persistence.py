import json
import os
from pathlib import Path


class ConfigPersistence:
    """配置的保存、加载、导入和导出"""

    def __init__(self, config_file=None):
        """初始化配置持久化
        
        Args:
            config_file: 配置文件路径，默认为用户目录下的 .py-packy/config.json
        """
        if config_file is None:
            # 使用默认配置文件路径
            config_dir = Path.home() / ".py-packy"
            config_dir.mkdir(exist_ok=True)
            self.config_file = config_dir / "config.json"
        else:
            # 使用指定的配置文件路径
            self.config_file = Path(config_file)

    def save_config(self, config_data):
        """
        保存配置到文件
        
        Args:
            config_data: 要保存的配置字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保配置目录存在
            self.config_file.parent.mkdir(exist_ok=True)

            # 写入配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            # 记录错误信息
            print(f"保存配置失败: {str(e)}")
            return False

    def load_config(self):
        """
        从文件加载配置
        
        Returns:
            dict: 配置数据，如果文件不存在或加载失败返回空字典
        """
        # 检查配置文件是否存在
        if not self.config_file.exists():
            return { }

        try:
            # 读取并解析配置文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            # 记录错误信息
            print(f"加载配置失败: {str(e)}")
            return { }

    @staticmethod
    def export_config(file_path, config_data):
        """
        导出配置到指定文件
        
        Args:
            file_path: 导出文件路径
            config_data: 要导出的配置字典
            
        Returns:
            tuple: (success: bool, message: str) - 成功标志和消息
        """
        try:
            # 写入导出文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True, "配置导出成功"
        except PermissionError:
            return False, "权限不足，无法写入文件"
        except Exception as e:
            return False, f"导出失败: {str(e)}"

    @staticmethod
    def import_config(file_path):
        """
        从指定文件导入配置

        Args:
            file_path: 导入文件路径
            
        Returns:
            tuple: (success: bool, data: dict or None, message: str) - 成功标志、配置数据和消息
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False, None, "配置文件不存在"

        try:
            # 读取并解析配置文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return True, data, "配置导入成功"
        except json.JSONDecodeError:
            return False, None, "配置文件格式错误"
        except Exception as e:
            return False, None, f"导入失败: {str(e)}"
