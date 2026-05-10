import bpy, addon_utils, os, sys, json, pathlib

addon_dir = bpy.utils.user_resource('SCRIPTS', path='addons', create=True)
target = os.path.join(addon_dir, 'RGBA_mmd')
os.makedirs(target, exist_ok=True)

FILES = {}
