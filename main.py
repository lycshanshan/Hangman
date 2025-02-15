import pygame
from threading import Thread
from queue import Queue
from time import sleep
from os import environ
from guess import *
from record import *
import record

# 设置窗口位置到屏幕中央
# 初始化 Pygame
pygame.init()
# 获取屏幕尺寸
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
# 计算窗口初始位置，使其居中
window_width = 960
window_height = 540
pos_x = (screen_width - window_width) // 2
pos_y = (screen_height - window_height) // 2
# 设置窗口位置到屏幕中央
environ['SDL_VIDEO_WINDOW_POS'] = f"{pos_x},{pos_y}"
pygame.init()

# 设置完窗口位置后，最后引入pgzero
import pgzrun

# 定义窗口大小
WIDTH = 960
HEIGHT = 540
VERSION = '3.1.1'
GAME_NAME = f'Hangman Game v{VERSION}'

# mute set module
# 保存原始的 sounds 对象
original_sounds = sounds
class SilentSound:
    def play(self):
        # 静默播放，什么也不做
        pass
class SilentSounds:
    def __getattr__(self, name):
        # 动态返回 SilentSound 实例，模拟 sounds.* 的行为
        return SilentSound()
mute = False
mute_button = Actor('unmute')
mute_button.pos = (40, 510)
def switch_mute():
    global sounds, mute
    if mute:
        mute_button.image = 'unmute'
        sounds = original_sounds
        sounds.complete.play()
    else:
        mute_button.image = 'mute'
        sounds = SilentSounds() # 用 SilentSounds 替换全局的 sounds
    mute = not mute

# classes - 输入框、文字框、按钮、复选框
class InputBox(Rect):
    def __init__(self, pos, size, fsize, if_center):
        super().__init__(*pos, *size)
        self.active = False
        self.text = ''
        self.fontsize = fsize
        self.if_center = if_center
    def draw(self, visible = True):
        if not visible:
            return
        screen.draw.filled_rect(self, 'white')
        screen.draw.rect(self, 'blue' if self.active else 'black')
        if self.if_center:
            screen.draw.text(self.text, center = self.center, fontsize=self.fontsize, color="black", fontname='consolas')
        else:
            pos = (self.x + self.fontsize*0.3, self.y + self.fontsize*0.3)
            screen.draw.text(self.text, pos, fontsize=self.fontsize, color="black", fontname='consolas')

class WordBox(Rect):
    def __init__(self, pos, size, fsize):
        super().__init__(*pos, *size)
        self.text = ''
        self.fontsize = fsize
    def draw(self):
        screen.draw.filled_rect(self, 'white')
        screen.draw.rect(self, 'blue' if self.text!='' else 'black')
        screen.draw.text(self.text, center = self.center, fontsize=self.fontsize, color="black", fontname='consolas')

class Button(Rect):
    def __init__(self, pos, size, text, fsize, button_color = 'grey', word_color = 'white'):
        super().__init__(*pos, *size)
        self.text = text
        self.fontsize = fsize
        self.color = button_color
        self.wordcolor = word_color
    def draw(self):
        screen.draw.filled_rect(self, self.color)
        screen.draw.text(self.text, center=self.center, fontsize=self.fontsize, color=self.wordcolor, fontname='consolas')

class Checkbox(Rect):
    def __init__(self, pos, a, text, default_state = False):
        size = (a, a)
        super().__init__(*pos, *size)
        self.text = text
        self.state = default_state
    def switch(self):
        self.state = not self.state
    def draw(self, visible = True):
        if not visible:
            return
        screen.draw.filled_rect(self, 'white')
        screen.draw.rect(self, 'black')
        screen.draw.text(self.text, (self.x+25, self.y-4), fontsize=self.width, color="black", fontname='consolas')
        if self.state:
            screen.draw.filled_rect(Rect((self.x+2, self.y+2), (self.width-4, self.height-4)), 'black')

