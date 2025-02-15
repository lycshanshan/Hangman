import time
import json
import logging
from ftplib import FTP
from os import path, remove, system
from uuid import getnode

UID = str(getnode()) # 获取设备的唯一标识符
ADMIN_UID = '________________' # 管理员UID
score = 0

logging.basicConfig(filename='Game logs.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
system(f'attrib +h "Game logs.log"')

def record_game(computer_play, if_win, ans_word, endless_mode):
    # 获取当前时间的结构化时间
    local_time = time.localtime()
    # 将时间格式化为字符串
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    player_mode = 'Computer play mode' if computer_play else 'Player play mode'
    result = 'Win' if if_win else 'Lose'
    with open('Game Records.txt', 'a') as f:
        if endless_mode:
            f.write(f'{current_time} {player_mode} - Endless\n    Word: {ans_word}\n    Result: None\n')
        else:
            f.write(f'{current_time} {player_mode}\n    Word: {ans_word}\n    Result: {result}\n')

def check_uid():
    # 检测UID是否正确
    with open('Game Records.txt', 'r+') as f:
        if next(f)[4:] != UID:
            # 将文件指针移动到文件开头
            f.seek(0)
            # 写入修改后的第一行，并保留其余内容
            f.write(f'UID: {UID}\n')

def judge_if_win(one_record):
    # 玩家游戏胜利或电脑游戏失败时，玩家记1分
    if (one_record[20] == 'P' and one_record.endswith('Win')) or (one_record[20] == 'C' and one_record.endswith('Lose')):
        return 1
    return 0

def get_game_record():
    # 获取游戏记录，返回值为列表，每一项为一条游戏记录，含3行（两个'\n    '）
    global score
    score = 0
    records = []
    if not path.exists('Game Records.txt'): # 如果游戏记录不存在，创建文件并在第一行写入UID
        with open('Game Records.txt', 'w') as f:
            f.write(f'UID: {UID}\n')
    check_uid()
    with open('Game Records.txt', 'r') as f:
        one_record = ''
        for line in f.readlines():
            if line[0:3] == 'UID': # 跳过UID行
                continue
            if line[0] != ' ' and one_record != '': # 该行是某条（非1）游戏记录的第一行
                score += judge_if_win(one_record)
                records.append(one_record)
                one_record = line.strip()
            elif one_record == '': # 该行是第一条游戏记录的第一行
                one_record = line.strip()
            else:
                one_record += f'\n    {line.strip()}'
    if one_record != '': # 把最后一条游戏记录加入列表
        score += judge_if_win(one_record)
        records.append(one_record)
    return records

def encode_file(source_path, target_path):
    file_header = b'\xFF\xFE\x00\x00' # 干扰文件头，编辑器将文件识别为UTF-32编码
    with open(source_path, 'r') as f:
        # 若源文件为.json文件，以json方式读取；否则，普通方式读取
        if source_path.endswith('.json'):
            json_data = json.load(f)
            file_data = json.dumps(json_data)
        else:
            file_data = f.read()
    # 打开文件，以二进制写入模式
    with open(target_path, 'wb') as f:
        # 写入干扰头部
        f.write(file_header)
        # 写入 JSON 数据
        f.write(file_data.encode('utf-8'))

def decode_file(source_path, target_path):
    with open(source_path, 'rb') as f:
        f.seek(4)  # 跳过前4个字节文件头
        # 读取文档内容
        file_data = f.read().decode('utf-8')
    # 若目标文件为.json文件，将读取的字符串解析为 JSON 并写入.json文件
    if target_path.endswith('.json'):
        json_data = json.loads(file_data)
        with open(target_path, 'w') as f:
            json.dump(json_data, f)
        return
    # 否则，以一般形式写入目标文件
    with open(target_path, 'w') as f:
        f.write(file_data)

# FTP 服务器信息
ftp_server = '106.14.135.243'
ftp_user = 'hangman_data'
ftp_password = 'e2B78A2FKcX38xWR'
ftp_path = 'players_data.hgd'
local_path = 'players_data.hgd'
local_path_decoded = 'players_data.json'

def download_savings(uid = UID):
    try:
        # 连接到FTP服务器
        ftp = FTP(ftp_server)
        # 切换到主动模式
        ftp.set_pasv(True)
        ftp.login(user=ftp_user, passwd=ftp_password)

        # 下载远程文件
        with open(local_path, 'wb') as local_file:
            ftp.retrbinary(f'RETR {ftp_path}', local_file.write)
        with open(local_path, 'rb') as f:
            f.seek(4)  # 跳过前4个字节文件头
            # 读取JSON, 将读取的字符串解析为 JSON
            json_data = json.loads(f.read().decode('utf-8'))
        if UID == ADMIN_UID: # 如果是管理员账户，则将文件解码后保存
            decode_file(ftp_path, local_path_decoded)
        remove(local_path)
        ftp.quit()
        if not uid in json_data: # 如果用户信息不存在，返回False（主程序播放sys_wrong音效）
            return False
        user_data = json_data[uid].split('**') # 获取到的是传参的uid的数据，默认为本机UID
        with open('Game Records.txt', 'w') as f:
            f.write(f'UID: {UID}\n') # 写入文件的一定是本机UID
            for record in user_data[:-1]:
                f.write(record + '\n')
        logging.info(f"Download savings from UID[{uid}] succeeded.")
        return True # succeeded
    except Exception as e:
        logging.error(f"download_savings failed for error: {e}")
        return False # failed

def update_savings():
    try:
        # 连接到FTP服务器
        ftp = FTP(ftp_server)
        # 切换到主动模式
        ftp.set_pasv(True)
        ftp.login(user=ftp_user, passwd=ftp_password)

        # 下载远程文件
        with open(local_path, 'wb') as local_file:
            ftp.retrbinary(f'RETR {ftp_path}', local_file.write)

        # 修改文件内容
        with open(local_path, 'rb') as f:
            f.seek(4)  # 跳过前4个字节文件头
            # 读取JSON, 将读取的字符串解析为 JSON
            json_data = json.loads(f.read().decode('utf-8'))

        json_data[UID] = '**'.join(get_game_record()) + '**' + str(score)
        with open(local_path, 'wb') as f:    
            file_header = b'\xFF\xFE\x00\x00' # UTF-32
            json_str = json.dumps(json_data)
            f.write(file_header)
            f.write(json_str.encode('utf-8'))

        # 上传修改后的文件
        with open(local_path, 'rb') as local_file:
            ftp.storbinary(f'STOR {ftp_path}', local_file)
        remove(local_path)
        ftp.quit()
        logging.info("Update savings succeeded.")
        return True # succeeded
    except Exception as e:
        logging.error(f"Update savings failed for error: {e}")
        return False # failed
    
def download_scores():
    try:
        ftp = FTP(ftp_server)
        ftp.set_pasv(True)
        ftp.login(user=ftp_user, passwd=ftp_password)

        # 下载远程文件
        with open(local_path, 'wb') as local_file:
            ftp.retrbinary(f'RETR {ftp_path}', local_file.write)
        with open(local_path, 'rb') as f:
            f.seek(4)  # 跳过前4个字节文件头
            # 读取JSON, 将读取的字符串解析为 JSON
            json_data = json.loads(f.read().decode('utf-8'))
        remove(local_path)
        ftp.quit()
        for key, value in json_data.items():
            json_data[key] = value.split('**')[-1]
        sorted_scores = dict(sorted(json_data.items(), key=lambda item: item[1], reverse=True))
        logging.info("Download scores succeeded.")
        return sorted_scores
    except Exception as e:
        logging.error(f"Download scores failed for error: {e}")
