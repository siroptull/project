import pygame
import random
import sys
import numpy as np
import math
from pygame import gfxdraw
import os
from pygame import mixer

# Константы
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TUBE_WIDTH, TUBE_HEIGHT = 80, 200
ITEM_RADIUS = 30
ITEM_SPACING = 10
BG_COLOR = (240, 240, 240)
TUBE_COLOR = (180, 180, 180)
ANIMATION_SPEED = 5

# Цвета шариков
COLORS = {
    'A': (255, 0, 0),    # Красный
    'B': (0, 255, 0),    # Зеленый
    'C': (0, 0, 255),    # Синий
    'D': (255, 255, 0),  # Желтый
}

def resource_path(relative):
    """Получает абсолютный путь к ресурсу для работы и в EXE"""
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = sys._MEIPASS
        # В режиме exe ищем ресурсы непосредственно в базовой папке
        path = os.path.join(base_path, os.path.basename(relative))
        if not os.path.exists(path):
            # Пробуем исходный относительный путь
            path = os.path.join(base_path, relative)
    except AttributeError:
        # В режиме разработки используем обычные пути
        base_path = os.path.abspath(".")
        path = os.path.join(base_path, relative)
    
    path = os.path.normpath(path)
    
    # Расширенная отладка
    if not os.path.exists(path):
        print(f"⚠️ Resource not found: {path}")
        print(f"Base path: {base_path}")
        print(f"Relative path: {relative}")
        print(f"Current working dir: {os.getcwd()}")
        print(f"Files in target dir: {os.listdir(os.path.dirname(path) if os.path.dirname(path) else base_path)}")
    else:
        print(f"✓ Resource found: {path}")
    
    return path

# Инициализация Pygame с обработкой ошибок
try:
    pygame.init()
    # Уменьшаем буфер для более быстрой реакции звуков
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except pygame.error as e:
    print(f"Ошибка инициализации Pygame: {e}")
    sys.exit(1)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_enabled = True
        self.sound_enabled = True
        self._music_loaded = False  # Отслеживаем состояние загрузки музыки
        
        # Инициализация звуковой системы с обработкой ошибок
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._load_resources()
        except Exception as e:
            print(f"Ошибка инициализации звука: {e}")
            self._initialize_fallback()

    def _load_resources(self):
        """Загрузка всех звуковых ресурсов"""
        self._load_sounds()
        self._load_music()

    def _load_sounds(self):
        """Загрузка звуковых эффектов"""
        sound_files = {
            'select': 800,  # Частота для генерации, если файл не найден
            'move': 400,
            'win': 1000,
            'error': 200
        }
        
        for name, default_freq in sound_files.items():
            try:
                path = resource_path(f'project/sound/{name}.wav')
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                else:
                    self.sounds[name] = self._generate_sound(default_freq)
            except Exception as e:
                print(f"Ошибка загрузки звука {name}: {e}")
                self.sounds[name] = self._generate_sound(default_freq)

    def _load_music(self):
        """Загрузка фоновой музыки с несколькими попытками"""
        music_files = [
            'project/sound/background.ogg',  # Предпочтительный формат
            'project/sound/background.mp3'   # Альтернативный вариант
        ]
        
        for music_file in music_files:
            try:
                path = resource_path(music_file)
                if os.path.exists(path):
                    pygame.mixer.music.load(path)
                    self._music_loaded = True
                    if self.music_enabled:
                        pygame.mixer.music.play(-1)
                    return
            except Exception as e:
                print(f"Ошибка загрузки музыки ({music_file}): {e}")
        
        print("Не удалось загрузить фоновую музыку")
        self._music_loaded = False

    def _generate_sound(self, freq=440, duration=0.1):
        """Генерация простого звука"""
        sample_rate = 44100
        samples = int(duration * sample_rate)
        buffer = np.zeros((samples, 2), dtype=np.int16)
        
        for s in range(samples):
            val = int(32767.0 * math.sin(2.0 * math.pi * freq * s / sample_rate))
            buffer[s][0] = buffer[s][1] = val
        
        return pygame.mixer.Sound(buffer)

    def _initialize_fallback(self):
        """Резервная инициализация при ошибках"""
        self.music_enabled = False
        self.sound_enabled = False
        self._music_loaded = False
        print("Звуковая система работает в ограниченном режиме")

    def toggle_music(self):
        """Безопасное переключение музыки"""
        if not self._music_loaded:
            print("Музыка не загружена, попытка перезагрузки...")
            self._load_music()
            return
            
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()

    def play(self, name):
        """Безопасное воспроизведение звука"""
        if self.sound_enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                print(f"Не удалось воспроизвести звук {name}")

    def toggle_sound(self):
        """Переключение звуковых эффектов"""
        self.sound_enabled = not self.sound_enabled