# Pygamezero Actors, 用于首页、游戏页动画和图片显示
hangman_start = Actor('hangman00') # 首页动画(status == 0)
hangman_start.pos = (150, 250)
hangman_start_fridx_i = 0
hangman_start_fridx_j = 0
hangman_start_ftime = 0.1
hangman_game = Actor('hangman00') # 游戏界面动画(status == 2)
hangman_game.pos = (780, 170)
hangman_result = Actor('hangman7z') # 结束界面图片(status == 3)
hangman_result.pos = (300, 300)

# buttons
# normal buttons
button_start = Button((420, 250), (120, 45), 'Start', 25)
button_record = Button((420, 310), (120, 45), 'Records', 25)
button_update = Button((790, 100), (100, 40), 'Update', 20)
button_download = Button((790, 150), (100, 40), 'Download', 20)
button_rankinglist = Button((770, 300), (140, 40), 'Ranking List', 20)
button_confirm_settings = Button((405, 450), (150, 40), 'Confirm', 25)
button_restart = Button((500, 300), (160, 60), 'Restart', 30)
button_exit = Button((850, 480), (60, 28), 'Exit', 18)
button_clear = Button((680, 330), (80, 30), 'Clear', 20)
button_kill = Button((770, 330), (80, 30), 'Kill', 20)

# checkboxes
checkbox_auto_wordc = Checkbox((150, 270), 20, 'computer', True)
checkbox_player_wordc = Checkbox((150, 300), 20, 'player', False)
checkbox_endlessmode = Checkbox((570, 270), 20, 'Endless Mode', False)
checkbox_wordbank_beginner = Checkbox((680, 300), 20, 'beginner', True)
checkbox_wordbank_easy = Checkbox((680, 330), 20, 'easy', True)
checkbox_wordbank_medium = Checkbox((680, 360), 20, 'medium', True)
checkbox_wordbank_difficult = Checkbox((680, 390), 20, 'difficult', True)
checkbox_computer_play = Checkbox((570, 270), 20, 'Computer player', False)
checkbox_autohang = Checkbox((570, 300), 20, 'auto hang\n(disable to draw hangman)', True)

# checkbox groups
checkbox_group_wordc = [checkbox_auto_wordc, checkbox_player_wordc]
checkbox_group_swac = [checkbox_endlessmode, checkbox_wordbank_beginner, checkbox_wordbank_easy, 
                       checkbox_wordbank_medium, checkbox_wordbank_difficult] # show when auto choose
checkbox_group_swpc = [checkbox_computer_play, checkbox_autohang] # show when player choose

# input boxes
# fontsize should equal 0.5*height first, then adjust it according to the real situation
input_player_word = InputBox((240, 330), (200, 41), 20, False)
input_guess_word = InputBox((400, 60), (60, 60), 40, True)
input_download_uid = InputBox((760, 200), (160, 35), 18, False)
input_download_uid.text = UID

# initialize
# 游戏相关变量
game_status = 0
wordbank_choice = [True, True, True, True]
ans_word = ''
word_boxes = []
excluded_letters = ''
if_win = True
hang_phase = 0
paint_lines = []
developer_mode = 0
game_records = get_game_record()
game_records_index = 0
rankinglist = ''

hangman_image_number = [1, 5, 11, 7, 6, 6, 7, 7]
hangman_frame_list = [[(f'hangman{i}{j}') for j in range(hangman_image_number[i])] for i in range(len(hangman_image_number))]

# initialize
# used when restart in the game
def initialize():
    global game_status, checkbox_player_wordc, checkbox_endlessmode, checkbox_autohang, ans_word, excluded_letters, if_win, hang_phase, paint_lines, word_boxes
    global input_player_word, input_guess_word, hangman_game, wordbank_choice, checkbox_computer_play, developer_mode, game_records, game_records_index
    game_status = 0
    wordbank_choice = [True, True, True, True]
    ans_word = ''
    word_boxes = []
    excluded_letters = ''
    if_win = True
    hang_phase = 0
    paint_lines = []
    # developer_mode = 0
    game_records = get_game_record()
    game_records_index = 0
    checkbox_player_wordc.state = False
    checkbox_endlessmode.state = False
    checkbox_computer_play.state = False
    checkbox_autohang.state = True
    input_player_word.text = ''
    input_guess_word.text = ''
    input_download_uid.text = UID
    hangman_game.image = 'hangman00'

