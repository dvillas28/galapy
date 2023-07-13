import pygame as pg

class Enemy(pg.sprite.Sprite):
    def __init__(self, settings, screen):
        super().__init__()
        self.screen = screen
        self.screen_rect = self.screen.get_rect() # rectangulo de la pantalla para su uso posterior
        self.settings = settings
    
        # iniciamos la imagen y su rectangulo, en este caso, la imagen es random
        self.images = ['images/enemy_3(1).png','images/enemy1_bigger2.png']
        self.image = pg.image.load(self.images[0])
        self.image = pg.transform.scale(self.image, (44*self.settings.scalar, 34*self.settings.scalar))
        self.rect = self.image.get_rect()

        #posicion inicial
        self.rect.x = int(self.rect.width)
        self.rect.y = int(self.rect.height)

        # posicionn exacta
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # variables de llegada de flota, recordar almacenar estos valores en opciones mas tarde
        self.arrival_spd = 0
        self.arrival_g = 0.15
        self.dir = 1

        # variables de movimiento de zigzag
        self.zigzag_move = False
        self.zigzag_spd = 4
        self.zigzag_dir = 1

    def blitme(self):
        # blitea el enemigo a la pantalla
        self.screen.blit(self.image, self.rect)

    def update(self):
        if self.arrival_spd != 0:
            # aca el alien se mueve hacia la izq hasta que se llega a 0
            self.x -= self.arrival_spd
            self.arrival_spd -= self.arrival_g

            if self.arrival_spd  <= 0:
                # una vez de llega a 0, el enemigon se queda ahi
                self.arrival_g = 0
                self.arrival_spd = 0
        
        else: # movimiento default
            if not self.zigzag_move:
                # movimiento pasivo arriba y hacia abajo
                self.y += self.settings.enemy_vertical_spd * self.dir
            else:
                # movimiento hacia adelante si es que el bool esta activo
                self.x -=self.zigzag_spd*self.settings.scalar
                ## TODO self.y
            
        # actualizacion de los valores de posicion
        self.rect.x = self.x
        self.rect.y = self.y

    def check_edges(self):
        # este metodo checquea si el enemigo toca algun limite de la pantalla
        if self.rect.top <= 23 :#self.settings.bd_height:
            return True
        elif self.rect.bottom >= self.screen_rect.bottom:
            return True