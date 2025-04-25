[app]
title = TTSApp
package.name = ttsapp
package.domain = org.kivy
source.dir = .
source.include_exts = py,kv,png,jpg,ttf,txt,json
version = 1.0
requirements = python3,kivy,kivymd,requests,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 运行入口
entrypoint = main.py

# 启动图标（可选）
# icon.filename = icons/app_icon.png

# 编译时避免压缩的文件（音频或模型）
android.allow_backup = True
android.archs = armeabi-v7a, arm64-v8a

# Android API 最小版本
android.minapi = 21
android.target = 33

# 忽略 log 级别限制（调试用）
log_level = 2

# 编译指令（不改也行）
[buildozer]
log_level = 2
warn_on_root = 1