# ranking list 排行榜
def generate_rankinglist():
    global rankinglist
    rankinglist = 'Rank       ID                  Score\n\n'
    for i, (key, value) in enumerate(download_scores().items()):
        if i > 5:
            break
        rankinglist += f'{str(i+1)}          {key}       {value}\n\n'

# variables and functions about drawing board 画板相关变量和函数
is_drawing = False

def on_mouse_up():
    global is_drawing
    is_drawing = False  # 停止绘制

def on_mouse_move(pos):
    if is_drawing and Rect((680, 80), (180, 230)).collidepoint(pos):
        paint_lines[-1].append(pos)  # 继续在当前线条中添加点

# 多线程相关模块
# thread queue 
# 创建一个队列来保存 `draw_hang` 任务
task_queue = Queue()
# 记录当前是否有任务在执行
task_running = False
# 启动一个后台线程，负责处理任务队列
def task_manager():
    global task_running
    while True:
        # 从队列中获取一个任务（会阻塞直到有任务）
        task = task_queue.get()
        if task is not None:
            task_running = True  # 标记任务开始执行
            task()  # 执行任务
            task_running = False  # 标记任务执行完毕
        task_queue.task_done()  # 通知队列任务已完成
# 启动 `task_manager` 线程
manager_thread = Thread(target=task_manager, daemon=True)  # 后台线程
manager_thread.start()

# ftp操作线程
def thread_ftp(mode):
    global game_records, game_records_index
    if mode == 'update':
        if update_savings():
            sounds.complete.play()
        else:
            sounds.sys_wrong.play()
    elif mode == 'download':
        if download_savings(input_download_uid.text):
            sounds.complete.play()
            game_records = get_game_record()
            game_records_index = 0
        else:
            sounds.sys_wrong.play()

# word boxes
def generate_word_boxes(ans):
    global word_boxes
    # xy range: x[100,600], y[180,300]
    box_a = 500/(1.2*len(ans)-0.2) # na+(n-1)b=600-100, b=0.2a
    box_a = 60 if box_a > 60 else box_a
    box_a = 30 if box_a < 30 else box_a
    for i in range(len(ans)):
        x = 100 + i*1.2*box_a
        y = 180 + (120-box_a)/2
        word_boxes.append(WordBox((x, y), (box_a, box_a), box_a*0.67))

# 和 screen.text.draw 的 center 参数配合使用，把 text 的中心放置在 (x,y)
def center_place(x, y):
    return Rect((0, 0), (x*2, y*2)).center

def draw_checkboxes():
    checkbox_auto_wordc.state = not checkbox_player_wordc.state
    checkbox_auto_wordc.draw()
    checkbox_player_wordc.draw()
    for i in (checkbox_group_swac if checkbox_auto_wordc.state else checkbox_group_swpc):
        i.draw()

def check_checkboxes(pos):
    if checkbox_auto_wordc.collidepoint(pos):
        checkbox_player_wordc.state = False
        checkbox_autohang.state = True
        checkbox_endlessmode.state = False
        checkbox_computer_play.state = False
    if checkbox_player_wordc.collidepoint(pos):
        checkbox_player_wordc.state = True
        checkbox_endlessmode.state = not checkbox_autohang.state
    if checkbox_endlessmode.collidepoint(pos) and (not checkbox_player_wordc.state):
        checkbox_endlessmode.state = not checkbox_endlessmode.state
    if checkbox_wordbank_beginner.collidepoint(pos) and (not checkbox_player_wordc.state):
        checkbox_wordbank_beginner.switch()
    if checkbox_wordbank_easy.collidepoint(pos) and (not checkbox_player_wordc.state):
        checkbox_wordbank_easy.switch()
    if checkbox_wordbank_medium.collidepoint(pos) and (not checkbox_player_wordc.state):
        checkbox_wordbank_medium.switch()
    if checkbox_wordbank_difficult.collidepoint(pos) and (not checkbox_player_wordc.state):
        checkbox_wordbank_difficult.switch()
    if checkbox_autohang.collidepoint(pos) and checkbox_player_wordc.state:
        checkbox_autohang.state = not checkbox_autohang.state
        checkbox_endlessmode.state = not checkbox_autohang.state
        checkbox_computer_play.state = False if not checkbox_autohang.state else checkbox_computer_play.state
    if checkbox_computer_play.collidepoint(pos) and checkbox_player_wordc.state:
        checkbox_computer_play.state = not checkbox_computer_play.state
        checkbox_autohang.state = True
        checkbox_endlessmode.state = not checkbox_autohang.state

