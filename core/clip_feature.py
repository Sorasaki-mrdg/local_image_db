import torch
from PIL import Image
import cn_clip.clip as clip
from cn_clip.clip import load_from_name, available_models

class ClipFeatureExtractor:
    def __init__(self, model_name="ViT-H-14", device=None, download_root='./'):
        # 设置设备
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")

        # 加载模型和预处理函数
        self.model, self.preprocess = load_from_name(model_name, device=self.device, download_root=download_root)
        self.model.eval()

    def generate_image_features(self, image_path):
        # 读取图片并进行预处理
        image = Image.open(image_path).convert("RGB")
        image = self.preprocess(image).unsqueeze(0).to(self.device)

        # 使用模型生成特征向量
        with torch.no_grad():
            features = self.model.encode_image(image)
            features /= features.norm(dim=-1, keepdim=True)  # 归一化特征向量
        features_np = features.cpu().numpy()
        # 将特征向量转换为CPU张量并返回
        print("图片特征向量的维度：", features_np.shape)
        if features_np.shape != (1, 1024):
            raise ValueError(f"图片特征向量的维度应为 (1, 1024)，但实际维度为 {features_np.shape}")
            input("维度错误！")
        return features_np