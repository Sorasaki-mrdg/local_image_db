import sqlite3
import numpy as np
import os
from core.clip_feature import ClipFeatureEx
import core.clip_feature as clip_feature
import core.db_config as db_config
import core.search_count as search_count
from core.database import DatabaseManager


def main(db_path, how_many_results=5):
    # 连接到SQLite数据库
    image_db = DatabaseManager(db_path)
    image_db.connect()
    image_db.create_tables()

    clipex = ClipFeatureEx(model_name="ViT-H-14", device=None, download_root='./')

    # 查询数据库中的所有图片特征向量
    rows = image_db.execute_query("SELECT id, features FROM images")
    

    # 存储所有图片的特征向量
    all_image_features = []
    image_ids = []
    for row in rows:
        #print(row)
        image_id, features = row
        #print(image_id)
        #print(features)
        if features is not None:
            # 将BLOB转换为numpy数组
            features_array = np.frombuffer(features, dtype=np.float16)
            #print(features_array)
            all_image_features.append((features_array))
            image_ids.append(image_id)

    while True:
        # 获取用户输入的文本
        user_text = input("请输入文本：")
        # 生成用户文本的特征向量
        text_features = clipex.generate_text_features(user_text)
        print("文本特征向量：", text_features)
        
        # 计算相似度并找出相似度最高的5个结果

    
        similarities = [clip_feature.calculate_similarity(text_features, image_features) for image_features in all_image_features]
        top_indices = np.argsort(similarities)[-how_many_results:][::-1]  # 降序排序

        print("相似度最高的5个图片ID和路径：")
        for idx in top_indices:
            image_id = image_ids[idx]  # 使用正确的ID
            similarity = similarities[idx]
            result = image_db.execute_query("SELECT path FROM images WHERE id = ?", (image_id,))
            if result is not None:
                path = result[0][0]
                if os.path.exists(path):
                    print(f"图片ID: {image_id}, 路径: {path}, 相似度: {similarity:.2f}")
                    os.startfile(path)
                else:
                    print(f"图片ID: {image_id}, 文件不存在: {path}, 相似度: {similarity:.2f}")
        search_count.update_search_count('text')
    # 关闭数据库连接
    image_db.close()

if __name__ == "__main__":
    config = db_config.load_config()
    db_path = config["database_path"]
    # db_path = "images.db"  # 数据库文件路径
    main(db_path)