def draw_wordboxes(objs):
    for i in objs:
        i.draw()

def draw_hang():
    # 绘画下一个阶段的小人
    global hang_phase, game_status, if_win
    hang_phase += 1
    if hang_phase > 7: # 防止进入结算前短时间内多次绘画导致超限
        return
    for i in hangman_frame_list[hang_phase]:
        hangman_game.image = i
        sleep(0.05)
    if hang_phase == 7: # 判断游戏失败
        if not checkbox_endlessmode.state: # 正常模式下，记录游戏并进入结算界面
            sounds.lose.play()
            if_win = False
            record_game(checkbox_computer_play.state, if_win, ans_word, checkbox_endlessmode.state)
            game_status = 3
        else: # 无尽模式下，清除小人，重新开始绘画
            hang_phase = 0
            hangman_game.image = 'hangman00'

def judge_and_update(letter, word):
    global excluded_letters, task_queue
    if letter in word:
        sounds.right.play()
        for i, x in enumerate(word):
            word_boxes[i].text = letter if x == letter else word_boxes[i].text
    else:
        if not letter in excluded_letters:
            sounds.wrong.play()
            excluded_letters = excluded_letters + ' ' + letter
            task_queue.put(draw_hang)

def win():
    for i in word_boxes:
        if i.text == '':
            return False
    sounds.win.play()
    record_game(checkbox_computer_play.state, if_win, ans_word, checkbox_endlessmode.state)
    return True

def start_game():
    global game_status, ans_word, wordbank_choice
    wordbank_choice = [checkbox_wordbank_beginner.state, checkbox_wordbank_easy.state, 
                       checkbox_wordbank_medium.state, checkbox_wordbank_difficult.state]
    if checkbox_player_wordc.state:
        ans_word = input_player_word.text
        if ans_word == '':
            sounds.sys_wrong.play()
            return
    elif not any(wordbank_choice):
        sounds.sys_wrong.play()
        return
    else:
        ans_word = auto_word_choose(wordbank_choice)
    if checkbox_computer_play.state:
        thread_computer_play = Thread(target = computer_guess, args = (len(ans_word), ans_word), daemon = True)
        thread_computer_play.start()
    generate_word_boxes(ans_word)
    if checkbox_endlessmode.state:
        record_game(checkbox_computer_play.state, if_win, ans_word, checkbox_endlessmode.state)
    game_status = 2

