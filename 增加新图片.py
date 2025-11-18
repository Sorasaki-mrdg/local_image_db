import sqlite3
import os
import core.db_config as db_config

# 定义插入图片路径的函数
def insert_image_path(image_path):
    cursor.execute('INSERT INTO images (path) VALUES (?)', (image_path,))
    conn.commit()

config = db_config.load_config()
image_directories = config["image_directories"]
db_path = config["database_path"]
valid_extensions = tuple(config["valid_extensions"])

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建images表，如果尚未创建
cursor.execute('''
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL,
    features BLOB
)
''')

# # 定义要处理的文件扩展名
# valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.jfif')

existing_paths = set(row[0] for row in cursor.execute('SELECT path FROM images').fetchall())
# # 遍历F:\picture目录下的所有文件
# image_directory = 'F:\\picture'
for image_directory in image_directories:
    if not os.path.exists(image_directory):
        print(f"警告：目录不存在，跳过: {image_directory}")
        continue
    if not os.path.isdir(image_directory):
        print(f"警告：不是目录，跳过: {image_directory}")
        continue
    for filename in os.listdir(image_directory):
        # 检查文件扩展名
        if filename.lower().endswith(valid_extensions):
            # 构建完整的文件路径
            image_path = os.path.join(image_directory, filename)
            # 检查existing_paths中是否已存在该文件路径
            if image_path not in existing_paths:
                # 如果数据库中没有此文件路径，则加入数据库
                print(image_path)
                insert_image_path(image_path)

# 查询数据库中的所有图片路径
cursor.execute("SELECT path FROM images")
rows = cursor.fetchall()

# 遍历所有路径，检查文件是否存在
for path, in rows:
    # 直接使用数据库中存储的完整路径，不需要再次拼接
    # 检查文件是否存在且位于配置的目录中
    file_in_config_dirs = any(path.startswith(directory) for directory in image_directories)
    if not os.path.exists(path) or not file_in_config_dirs:
        cursor.execute("DELETE FROM images WHERE path = ?", (path,))
        print(f"删除: {path}")
        if not os.path.exists(path):
            print(" 文件不存在")
        else:
            print(f" 不在配置目录中（配置目录: {image_directories}）")

# 提交更改
conn.commit()

# 关闭数据库连接
cursor.close()
conn.close()