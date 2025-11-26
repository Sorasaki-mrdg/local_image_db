import sqlite3
import core.db_config as db_config

def remove_duplicate_paths():
    """删除重复的图片路径"""
    config = db_config.load_config()
    db_path = config["database_path"]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查找重复路径
    duplicates = cursor.execute('''
        SELECT path, COUNT(*) as count 
        FROM images 
        GROUP BY path 
        HAVING COUNT(*) > 1
    ''').fetchall()
    
    if not duplicates:
        print("没有发现重复路径")
        return
    
    print(f"发现 {len(duplicates)} 个重复路径:")
    for path, count in duplicates:
        print(f"  {path} (重复 {count} 次)")
    
    # 删除重复，只保留id最小的
    cursor.execute('''
        DELETE FROM images 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM images 
            GROUP BY path
        )
    ''')
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"已删除 {deleted_count} 条重复记录")

if __name__ == "__main__":
    remove_duplicate_paths()