def on_key_down(key):
    global game_status, ans_word, if_win, developer_mode
    enter = 0
    backspace = 0
    char = 0
    number = 0
    if key.value == 8:
        backspace = 1
    elif key.value == 13:
        enter = 1
    elif 97 <= key.value <= 122:
        char = 1
    elif 48 <= key.value <= 57:
        number = 1
    else:
        return False
    
    if game_status == 0:
        if backspace: # 主界面按七下backspace进入作弊模式
            developer_mode += 1
        elif enter:
            developer_mode = 0
    if input_player_word.active:
        if backspace: # 删除字符
            input_player_word.text = input_player_word.text[:-1]
        elif enter: # 回车确认输入
            input_player_word.active = False
        elif char: # 仅能输入字母
            input_player_word.text += chr(key.value)
            if len(input_player_word.text) > 15:
                input_player_word.text = input_player_word.text[1:]
    if input_guess_word.active:
        if backspace:  # 删除字符
            input_guess_word.text = input_guess_word.text[:-1]
        elif enter:  # 回车确认输入
            if input_guess_word.text == '':
                return
            judge_and_update(input_guess_word.text, ans_word)
            if win():
                if_win = True
                game_status = 3
            input_guess_word.text = ''
        else:
            if char: # 仅能输入字母
                input_guess_word.text = chr(key.value)
    if input_download_uid.active:
        if backspace:  # 删除字符
            input_download_uid.text = input_download_uid.text[:-1]
        elif enter:  # 回车确认输入
            input_download_uid.active = False
        elif number: # 仅能输入数字
            input_download_uid.text += chr(key.value)
        
def on_mouse_down(pos, button):
    global game_status, checkbox_player_wordc, checkbox_endlessmode, checkbox_autohang, is_drawing, if_win
    global paint_lines, wordbank_choice, checkbox_computer_play, game_records_index
    if game_status == 4 and button in {4, 5}:  # 游戏记录
        if button == 4:  # 上翻页
            game_records_index = max(0, game_records_index - 1)
        elif button == 5:  # 下翻页
            game_records_index = min(game_records_index + 1, len(game_records) - 4)
    if button != 1:
        return
    if game_status == 0:
        if button_start.collidepoint(pos):
            game_status = 1
        if button_record.collidepoint(pos):
            game_status = 4
    if game_status == 1:
        check_checkboxes(pos)
        if input_player_word.collidepoint(pos):
            input_player_word.active = True  # 激活输入框
        else:
            input_player_word.active = False  # 取消激活
        if button_confirm_settings.collidepoint(pos):
            start_game()
    if game_status == 2:
        if input_guess_word.collidepoint(pos) and not checkbox_computer_play.state:
            input_guess_word.active = True  # 激活输入框
        else:
            input_guess_word.active = False  # 取消激活
        if not checkbox_autohang.state:
            if Rect((680, 80), (180, 230)).collidepoint(pos):
                is_drawing = True  # 开始绘制
                paint_lines.append([pos])  # 创建新线条，添加第一个点
            if button_clear.collidepoint(pos):
                paint_lines = []
            if button_kill.collidepoint(pos):
                sounds.lose.play()
                if_win = False
                game_status = 3
    if game_status == 3:
        if button_restart.collidepoint(pos):
            initialize()
            game_status = 0
    if game_status == 4: # 游戏记录
        if input_download_uid.collidepoint(pos):
            input_download_uid.active = True  # 激活输入框
        else:
            input_download_uid.active = False  # 取消激活
        if button_update.collidepoint(pos):
            Thread(target = thread_ftp, args = ('update',), daemon = True).start()
        if button_download.collidepoint(pos):
            Thread(target = thread_ftp, args = ('download',), daemon = True).start()
        if button_rankinglist.collidepoint(pos):
            Thread(target = generate_rankinglist, daemon = True).start()
            game_status = 5
    if game_status in {1, 2, 4, 5} and button_exit.collidepoint(pos):
        if game_status == 2 and checkbox_computer_play.state:
            sounds.sys_wrong.play()
            return
        game_status in {1, 2} and initialize()  # 仅在 game_status 为 1 或 2 时运行 initialize
        game_status = 4 if game_status == 5 else 0
    if mute_button.collidepoint(pos):
        switch_mute()

def update(dt):
    global hangman_start_fridx_i, hangman_start_fridx_j
    if game_status == 0:
        # 更新帧索引
        hangman_start_fridx_j += dt / hangman_start_ftime
        # 如果帧索引超出范围，循环回到第一帧
        if hangman_start_fridx_j >= len(hangman_frame_list[hangman_start_fridx_i]):
            hangman_start_fridx_j = 0
            hangman_start_fridx_i += 1
            if(hangman_start_fridx_i >= len(hangman_frame_list)):
                hangman_start_fridx_i = 0
        # 切换角色图像
        hangman_start.image = hangman_frame_list[int(hangman_start_fridx_i)][int(hangman_start_fridx_j)]

