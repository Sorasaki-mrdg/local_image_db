import os
import json

def update_search_count(search_type):
    """更新搜索计数器。

    根据传入的搜索类型（'image' 或 'text'），更新相应的搜索计数器。
    计数器存储在名为 'search_count.json' 的 JSON 文件中。

    参数:
        search_type (str): 搜索类型，必须是 'image' 或 'text'。

    返回:
        None
    """
    if search_type not in ['image', 'text']:
        raise ValueError("search_type 必须是 'image' 或 'text'")

    count_file = 'search_count.json'

    # 初始化计数器
    counts = {'image': 0, 'text': 0}

    # 如果文件存在，读取现有计数
    if os.path.exists(count_file):
        with open(count_file, 'r', encoding='utf-8') as f:
            try:
                counts = json.load(f)
            except json.JSONDecodeError:
                pass  # 如果文件损坏，继续使用初始化的计数器

    # 更新相应的计数器
    counts[search_type] += 1

    # 将更新后的计数写回文件
    with open(count_file, 'w', encoding='utf-8') as f:
        json.dump(counts, f, ensure_ascii=False, indent=4)

    # 打印当前总计数
    print(f"已搜图{counts['image']+counts['text']}次")