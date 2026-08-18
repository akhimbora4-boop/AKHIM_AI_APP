[app]

title = AKHIM AI
package.name = akhimai
package.domain = org.akhim.ai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1

# ইয়াত requests যোগ কৰা হ'ল (AI-ৰ লগত যোগাযোগ কৰিবলৈ)
requirements = python3==3.10.14,hostpython3==3.10.14,kivy==2.3.0,beautifulsoup4==4.12.3,soupsieve==2.5,requests

# এপটো থিয়কৈ (Portrait) চলাবলৈ
orientation = portrait
fullscreen = 0

# Android
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True
android.logcat_filters = *:S python:D

# ইণ্টাৰনেটৰ অনুমতি (AI ৰ লগত কথা পাতিবলৈ)
android.permissions = INTERNET

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