# 绘制游戏内容
def draw():
    screen.clear()
    screen.fill((255, 255, 255))  # 设置背景颜色为white
    pygame.display.set_caption(GAME_NAME)  # 修改窗口标题
    pygame.display.set_icon(pygame.image.load("images/icon.png"))  # 设置窗口图标

    mute_button.draw()

    #status=0：游戏开始界面
    if game_status == 0:
        screen.draw.text('Hangman Game', center = center_place(480, 120), fontsize=50, color="black", fontname='consolas')
        button_start.draw()
        button_record.draw()
        hangman_start.draw()
    
    #status=1：选择模式界面
    if game_status == 1:
        screen.draw.text('Please set your game', center = center_place(480, 120), fontsize=40, color="black", fontname='consolas')
        screen.draw.text('Word selector', (150, 205), fontsize=30, color="black", fontname='consolas')
        screen.draw.text('Other settings', (570, 205), fontsize=30, color="black", fontname='consolas')
        screen.draw.text('Word:' if checkbox_player_wordc.state else '', (175, 330+6), fontsize=20, color="black", fontname='consolas')
        screen.draw.text('Wordbank:' if not checkbox_player_wordc.state else '', (570, 300-2), fontsize=20, color="black", fontname='consolas')
        draw_checkboxes()
        button_confirm_settings.draw()
        input_player_word.draw(checkbox_player_wordc.state)

    #status=2：猜词界面
    if game_status == 2:
        screen.draw.text('Guess a Letter:', (100, 70), fontsize=35, color="black", fontname='consolas')
        input_guess_word.draw()
        draw_wordboxes(word_boxes)
        screen.draw.text('Excluded:' + excluded_letters, (100, 400), fontsize=35, color="black", fontname='consolas')
        if checkbox_autohang.state:
            hangman_game.draw()
        else:
            button_clear.draw()
            button_kill.draw()
            screen.draw.rect(Rect((680, 80), (180, 230)), 'black')
            for line in paint_lines:
                if len(line) <= 1:
                    return
                # 使用 `for` 循环来逐点连接线条
                for i in range(len(line) - 1):
                    screen.draw.line(line[i], line[i + 1], 'red')  # 逐点绘制线段

        # cheat, use to debug
        screen.draw.text('Ans: '+ans_word if developer_mode == 7 else '', (20, 520), fontsize=15, color="black", fontname='consolas')

    #status=3：游戏结束界面
    if game_status == 3:
        text1 = 'Computer ' if checkbox_computer_play.state else 'You '
        text2 = 'won!' if if_win else 'lost!'
        screen.draw.text(text1 + text2, center = center_place(480, 120), fontsize=40, color="black", fontname='consolas')
        screen.draw.text('Answer: ' + ans_word, (500, 230), fontsize=30, color="black", fontname='consolas')
        button_restart.draw()
        hangman_result.image = 'rescued' if if_win else 'hangman7z'
        hangman_result.draw()
    
    #status=4: 游戏记录界面
    if game_status == 4:
        game_record_text = ''
        game_records_index_end = game_records_index + 4 if len(game_records) >= 4 else len(game_records) - 1
        for i in range(game_records_index, game_records_index_end):
            game_record_text +=  f'{game_records[i]}\n\n'
        screen.draw.text(game_record_text, (100, 40), fontsize=25, color="black", fontname='consolas')
        screen.draw.text(f'UID: {UID}', (760, 10), fontsize=18, color="black", fontname='consolas')
        screen.draw.text(f'Score: {record.score}', (760, 30), fontsize=18, color="black", fontname='consolas')
        button_update.draw()
        button_download.draw()
        input_download_uid.draw()
        button_rankinglist.draw()

    #status=5: 排行榜界面
    if game_status == 5:
        screen.draw.text(rankinglist, (100, 40), fontsize=25, color="black", fontname='consolas')

    if game_status in {1, 2, 4, 5}:
        button_exit.draw()

