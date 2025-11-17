import sqlite3
import hashlib
import os
from PIL import Image
import shutil

class DuplicateFinder:
    """
    他们将你循环播放，
    而我紧抓着那些温柔时刻 如同易碎的珍藏。
    它们如此稀少难寻，
    我感激每个瞬间都刻骨难忘。
    裹着浪漫的片段 终以苦涩日出与告别收场，
    那些脆弱罕见的时刻让我思量，
    若非这般珍贵 是否还会散发同样芬芳。
    但我仍会吞噬你 躺卧在此追忆经年的情感摇晃，
    压抑的渴望与火山爆发 终归沉寂深藏。
    我思忖我们能否交融流淌，
    抑或只是双生灵魂 在错误的世代相望。
    """

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def calculate_file_hash(self, file_path, algorithm='md5'):
        """计算文件哈希值"""
        hash_func = hashlib.md5() if algorithm == 'md5' else hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            print(f"计算哈希失败 {file_path}: {e}")
            return None
    
    def get_all_images_from_db(self):
        """从数据库获取所有图片路径"""
        self.cursor.execute("SELECT id, path FROM images")
        return self.cursor.fetchall()
    
    def find_duplicate_groups(self):
        """查找重复图片组"""
        print("正在扫描图片文件...")
        images = self.get_all_images_from_db()
        
        hash_groups = {}
        valid_images = []
        
        # 计算所有有效图片的哈希值
        for image_id, image_path in images:
            if os.path.exists(image_path):
                file_hash = self.calculate_file_hash(image_path)
                if file_hash:
                    if file_hash in hash_groups:
                        hash_groups[file_hash].append((image_id, image_path))
                    else:
                        hash_groups[file_hash] = [(image_id, image_path)]
                    valid_images.append((image_id, image_path))
            else:
                print(f"文件不存在: {image_path}")
        
        # 只返回有重复的组
        duplicate_groups = {hash: paths for hash, paths in hash_groups.items() if len(paths) > 1}
        
        print(f"扫描完成！总共 {len(valid_images)} 个有效文件，找到 {len(duplicate_groups)} 组重复图片")
        return duplicate_groups
    
    def show_image_info(self, image_path):
        """显示图片信息"""
        try:
            with Image.open(image_path) as img:
                file_size = os.path.getsize(image_path) / 1024  # KB
                print(f"    路径: {image_path}")
                print(f"    大小: {file_size:.1f}KB")
                print(f"    尺寸: {img.size}")
                print(f"    格式: {img.format}")
                print("    " + "-" * 50)
        except Exception as e:
            print(f"    无法读取图片信息: {e}")
    
    def open_image(self, image_path):
        """用默认程序打开图片"""
        try:
            os.startfile(image_path)
            print(f"已打开: {image_path}")
        except Exception as e:
            print(f"打开图片失败: {e}")
    
    def handle_duplicate_group(self, hash_value, duplicate_group):
        """处理一组重复图片"""
        print(f"\n{'='*60}")
        print(f"发现重复图片组 (哈希: {hash_value[:8]}...)")
        print(f"包含 {len(duplicate_group)} 个文件:")
        print('='*60)
        
        # 显示所有重复文件信息
        for i, (image_id, image_path) in enumerate(duplicate_group, 1):
            print(f"{i}. ")
            self.show_image_info(image_path)
        
        while True:
            print("\n请选择操作:")
            print("1. 打开所有图片进行对比")
            print("2. 打开指定图片")
            print("3. 删除指定图片")
            print("4. 保留所有，跳过此组")
            print("5. 退出查重程序")
            
            choice = input("请输入选择 (1-5): ").strip()
            
            if choice == '1':
                # 打开所有图片
                for _, image_path in duplicate_group:
                    self.open_image(image_path)
                input("所有图片已打开，按回车继续...")
                
            elif choice == '2':
                # 打开指定图片
                try:
                    index = int(input(f"请输入要打开的图片编号 (1-{len(duplicate_group)}): ")) - 1
                    if 0 <= index < len(duplicate_group):
                        self.open_image(duplicate_group[index][1])
                    else:
                        print("编号无效！")
                except ValueError:
                    print("请输入有效数字！")
                    
            elif choice == '3':
                # 删除指定图片
                try:
                    index = int(input(f"请输入要删除的图片编号 (1-{len(duplicate_group)}): ")) - 1
                    if 0 <= index < len(duplicate_group):
                        image_id, image_path = duplicate_group[index]
                        self.delete_image(image_id, image_path)
                        # 从当前组移除已删除的图片
                        duplicate_group.pop(index)
                        if len(duplicate_group) <= 1:
                            print("该组重复图片已处理完毕")
                            break
                    else:
                        print("编号无效！")
                except ValueError:
                    print("请输入有效数字！")
                    
            elif choice == '4':
                # 跳过此组
                print("跳过此组重复图片")
                break
                
            elif choice == '5':
                # 退出程序
                print("退出查重程序")
                return False
            else:
                print("无效选择，请重新输入！")
        
        return True
    
    def delete_image(self, image_id, image_path):
        """删除图片文件和数据记录"""
        try:
            # 确认删除
            confirm = input(f"确认删除图片？(y/N): {image_path} ").strip().lower()
            if confirm != 'y':
                print("取消删除")
                return
            
            # 删除文件
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"已删除文件: {image_path}")
            else:
                print(f"文件不存在: {image_path}")
            
            # 删除数据库记录
            self.cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
            self.conn.commit()
            print(f"已删除数据库记录 ID: {image_id}")
            
        except Exception as e:
            print(f"删除失败: {e}")
    
    def run(self):
        """运行查重程序"""
        print("开始图片查重...")
        
        # 查找重复组
        duplicate_groups = self.find_duplicate_groups()
        
        if not duplicate_groups:
            print("没有找到重复图片！")
            return
        
        # 处理每个重复组
        for hash_value, duplicate_group in duplicate_groups.items():
            if not self.handle_duplicate_group(hash_value, duplicate_group):
                break  # 用户选择退出
        
        print("\n查重程序结束")
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    db_path = "images.db"  # 数据库文件路径
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    finder = DuplicateFinder(db_path)
    finder.run()

if __name__ == "__main__":
    main()