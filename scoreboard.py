import pygame as pg
from ship import Ship

class Scoreboard():
    # scoreboard para galapy
    def __init__(self, game):
        
        self.game = game

        self.screen = self.game.screen
        self.settings = self.game.settings
        self.stats = self.game.stats

        self.text_color = (228, 222, 230)
        self.font = pg.font.SysFont(None, 40)

        self.prep_score()
        self.prep_highscore()
        self.prep_level()
        self.prep_ships()
        self.prep_enemy_count()

    def prep_score(self):
        # renderiza una imagen y la posiciona
        rounded_score = round(self.stats.score, -1) # -1: redonde al multiplo de 10
        score_str = f'{int(rounded_score):,}' 
        
        self.score_image = self.font.render(score_str, True, self.text_color) # creacion de la imagen

        self.score_rect = self.score_image.get_rect()
        self.score_rect.left = 15
        self.score_rect.top = 10

    def prep_highscore(self):
        rounded_hg = round(self.stats.highscore, -1)
        highscore_str = f'{int(rounded_hg):,}'

        self.highscore_image = self.font.render(highscore_str, True, self.text_color)
        
        self.highscore_rect = self.highscore_image.get_rect()
        self.highscore_rect.centerx = self.screen.get_rect().centerx # lo colocamos al medio
        self.highscore_rect.top = 10

    def prep_level(self):
        level_str = f'{self.stats.level}'

        self.level_image = self.font.render(level_str, True, self.text_color)

        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.settings.width - 15
        self.level_rect.top = 10

    def prep_enemy_count(self):
        enemy_str = f'{self.stats.enemy_count}'
        self.enemy_count_image = self.font.render(enemy_str, True, self.text_color)

        self.enemy_count_rect = self.enemy_count_image.get_rect()
        self.enemy_count_rect.right = self.settings.width - 15
        self.enemy_count_rect.top = 40   

    def prep_ships(self):
        self.ships = pg.sprite.Group()
        for ship_number in range(self.stats.available_ships):
            ship = Ship(self.settings, self.screen)

            # rotar y achicar la imagen
            ship.image = pg.transform.rotate(ship.image, 90)
            ship.image = pg.transform.scale(ship.image, (30, 54/2))
            
            # la posicionamos
            ship.rect.x = (self.level_rect.left  - 100) - (ship.rect.width * ship_number) 
            ship.rect.y = 10
            
            self.ships.add(ship) # Ship debe heredar de sprite para eso

    def show_score(self):
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.screen.blit(self.enemy_count_image, self.enemy_count_rect)
        self.screen.blit(self.highscore_image, self.highscore_rect)

        self.ships.draw(self.screen)