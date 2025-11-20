import sqlite3
import os
from PIL import Image

from core.clip_feature import ClipFeatureEx
import core.db_config as db_config
from core.database import DatabaseManager

def is_supported_image(file_path):
    # 检查文件扩展名是否为支持的格式
    supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.jfif']
    _, ext = os.path.splitext(file_path)
    return ext.lower() in supported_extensions

def main(db_path):
    # 连接到SQLite数据库
    image_db = DatabaseManager(db_path)
    image_db.connect()
    image_db.create_tables()
    
    # 初始化ClipFeatureEx
    clipex = ClipFeatureEx(model_name="ViT-H-14", device=None, download_root='./')


    # 查询数据库中的所有图片路径
    rows = image_db.execute_query("SELECT id, path, features FROM images")

    for row in rows:
        image_id, image_path, existing_features = row
        if not os.path.exists(image_path):
                print(f"文件不存在，跳过 ID {image_id}: {image_path}")
                continue
        if is_supported_image(image_path):
            if existing_features is None:  # 检查features是否为空
                try:
                    # 预处理
                    image = Image.open(image_path).convert("RGB")
                    # 生成特征向量
                    features = clipex.generate_image_features(image)

                    # 将特征向量存储到数据库
                    image_db.execute_query("UPDATE images SET features = ? WHERE id = ?", (features.tobytes(), image_id))
                    print(f"Updated features for image ID {image_id}")
                except Exception as e:
                    print(f"Error processing image ID {image_id}: {e}")
            else:
                print(f"Skipping image ID {image_id} as it already has features.")
        else:
            print(f"Skipping unsupported file format: {image_path}")

    # 关闭数据库连接
    image_db.close()

if __name__ == "__main__":
    # db_path = "images.db"  # 数据库文件路径
    config = db_config.load_config()
    db_path = config["database_path"]
    main(db_path)