# computer guess module
from collections import Counter

guess_word_list = data[4]
def initialize_candidates(word_length):
    ### 根据目标单词的长度，筛选出候选单词 ###
    return [word for word in guess_word_list if len(word) == word_length]

def get_most_common_letter(current_pattern, candidates, guessed_letters):
    ### 从候选单词中选择出现频率最高的字母作为猜测字母 ###
    # 计算候选单词中每个字母的出现频率
    letter_counts = Counter(letter for word in candidates for letter in word if letter not in guessed_letters)
    # 返回出现频率最高的字母
    if letter_counts:
        return letter_counts.most_common(1)[0][0]
    else:
        # 使用N-gram模型返回最有可能出现的字母
        candidates = Counter()
        for i, char in enumerate(current_pattern):
            if char == "_":  # 对于未知的字母进行猜测
                # 结合前一个字母的信息
                if i > 0 and current_pattern[i - 1].isalpha():
                    previous_letter = current_pattern[i - 1]
                    if previous_letter in bigram_model:
                        candidates.update(bigram_model[previous_letter])
                # 结合后一个字母的信息
                if i < len(current_pattern) - 1 and current_pattern[i + 1].isalpha():
                    next_letter = current_pattern[i + 1]
                    for letter in bigram_model:
                        if next_letter in bigram_model[letter]:
                            candidates[letter] += bigram_model[letter][next_letter]
         # 排除已猜过的字母
        for letter in guessed_letters:
            if letter in candidates:
                del candidates[letter]
        if candidates: # 返回按概率排序的候选字母
            candidates_list = [letter for letter, _ in candidates.most_common()]
        else: # 如果没有候选字母，则返回频率最高的字母作为候选
            candidates_list = [letter for letter in "etaoinshrdlcumwfgypbvkjxqz" if letter not in guessed_letters]
        return candidates_list[0]

def filter_candidates(candidates, pattern, guess):
    ### 根据当前模式过滤候选单词 ###
    filtered_candidates = []
    for word in candidates:
        match = True
        for i, char in enumerate(pattern):
            if char == "_":  # 未知位置
                if word[i] == guess:  # 如果模式中是未知，且单词中该位置是猜测字母，则不符合
                    match = False
                    break
            else:  # 已知字母位置
                if word[i] != char:  # 模式中的已知字母和单词不匹配
                    match = False
                    break
        if match:
            filtered_candidates.append(word)
    return filtered_candidates

def computer_guess(word_length, actual_word):
    global input_guess_word, game_status, if_win
    # 电脑猜词逻辑
    # :param word_length: 目标单词的长度
    # :param actual_word: 玩家选择的实际单词（用于模拟游戏）
    # 初始化变量
    pattern = ["_"] * word_length  # 记录电脑当前猜测的模式
    guessed_letters = set()  # 记录已猜测过的字母
    wrong_guesses = 0  # 错误猜测次数
    max_wrong_guesses = 7  # 最多允许 6 次错误猜测
    candidates = initialize_candidates(word_length) # 初始化候选单词列表

    while "_" in pattern and wrong_guesses < max_wrong_guesses:
        # 选择最常见的字母作为下一个猜测字母
        guess = get_most_common_letter(pattern, candidates, guessed_letters)

        # 添加到已猜测字母中
        guessed_letters.add(guess)
        input_guess_word.text = guess
        sleep(1.5)

        # 检查猜测是否在目标单词中
        judge_and_update(guess, actual_word)
        if win():
            if_win = True
            game_status = 3
            return
        input_guess_word.text = ''
        if guess in actual_word:
            # 更新模式
            for i, char in enumerate(actual_word):
                if char == guess:
                    pattern[i] = guess
            # 根据新的模式过滤候选单词
            candidates = filter_candidates(candidates, pattern, guess)
        else:
            wrong_guesses += 1
        sleep(1.5)

pgzrun.go()