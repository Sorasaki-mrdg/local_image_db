import sqlite3
import torch
from PIL import Image
import cn_clip.clip as clip
from cn_clip.clip import load_from_name, available_models
import os

def generate_features(image_path, model, preprocess, device):
    # 读取图片并进行预处理
    image = Image.open(image_path).convert("RGB")
    image = preprocess(image).unsqueeze(0).to(device)

    # 使用模型生成特征向量
    with torch.no_grad():
        features = model.encode_image(image)
        features /= features.norm(dim=-1, keepdim=True)  # 归一化特征向量

    features_np = features.cpu().numpy()
    # 将特征向量转换为CPU张量并返回
    print("图片特征向量的维度：", features_np.shape)
    if features_np.shape != (1, 1024):
        raise ValueError(f"图片特征向量的维度应为 (1, 1024)，但实际维度为 {features_np.shape}")
        input("维度错误！")
    return features_np

def is_supported_image(file_path):
    # 检查文件扩展名是否为支持的格式
    supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.jfif']
    _, ext = os.path.splitext(file_path)
    return ext.lower() in supported_extensions

def main(db_path):
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 打印可用模型
    print("Available models:", available_models())

    # 设置设备
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 加载模型
    model, preprocess = load_from_name("ViT-H-14", device=device, download_root='./')
    model.eval()

    # 查询数据库中的所有图片路径
    cursor.execute("SELECT id, path, features FROM images")
    rows = cursor.fetchall()

    for row in rows:
        image_id, image_path, existing_features = row
        if is_supported_image(image_path):
            if existing_features is None:  # 检查features是否为空
                try:
                    # 生成特征向量
                    features = generate_features(image_path, model, preprocess, device)

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
    db_path = "images.db"  # 数据库文件路径
    main(db_path)