class Animation:
    def __init__(self):
        self.active = False
        self.item = None
        self.color = None
        self.start_pos = (0, 0)
        self.end_pos = (0, 0)
        self.current_pos = [0, 0]
        self.progress = 0
        self.from_tube = None
        self.to_tube = None
        
    def start(self, item, color, from_tube, to_tube):
        self.active = True
        self.item = item
        self.color = color
        self.from_tube = from_tube
        self.to_tube = to_tube
        self.start_pos = from_tube.get_item_position(len(from_tube.items)-1)
        self.end_pos = to_tube.get_item_position(len(to_tube.items))
        self.current_pos = list(self.start_pos)
        self.progress = 0
        
    def update(self):
        if not self.active:
            return False
            
        self.progress += ANIMATION_SPEED
        if self.progress >= 100:
            self.active = False
            if self.item in self.from_tube.items:  # Добавлена проверка
                self.from_tube.items.remove(self.item)
            self.to_tube.items.append(self.item)
            return False
            
        t = self.progress / 100
        t = t * t * (3 - 2 * t)  # Плавное ускорение и замедление
        
        self.current_pos[0] = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
        self.current_pos[1] = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
        
        return True
        
    def draw(self, screen):
        if self.active:
            gfxdraw.filled_circle(
                screen, 
                int(self.current_pos[0]), 
                int(self.current_pos[1]), 
                ITEM_RADIUS, 
                self.color
            )
            gfxdraw.aacircle(
                screen,
                int(self.current_pos[0]), 
                int(self.current_pos[1]), 
                ITEM_RADIUS, 
                (max(self.color[0]-50, 0), 
                max(self.color[1]-50, 0), 
                max(self.color[2]-50, 0))
            )

