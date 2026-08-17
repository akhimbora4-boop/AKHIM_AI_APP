[app]

title = AKHIM AI
package.name = akhimai
package.domain = org.akhim.ai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
# ইয়াত charset-normalizer==3.3.2 যোগ কৰা হৈছে
requirements = python3,kivy,beautifulsoup4==4.12.3,soupsieve==2.5,charset-normalizer==3.3.2
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

p4a.branch = develop

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