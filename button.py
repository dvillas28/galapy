import pygame as pg

class Button():
    def __init__(self, screen, msg, width, height):
        # pantalla
        self.screen = screen
        self.screen_rect = self.screen.get_rect()

        # dimensiones 
        self.width = width
        self.height = height

        # colores y fuente
        self.button_color = (36, 10, 42)
        self.text_color = (228, 222, 230)
        self.font = pg.font.SysFont(None, 48)

        # rect del boton, lo centramos en la pantalla
        self.rect = pg.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center 

        self.prep_msg(msg)

    def prep_msg(self, msg):
        # renerizamos una imagen
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect) # boton
        self.screen.blit(self.msg_image, self.msg_image_rect) # texto del boton