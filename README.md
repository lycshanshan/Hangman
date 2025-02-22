# Hangman

## 项目介绍
这是一个基于 Python 开发的 Hangman 猜词游戏，支持玩家与电脑互相对战，包含多种游戏模式（普通模式、无尽模式、电脑自动猜词模式）和难度选择。项目提供图形化界面、云存档、排行榜、游戏记录等功能。

## 运行准备
运行该项目需要安装以下库：
- `pygame`
- `tqdm`

## 游玩注意事项
1. **窗口定位**：游戏启动时窗口会自动居中显示；
2. **玩家出题**：需输入有效单词（不含特殊符号），否则无法开始游戏；
3. **电脑猜词模式**：该模式下玩家不可进行任何操作，且仅支持自动悬挂小人；
4. **画板功能**：绘画模式下点击 `Clear` 按钮可清空画板内容；
5. **开发者模式**：在开始界面连续点击七次 `Backspace`，可在猜词时显示答案；
6. **游戏记录**：所有对局记录会保存在 `Game Records.txt` 中，云存档需通过 UID 同步；
7. **静音功能**：点击左下角按钮可快速静音；
8. **模式互斥**：玩家出题时若启用自动悬挂，无尽模式将自动关闭。
