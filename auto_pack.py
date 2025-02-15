from ftplib import FTP
from os import path, listdir, remove, system,  makedirs
from shutil import rmtree
from zipfile import ZipFile
from subprocess import run

folder_path = path.dirname(path.abspath(__file__))
self_name = path.basename(path.abspath(__file__))

command_cd = ['cd', f'{folder_path}\\Hangman_packed']
command_pack = ['pyinstaller', '--noconfirm', '--onefile', '--windowed', 
                '--add-data', 'C:\Users\lycsh\AppData\Local\Programs\Python\Python311\Lib\site-packages\pgzero\data;pgzero/data', 
                '--add-data', f'{folder_path}\\images;images', '--add-data', f'{folder_path}\\sounds;sounds', 
                '--add-data', f'{folder_path}\\fonts;fonts', f'--icon="{folder_path}\\images\\icon.ico"', 
                f'{folder_path}\\main.py']

if path.exists('Hangman_packed'):
    rmtree('Hangman_packed')
makedirs('Hangman_packed')

run(command_cd)
run(command_pack)