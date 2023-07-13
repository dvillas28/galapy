import pygame as pg

class Ship(pg.sprite.Sprite):
    def __init__(self, settings, screen):
        
        super().__init__()
        
        self.screen = screen
        self.settings = settings

        # cargamos la imagen y la modificamos
        image = pg.image.load('images/fighter2.png')
        image2 = pg.transform.rotate(image, 270)
        # self.image = pg.transform.scale(image2, (68*settings.scalar,84*settings.scalar))
        
        self.image = pg.transform.scale(image2, (60, 54))

        # obtenemos los parametros de rectangulo de la imagen y la pantalla
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # asignamos la posicion inicial de la nave 
        # hacia la x = izquierda y centro vertical, usando los parametros
        # de la pantalla

        self.rect.centery = self.screen_rect.centery
        self.rect.left = self.screen_rect.left
        
        # guadramos los valores de rectangulo de x e y como floats, para modificarlos
        # despues en los metodos de movimiento
        self.y = float(self.rect.centery)
        self.x = float(self.rect.left)

        # booleanos de movimientos, activan los metodos de mov
        self.up = False
        self.down = False
        self.right = False
        self.left = False

    def blitme(self):
        # blit toma la surf y su rectangulo y lo pega en la pantalla
        self.screen.blit(self.image, self.rect)

    def update_mov(self): # recordad el punto de ref del moviemiento (x=left, centery)
        if self.up and self.rect.top > 45:
            self.y -= self.settings.ship_speed

        if self.down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.settings.ship_speed

        if self.right and self.rect.right < 650:
            self.x += self.settings.ship_speed

        if self.left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # asignamos los valores rectangulos (enteros) a los valores float de rectangulo
        # que han ido cambiando en este metodo
        self.rect.centery = self.y
        self.rect.left = self.x

    def reset_pos(self):
        self.y = self.screen_rect.centery
        self.x = self.screen_rect.left