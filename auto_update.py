from ftplib import FTP
from tqdm import tqdm
from msvcrt import getch
from os import path, listdir, remove, system,  makedirs
from shutil import rmtree
from zipfile import ZipFile
import sys

def get_file_path():
    if getattr(sys, 'frozen', False):  # 检测是否在打包后的环境中
        # sys.executable 指向 .exe 文件的路径
        return sys.executable
    else:
        # 正常的 Python 解释器环境，使用 __file__
        return path.abspath(__file__)

# 文件夹绝对路径、文件名，删除文件使用
file_path = get_file_path()
folder_path = path.dirname(file_path)
self_name = path.basename(file_path)

# FTP 服务器信息
ftp_server = '106.14.135.243'
ftp_user = 'hangman_data'
ftp_password = 'e2B78A2FKcX38xWR'
ftp_version_path = 'latest_version.txt'
ftp_pack_path = 'Hangman_packed.zip'

local_version_path = f'{folder_path}\\latest_version.txt'
current_version_path = f'{folder_path}\\version.txt'
local_pack_path = f'{folder_path}\\Hangman_packed.zip'
local_version_name = 'latest_version.txt'
current_version_name = 'version.txt'
local_pack_name = 'Hangman_packed.zip'

first_use_notice = '''!!!重要提示!!!
首次使用本下载器时请注意: 
下载完成后，下载器所在文件夹中所有其他文件将被删除！
请务必将下载器放置于空文件夹中！
--------------------------------------------------------
按任意键以确认并开始下载...'''

def wait(notice):
    print(notice, end='', flush=True)
    getch()

def delete_except(folder_path, keep_files):
    for item in listdir(folder_path):
        item_path = path.join(folder_path, item)
        if not item in keep_files:
            if path.isfile(item_path):
                remove(item_path)  # 删除文件
            elif path.isdir(item_path):
                rmtree(item_path)  # 删除文件夹及其内容

def get_latest_version(): # 仅下载version.txt
    try:
        # 连接到FTP服务器
        ftp = FTP(ftp_server)
        # 切换到主动模式
        ftp.set_pasv(True)
        ftp.login(user=ftp_user, passwd=ftp_password)

        # 下载远程文件
        with open(local_version_path, 'wb') as local_file:
            ftp.retrbinary(f'RETR {ftp_version_path}', local_file.write)
        with open(local_version_path, 'r') as f:
            latest_version = f.readline().strip()
        ftp.quit()
        remove(local_version_path)
        return latest_version

    except Exception as e:
        print(f"Failed to get latest version data from ftp server: {e}")
        return False # failed

def download_latest_version():
    print()
    try:
        # 连接到FTP服务器
        ftp = FTP(ftp_server)
        # 切换到主动模式
        ftp.set_pasv(True)
        ftp.login(user=ftp_user, passwd=ftp_password)

        # 下载远程文件
        if path.exists(current_version_path):
            remove(current_version_path)
        with open(current_version_path, 'wb') as local_file:
            ftp.retrbinary(f'RETR {ftp_version_path}', local_file.write)
        system(f'attrib +h {current_version_path}')
        # remove(local_version_path)

        ftp_file_size = ftp.size(ftp_pack_path) # 获取文件大小
        # 打开本地文件用于写入二进制数据
        with open(local_pack_path, 'wb') as local_file:
            # 初始化进度条
            with tqdm(total=ftp_file_size, unit='B', unit_scale=True, desc='Downloading') as pbar:
                def callback(data):
                    local_file.write(data)
                    pbar.update(len(data))  # 更新进度条
                # 从FTP服务器下载文件
                ftp.retrbinary(f'RETR {ftp_pack_path}', callback)
        ftp.quit()

        print("Successfully downloaded latest version as a zip pack.")
        return True # succeeded
    except Exception as e:
        print(f"Failed to download latest version: {e}")
        return False # failed

def unzip_file(zip_file_path, extract_to_folder):
    # 检查目标文件夹是否存在，如果不存在则创建
    if not path.exists(extract_to_folder):
        makedirs(extract_to_folder)

    # 打开并解压.zip文件
    with ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_folder)
        print(f'Successfully unpacked {zip_file_path} to {extract_to_folder}')

def update_game():
    print(f'Current path: {folder_path}\\{self_name}')
    if path.exists(current_version_path):
        with open(current_version_path, 'r') as f:
            current_version = f.readline().strip()
        latest_version = get_latest_version()
        if not latest_version:
            return
        if current_version == latest_version:
            print(f'The game version {current_version} is the latest version!')
            return
        wait(f'current version: {current_version}, latest version: {latest_version}\nPress any key to start downloading...')
    else:
        wait(first_use_notice)
    if not download_latest_version():
        return
    delete_except(folder_path, [self_name, local_pack_name, current_version_name])
    unzip_file(local_pack_path, folder_path)
    remove(local_pack_path)
    print('Successfully download latest Hangman Game.')

update_game()
wait('Press any key to exit...')
