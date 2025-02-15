import json
from random import randint

# process dictionary.txt, not used now
# from wordfreq import zipf_frequency
# all = []
# beginner = []
# easy = []
# medium = []
# difficult = []
# with open('dictionary.txt', 'r') as f:
#     for i in f.readlines():
#         i = i.strip()
#         if 5 <= len(i) <= 15 and i.isalpha() and i.islower():
#             all.append(i)
#             # 单词难度评分：zipf词频占70%, 单词长度占30%
#             # 评分0-40为入门词, 41-55为简单词, 56-75为中档词, 76及以上为难词
#             difficulty_score = (8 - zipf_frequency(i, 'en')) / 8 * 70 + (len(i) - 5) * 3
#             if difficulty_score <= 40:
#                 beginner.append(i)
#             elif difficulty_score <= 55:
#                 easy.append(i)
#             elif difficulty_score <= 75:
#                 medium.append(i)
#             else:
#                 difficult.append(i)

# print(len(all), len(beginner), len(easy), len(medium), len(difficult))
# data = [beginner, easy, medium, difficult, all]
# with open('dictionary.json', 'w') as f:
#     json.dump(data, f)

# 构建一个简单的 bigram 模型（可以从大量语料中统计得出）
# 花费时间太长，直接从json里读取模型
# from collections import defaultdict, Counter
# bigram_model = defaultdict(Counter)
# corpus  = ''
# for i, bank in enumerate(data):
#     if i == 4:
#         break
#     for j in bank:
#         frequency = round(zipf_frequency(j, 'en') * 10)
#         corpus += (j + '.') * frequency
#     # corpus += ('.'.join(bank) + '.') * (4 - i)

# # 构建 bigram 统计
# for i in range(len(corpus) - 1):
#     first, second = corpus[i], corpus[i + 1]
#     if first.isalpha() and second.isalpha():
#         bigram_model[first][second] += 1

# # 将 bigram 模型转换为概率分布（频率 -> 概率）
# for first, next_letters in bigram_model.items():
#     total_count = sum(next_letters.values())
#     for letter in next_letters:
#         bigram_model[first][letter] /= total_count

# with open('bigram_model.json', 'w') as f:
#     json.dump(bigram_model, f)

# 修改文件格式，通过干扰文件头让文件无法被正常读取
# def create_custom_json_file(filename, json_data):
#     # 自定义的干扰文件头
#     file_header = b'\xFF\xFE\x00\x00' # UTF-32
    
#     # 将 JSON 数据转换为字符串
#     json_str = json.dumps(json_data)
    
#     # 打开文件，以二进制写入模式
#     with open(filename, 'wb') as f:
#         # 写入干扰头部
#         f.write(file_header)
#         # 写入 JSON 数据
#         f.write(json_str.encode('utf-8'))

# with open('bigram_model.json', 'r') as f:
#     bigram_model = json.load(f)
#     create_custom_json_file('bigram_model.hgd', bigram_model)

# with open('dictionary.json', 'r') as f:
#     dic = json.load(f)
#     create_custom_json_file('dictionary.hgd', dic)

data = []
wordbank = []
bigram_model = []
length_wordbank = 0

with open('dictionary.hgd', 'rb') as f:
    f.seek(4)  # 跳过前4个字节干扰文件头
    # 读取剩余部分JSON数据
    json_data = f.read().decode('utf-8')
    # 将读取的字符串解析为 JSON
    data = json.loads(json_data)

with open('bigram_model.hgd', 'rb') as f:
    f.seek(4)  # 跳过前4个字节干扰文件头
    # 读取剩余部分JSON数据
    json_data = f.read().decode('utf-8')
    # 将读取的字符串解析为 JSON
    bigram_model = json.loads(json_data)

def auto_word_choose(wordbank_choice = [True, True, True, True]): # beginner, easy, medium, difficult
    # 自动随机选择单词，返回值为一个字符串
    global data, wordbank, length_wordbank
    wordbank = []
    length_wordbank = 0
    for i, choice in enumerate(wordbank_choice):
        if choice:
            wordbank.extend(data[i])
            length_wordbank += len(data[i])
    print(len(wordbank))
    idx = randint(0, length_wordbank-1)
    return wordbank[idx]