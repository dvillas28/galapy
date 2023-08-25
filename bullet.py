import pygame as pg

class Bullet(pg.sprite.Sprite):
    def __init__(self, settings, screen, ship):
        super().__init__()

        self.screen = screen
        # como no tenemos imagen creamos un rectangulo sin imagen
        self.rect = pg.Rect(0, 0, settings.bullet_width*settings.scalar, settings.bullet_height*settings.scalar)

        #asignamos la posicion inicial de una bala (saliendo de la nave)
        self.rect.centery = ship.rect.centery
        self.rect.right = ship.rect.right

        # almacenamos su valor x como float para modificarlos despues
        self.x = float(self.rect.x)

        # color, speed y sonido
        self.color = settings.bullet_color
        self.bullet_speed = settings.bullet_speed
        self.shot = pg.mixer.Sound('sound/galaga_shot.mp3')
        self.shot.set_volume(0.5)

    def draw_bullet(self):
        # draw rect dibuja en la pantalla el rectangulo rect con el color
        pg.draw.rect(self.screen, self.color, self.rect)

    def update(self):
        # actualiza la posicion de la bala
        self.x += self.bullet_speed
        self.rect.x = self.x