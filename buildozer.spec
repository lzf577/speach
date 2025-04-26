[app]
title = TTSBatchApp
package.name = ttsbatch
package.domain = org.chattts
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav
version = 0.1
requirements = python3,kivy,requests
orientation = portrait
fullscreen = 0
osx.python_version = 3
osx.kivy_version = 2.2.1

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 31
android.ndk = 23b
android.ndk_path = $ANDROID_NDK
android.sdk_path = $ANDROID_SDK_ROOT
android.ndk_api = 21
android.arch = armeabi-v7a
minapi = 21
presplash.filename = %(source.dir)s/data/icon.png
icon.filename = %(source.dir)s/data/icon.png
# 关闭权限限制调试
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
