import os

# 初始化3个列表，分别存「所有名」「仅文件」「仅文件夹」
all_name_list = []
only_file_list = []
only_dir_list = []

with os.scandir(".") as entries:
    for entry in entries:
        all_name_list.append(entry.name)
        if entry.is_file(follow_symlinks=False):  # 仅纯文件（排除软链接/文件夹）
            only_file_list.append(entry.name)
        if entry.is_dir(follow_symlinks=False):   # 仅纯文件夹（排除软链接/文件）
            only_dir_list.append(entry.name)

# 打印筛选结果
# print("所有文件名/文件夹名：", all_name_list)
# print("仅纯文件名：", only_file_list)
# print("仅文件夹名：", only_dir_list)

for name in only_file_list:
    print(name)  # 默认自动换行，直接打印即可