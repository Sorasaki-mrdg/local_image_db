import sqlite3
import os
from PIL import Image

from core.clip_feature import ClipFeatureEx
import core.db_config as db_config

def is_supported_image(file_path):
    # 检查文件扩展名是否为支持的格式
    supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.jfif']
    _, ext = os.path.splitext(file_path)
    return ext.lower() in supported_extensions

def main(db_path):
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    clipex = ClipFeatureEx(model_name="ViT-H-14", device=None, download_root='./')


    # 查询数据库中的所有图片路径
    cursor.execute("SELECT id, path, features FROM images")
    rows = cursor.fetchall()

    for row in rows:
        image_id, image_path, existing_features = row
        if is_supported_image(image_path):
            if existing_features is None:  # 检查features是否为空
                try:
                    # 预处理
                    image = Image.open(image_path).convert("RGB")
                    # 生成特征向量
                    features = clipex.generate_image_features(image)

                    # 将特征向量存储到数据库
                    cursor.execute("UPDATE images SET features = ? WHERE id = ?", (features.tobytes(), image_id))
                    conn.commit()
                    print(f"Updated features for image ID {image_id}")
                except Exception as e:
                    print(f"Error processing image ID {image_id}: {e}")
            else:
                print(f"Skipping image ID {image_id} as it already has features.")
        else:
            print(f"Skipping unsupported file format: {image_path}")

    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    # db_path = "images.db"  # 数据库文件路径
    config = db_config.load_config()
    db_path = config["database_path"]
    main(db_path)
