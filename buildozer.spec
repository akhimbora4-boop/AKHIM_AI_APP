[app]

title = AKHIM AI
package.name = akhimai
package.domain = org.akhim.ai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
# ইয়াত Python ৰ সুস্থিৰ ভাৰ্চন 3.11.4 দিয়া হৈছে আৰু charset-normalizer আঁতৰোৱা হৈছে
requirements = python3==3.11.4,kivy,beautifulsoup4==4.12.3,soupsieve==2.5
orientation = portrait
fullscreen = 0

# Android
android.api = 33
android.minapi = 24
android.ndk = 27b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True
android.logcat_filters = *:S python:D

# ইয়াত develop ৰ সলনি master কৰা হৈছে
p4a.branch = master

# iOS
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.12.2
ios.codesign.allowed = false

[buildozer]
log_level = 2
warn_on_root = 1

p4a.bootstrap = sdl2
p4a.extra_args = --skip-cleanup --force-build
