import sqlite3
import torch
from PIL import Image
from PIL import ImageGrab
import cn_clip.clip as clip
from cn_clip.clip import load_from_name, available_models
import numpy as np
import os
from core.clip_feature import ClipFeatureEx

def calculate_similarity(text_features, image_features):
    # 计算余弦相似度
    dot_product = np.dot(text_features.flatten(), image_features.flatten())
    norm_text = np.linalg.norm(text_features.flatten())
    norm_image = np.linalg.norm(image_features.flatten())
    similarity = dot_product / (norm_text * norm_image)
    return similarity



def main(db_path):
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    clipex = ClipFeatureEx(model_name="ViT-H-14", device=None, download_root='./')
    # 查询数据库中的所有图片特征向量
    cursor.execute("SELECT id, features FROM images")
    rows = cursor.fetchall()
    

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
    #input("按")
    while True:

        image = ImageGrab.grabclipboard()
        if isinstance(image, list):
            # 提取列表中的第一个元素（假设是文件路径）
            file_path = image[0].strip('"\' ')  # 去除路径两端的引号和空格

            # 检查是否为文件
            if os.path.isfile(file_path):
                # 检查文件扩展名
                valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.jfif'}
                ext = os.path.splitext(file_path)[1].lower()
                if ext in valid_extensions:
                    try:
                        # 读取图片并更新image变量
                        image = Image.open(file_path).convert("RGB")
                        print("图片已成功加载到image变量中。")
                    except Exception as e:
                        print(f"错误：无法打开图片文件，原因：{e}")
                else:
                    print(f"错误：不支持的文件类型 '{ext}'")
            else:
                print("错误：路径不存在或不是文件")

        #print(image)
        if isinstance(image, Image.Image):
            print("剪贴板的内容是图")
            # 生成剪贴板图片特征向量
            pic_features = clipex.generate_image_features(image)
            print("图片特征向量：", pic_features)
            
            # 计算相似度并找出相似度最高的5个结果
            similarities = [calculate_similarity(pic_features, image_features) for image_features in all_image_features]
            top_5_indices = np.argsort(similarities)[-5:][::-1]  # 降序排序

            print("相似度最高的5个图片ID和路径：")
            for idx in top_5_indices:
                image_id = image_ids[idx]  # 使用正确的ID
                similarity = similarities[idx]
                cursor.execute("SELECT path FROM images WHERE id = ?", (image_id,))
                result = cursor.fetchone()
                if result is not None:
                    path = result[0]
                    if os.path.exists(path):
                        print(f"图片ID: {image_id}, 路径: {path}, 相似度: {similarity:.2f}")
                        os.startfile(path)
                    else:
                        print(f"图片ID: {image_id}, 文件不存在: {path}, 相似度: {similarity:.2f}")
            input("按任意键继续")
        else:
            print("剪贴板不是图片")
            input("按任意键继续")
        
    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    db_path = "images.db"  # 数据库文件路径
    main(db_path)
