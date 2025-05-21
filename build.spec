# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.building.build_main import Analysis, PYZ, EXE

block_cipher = None

# ================== НАСТРОЙКА ПУТЕЙ ==================
# Определяем корневую директорию проекта
def get_project_root():
    try:
        # Способ 1: Относительно расположения spec-файла
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, '..'))
        
        # Проверяем существование нужных папок
        if not os.path.exists(os.path.join(project_root, 'sound')):
            # Способ 2: Текущая рабочая директория
            project_root = os.path.abspath('.')
            
        return project_root
    except:
        return os.path.abspath('.')

PROJECT_ROOT = get_project_root()
SOUND_DIR = os.path.join(PROJECT_ROOT, 'sound')
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'images')

print(f"\n=== ПРОВЕРКА СТРУКТУРЫ ===")
print(f"Корень проекта: {PROJECT_ROOT}")
print(f"Папка sound: {'существует' if os.path.exists(SOUND_DIR) else 'НЕ НАЙДЕНА!'}")
print(f"Папка images: {'существует' if os.path.exists(IMAGES_DIR) else 'НЕ НАЙДЕНА!'}")
print("=========================\n")

# ================== РЕСУРСЫ ==================
def get_resources():
    resources = []
    
    # 1. Аудиофайлы - добавляем с сохранением плоской структуры
    if os.path.exists(SOUND_DIR):
        for file in os.listdir(SOUND_DIR):
            if file.lower().endswith(('.wav', '.mp3', '.ogg')):
                src = os.path.join(SOUND_DIR, file)
                # Важно: кладем файлы прямо в корень
                resources.append((src, '.'))  # Изменили 'sound' на '.'
                print(f"✓ Аудио: {file} -> {file} (в корень)")
    
    # 2. Иконка
    icon_path = os.path.join(IMAGES_DIR, 'icon.ico')
    if os.path.exists(icon_path):
        resources.append((icon_path, '.'))
        print("✓ Иконка добавлена в корень")
    
    # 3. Данные pygame
    resources.extend(collect_data_files('pygame'))
    
    return resources

# ================== НАСТРОЙКИ СБОРКИ ==================
a = Analysis(
    ['source/game3.py'],  # Укажите правильный путь к вашему главному файлу
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=get_resources(),
    hiddenimports=[
        'pygame',
        'numpy',
        'pygame._sdl2.audio',
        'pygame.mixer',
        'pygame.mixer_music',
        'pygame.gfxdraw'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Иконка для EXE
exe_icon = os.path.join(IMAGES_DIR, 'icon.ico') if os.path.exists(os.path.join(IMAGES_DIR, 'icon.ico')) else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='SortingBottles',  # Имя исполняемого файла
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Использовать UPX для сжатия (если установлен)
    console=False,  # Оставьте True для отладки, потом можно поменять на False
    icon=exe_icon,
    disable_windowed_traceback=False
)

print("\n=== СБОРКА ЗАВЕРШЕНА ===")
print(f"Исполняемый файл будет создан в: {os.path.join(PROJECT_ROOT, 'dist')}")