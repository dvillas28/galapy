import pygame as pg
from os import path

class Settings(): 
    def __init__(self):
        # valores constantes a menos que se indique lo contrario
        self.FPS = 60
        
        # valores de tamaño de momento la pantalla tiene un tamaño fijo
        self.bd_height = 30
        self.width = 900*1.2 + 100
        self.height = 550*1.2 + self.bd_height
        self.scalar = 1.2

        self.lives = 3
        self.enemies_killed_for_life = 100
        self.level_up_sound = pg.mixer.Sound(path.join('sound', 'level_up.mp3'))
        self.level_up_sound.set_volume(0.5)

        self.level_cap = 12

        self.bullet_width = 15
        self.bullet_height = 5
        self.bullet_color = (255, 255, 255)
        self.max_bullets = 2

        self.enemy_drop_spd = 10
        self.zigzag_counter = 0 # constant value
        self.enemies_not_moving_cooldown = 120*3 # constant value
        
        self.fleet_cooldown_CONS = 120*0.5
        self.fleet_cooldown = self.fleet_cooldown_CONS

        self.speedup_scale = 1.1
        self.points_scale = 1.5
        
        self.init_dynamic_settings()

    def init_dynamic_settings(self):
        # stats que cambian a lo largo del juego
        self.ship_speed = 10*self.scalar
        self.bullet_speed = 30*self.scalar
        self.enemy_vertical_spd = 1.5*self.scalar

        self.enemy_points = 50

    def increase_speed(self):
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.enemy_vertical_spd *= self.speedup_scale

        self.enemy_points *= self.points_scale

    def decrease_speed(self):
        self.ship_speed /= (self.speedup_scale )
        self.bullet_speed /= (self.speedup_scale )
        self.enemy_vertical_spd /= (self.speedup_scale)