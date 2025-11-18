import json
import os

def load_config(config_path='config.json'):
    """加载配置文件"""
    if not os.path.exists(config_path):
        # 如果配置文件不存在，创建默认配置
        default_config = {
            "image_directories": [
                "F:\\picture"
            ],
            "database_path": "images.db",
            "valid_extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".jfif"]
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        print(f"已创建默认配置文件: {config_path}")
        return default_config
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)