class Tube:
    def __init__(self, x, y, items=None, max_size=4):
        self.x = x
        self.y = y
        self.max_size = max_size
        self.items = items.copy() if items else []

    def is_empty(self):
        return len(self.items) == 0

    def is_full(self):
        return len(self.items) == self.max_size

    def top_item(self):
        return self.items[-1] if not self.is_empty() else None

    def can_receive(self, item):
        return (not self.is_full()) and (self.is_empty() or self.top_item() == item)

    def get_item_position(self, index):
        y_pos = self.y + TUBE_HEIGHT - (index + 1) * (ITEM_RADIUS * 2 + ITEM_SPACING)
        return (self.x + TUBE_WIDTH//2, y_pos + ITEM_RADIUS)

    def draw(self, screen, selected=False, animation=None):
        pygame.draw.rect(
            screen, 
            TUBE_COLOR, 
            (self.x, self.y, TUBE_WIDTH, TUBE_HEIGHT), 
            border_radius=10
        )
        
        if selected:
            pygame.draw.rect(
                screen, 
                (0, 200, 0), 
                (self.x, self.y, TUBE_WIDTH, TUBE_HEIGHT), 
                3, 
                border_radius=10
            )
        
        for i, item in enumerate(self.items):
            if animation and animation.active and animation.from_tube == self and i == len(self.items)-1:
                continue
                
            pos = self.get_item_position(i)
            color = COLORS[item]
            gfxdraw.filled_circle(
                screen, 
                pos[0], 
                pos[1], 
                ITEM_RADIUS, 
                color
            )
            gfxdraw.aacircle(
                screen,
                pos[0], 
                pos[1], 
                ITEM_RADIUS, 
                (max(color[0]-50, 0), 
                max(color[1]-50, 0), 
                max(color[2]-50, 0))
            )

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Сортировка колб")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)
        self.sound = SoundManager()
        self.reset_game()

    def reset_game(self):
        self.tubes = []
        self.selected_tube = None
        self.moves = 0
        self.animation = Animation()
        self.win_sound_played = False
        self._setup_tubes()

    def _setup_tubes(self):
        colors = ['A', 'B', 'C', 'D']
        items = colors * 4
        random.shuffle(items)
        
        # Позиции колб
        positions = [
            (100, 250), (220, 250), (340, 250),
            (460, 250), (580, 250), (700, 250)
        ]
        
        # Создаем 6 колб: 4 с шариками, 2 пустые
        for i in range(6):
            tube_items = items[i*4:(i+1)*4] if i < 4 else []
            self.tubes.append(Tube(positions[i][0], positions[i][1], tube_items))

    def is_level_complete(self):
        for tube in self.tubes:
            if not tube.is_empty():
                if len(set(tube.items)) != 1 or len(tube.items) != 4:
                    return False
        return True

    def _handle_click(self, pos):
        if self.animation.active:
            return
            
        for i, tube in enumerate(self.tubes):
            tube_rect = pygame.Rect(tube.x, tube.y, TUBE_WIDTH, TUBE_HEIGHT)
            if tube_rect.collidepoint(pos):
                if self.selected_tube is None:
                    if not tube.is_empty():
                        self.selected_tube = i
                        self.sound.play('select')
                else:
                    if self.selected_tube == i:
                        self.selected_tube = None
                    else:
                        from_tube = self.tubes[self.selected_tube]
                        to_tube = tube
                        
                        if from_tube.top_item() and to_tube.can_receive(from_tube.top_item()):
                            self.animation.start(
                                from_tube.top_item(),
                                COLORS[from_tube.top_item()],
                                from_tube,
                                to_tube
                            )
                            self.moves += 1
                            self.sound.play('move')
                        else:
                            self.sound.play('error')
                            
                        self.selected_tube = None
                return

    def _handle_keydown(self, event):
        if event.key == pygame.K_r:
            self.reset_game()
        elif event.key == pygame.K_m:  # Включение/выключение музыки
            self.sound.toggle_music()
        elif event.key == pygame.K_s:  # Включение/выключение звуков
            self.sound.toggle_sound()
        elif event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _update(self):
        if self.animation.update():
            if not self.animation.active and self.is_level_complete() and not self.win_sound_played:
                self.sound.play('win')
                self.win_sound_played = True

    def _draw(self):
        self.screen.fill(BG_COLOR)
        
        # Рисуем колбы
        for i, tube in enumerate(self.tubes):
            tube.draw(
                self.screen, 
                selected=self.selected_tube == i,
                animation=self.animation
            )
        
        # Рисуем анимацию поверх всего
        self.animation.draw(self.screen)
        
        # Отображаем количество ходов
        moves_text = self.font.render(f"Ходы: {self.moves}", True, (50, 50, 50))
        self.screen.blit(moves_text, (20, 20))
        
        # Отображаем статус звуков
        music_status = "Музыка: ON" if self.sound.music_enabled else "Музыка: OFF"
        sound_status = "Звуки: ON" if self.sound.sound_enabled else "Звуки: OFF"
        
        music_text = self.small_font.render(music_status, True, (50, 50, 50))
        sound_text = self.small_font.render(sound_status, True, (50, 50, 50))
        
        self.screen.blit(music_text, (SCREEN_WIDTH - 150, 20))
        self.screen.blit(sound_text, (SCREEN_WIDTH - 150, 50))
        
        # Проверка победы
        if self.is_level_complete():
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            self.screen.blit(s, (0, 0))
            
            congrats = self.font.render("Уровень пройден!", True, (255, 255, 255))
            self.screen.blit(congrats, 
                (SCREEN_WIDTH//2 - congrats.get_width()//2, 
                 SCREEN_HEIGHT//2 - 30))
            
            restart = self.small_font.render("Нажмите R для рестарта", True, (255, 255, 255))
            self.screen.blit(restart, 
                (SCREEN_WIDTH//2 - restart.get_width()//2, 
                 SCREEN_HEIGHT//2 + 10))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Только левая кнопка мыши
                        self._handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)
            
            self._update()
            self._draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()