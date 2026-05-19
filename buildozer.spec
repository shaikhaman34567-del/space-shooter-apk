[app]
title = Space Shooter Pro
package.name = spaceshooterpro
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3, pygame
orientation = portrait
fullscreen = 1
android.archs = armeabi-v7a, arm64-v8a
android.api = 33
android.minapi = 24
android.ndk_api = 24
[buildozer]
log_level = 2
warn_on_root = 0
source.main_filename = game.py
