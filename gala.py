# GalaPy, a Galaga Clone, objetive: mashup of various beat'em up games (galaga, galaxian, xevious)

""" TODO
+prioritarios: dejan al juego en un estado 'funcional'
    - pause button con O solo cuando el juego este activo
    
+ya si todo lo anterior se hizo: son cosas para hacerlo mas entrete
    - algunos power ups: bala mas gruesa, bala que atraviesa (añadirlos con un cooldown), bomba se que lanza con X, ralentizador
        - de manera general y abstracta sera un sprite (PowerUp class) que afecta una stat del jugador en una partida
        - podrian aparecer al matar cierta canitdad de enemigos o de forma random
    - moviemento erratico de zigzag
    - rocas moviendose por el camino
        - que salgan de afuera de la pantalla y sue muevan de abajo para arriba
    - reset pos de los enemigos al morir
"""

import pygame as pg
import sys
import os
import math
import random
import time

# Classes
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
        self.level_up_sound = pg.mixer.Sound(os.path.join('sound', 'level_up.mp3'))
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

class Stats():
    # clase para variables que vayan cambiando, se inicia una vez por run del .py
    def __init__(self, settings):
        self.settings = settings
        self.reset_stats()

        arch = open('galapyhg.txt', 'r')
        self.highscore = int(arch.readline().strip()) # este valor no deberia cambiar
        arch.close()
        self.running = True

    def reset_stats(self):
        # valores que se deben reinciar
        self.available_ships = self.settings.lives
        self.score = 0
        self.level = 1
        self.enemy_count = 0

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
        self.shot = pg.mixer.Sound(os.path.join('sound', 'galaga_shot.mp3'))
        self.shot.set_volume(0.5)

    def draw_bullet(self):
        # draw rect dibuja en la pantalla el rectangulo rect con el color
        pg.draw.rect(self.screen, self.color, self.rect)

    def update(self):
        # actualiza la posicion de la bala
        self.x += self.bullet_speed
        self.rect.x = self.x

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

class PowerUp(pg.sprite.Sprite):
    # Sprite que al colisionar con la nave, genera algun efecto
    def __init__(self, settings, screen):
        super().__init__()
        
        self.settings = settings
        self.screen = screen
        self.screen_rect = self.screen.get_rect()

        self.image = pg.image.load("enemy.png") # TODO añadir imagen de pwrp
        
        self.rect = self.image.get_rect()
        
        # definir su area de aparicion y una velocidad de bajada (o subida)
        # el eje x debe ser entre el rango donde se mueve la nave, una pos random
        # el eje y debe ser 0 o el ancho de la pantalla

        # 2: por desttuir un alien ,- aparecen horizontalmente (programar como zz)

        # definir una probabilidad de spawn de un pwrp
        
        self.appear = False

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def generate_powerup(self):
        if self.appear:
            pass

class GalaPy(): 

    "Metodos de inicio de objetos y loop del juego"    
    def __init__(self):
        pg.init() # iniciamos el modulo
        pg.mixer.init() # iniciamos el modulo de sonido
        pg.display.set_caption('GalaPy') # nombre de la ventana
        self.clock = pg.time.Clock() # creacion de un reloj para la velocidad de actualizacion

        # objetos principales
        self.settings = Settings() # valores constantes que usan otras partes del codigo
        
        # pantalla y valores de tamaño
        self.screen = pg.display.set_mode((self.settings.width, self.settings.height)) # creacion pantalla como un display_SURF
        
        """
        # self.screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        # self.settings.width = self.screen.get_rect().width
        # self.settings.height = self.screen.get_rect().height
        # self.settings.scalar = self.settings.width/self.settings.height
        """

        self.stats = Stats(self.settings) # stats, puntuacion, nivel, etc
        self.sb = Scoreboard(self) # score, higscore, nivel
        self.ship = Ship(self.settings, self.screen) # creacion nave
        self.bullets = pg.sprite.Group() # creamos un grupo de balas
        self.enemies = pg.sprite.Group() # creamos un grupo de enemigos
        self.enemies_fleet() # flota de enemigos

        # background and scrolling code
        self.start_backround()

        # boton y inicializacion
        self.button = Button(self.screen, 'Play Game', 250, 50)
        self.stats.running = False

    def run(self):
        while True:
            self.clock.tick(self.settings.FPS)
            self.check_events() # checkeo de eventos
            
            if self.stats.running:
                
                # scroll code
                for i in range(0, self.tiles):
                    # se blitea la pantalla cada ciclo con un nuevo valor de scroll
                    self.screen.blit(self.background_image, (i*self.background_width + self.scroll, 0))
                self.scroll -= 0.5
                if abs(self.scroll) > self.background_width:
                    self.scroll = 0

                # actualizacion de sprites
                self.ship.update_mov() # llama el metodo de la nave en base a los valores bool obtenidos de check_events
                self.update_bullets() # actualiza la posicion de cada una de las balas en la pantalla
                self.update_enemies() # actualiza al grupo de enemigos 
            self.update_screen() # dibuja/pega todos los valores actualizados
            

    "metodos de funcionamiento del juego"
    # metodos asociadas a eventos y botones
    def check_events(self):
        # chequeo de eventos
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

            elif event.type == pg.KEYDOWN:
                self.keydown_events(event) # tecla presionada

            elif event.type == pg.KEYUP:
                self.keyup_events(event) # tecla suelta

            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                self.button_pressed(mouse_pos)

    def keydown_events(self, event):
        # chequea los eventos donde se presiona una tecla
        
        if event.key == pg.K_ESCAPE or event.key == pg.K_q:
            self.overwrite_highscore()
            sys.exit()
        
        elif event.key == pg.K_UP:
            self.ship.up = True
            #print('↑')        
        elif event.key == pg.K_DOWN:
            self.ship.down = True
            #print('↓')
        elif event.key == pg.K_RIGHT:
            self.ship.right = True
            #print('→')
        elif event.key == pg.K_LEFT:
            self.ship.left = True
            #print('←')

        elif event.key == pg.K_SPACE:
            # si presionamos SPACE, chequea si la cantidad de balas actual es menos a las permitidas
            # se crea una nueva bala, se añade al grupo y se ejecuta el sonido
            if len(self.bullets) < self.settings.max_bullets:
                self.add_bullet()

        elif event.key == pg.K_p or event.key == pg.K_KP_0:
            if not self.stats.running:
                self.start_game()

        elif event.key == pg.K_o:
            self.stats.highscore = 0
            self.sb.prep_highscore()
            print("/highscore set to 0")
            # Nota: el score se sobreescribe sobre el actual hasta que se inicia un juego
            # esto debido a que se bliteo la imagen del backround justo despues

    def keyup_events(self, event):
        # chequea los eventos donde se suelta una tecla
        # estos eventos devuelven los booleanos para dejar de movernos
        if event.key == pg.K_UP:
            self.ship.up = False
                    
        elif event.key == pg.K_DOWN:
            self.ship.down = False
                    
        elif event.key == pg.K_RIGHT:
            self.ship.right = False
                    
        elif event.key == pg.K_LEFT:
            self.ship.left = False

    def button_pressed(self, mouse_pos):
        pressed = self.button.rect.collidepoint(mouse_pos)
        if pressed and not self.stats.running:
            self.start_game()

    def start_game(self):
        # inicio y reinicio de stats y opciones variables del juego

        pg.mouse.set_visible(False)
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.sb.prep_enemy_count()
        self.settings.init_dynamic_settings()
        self.stats.running = True

        self.bullets.empty()
        self.enemies.empty()

        self.enemies_fleet()
        self.ship.reset_pos()

    def check_highscore(self):
        if self.stats.score > self.stats.highscore:
            self.stats.highscore = self.stats.score
            self.sb.prep_highscore()

    # metodos que tengan que ver con las balas:
    def add_bullet(self):
        if self.stats.running:
            new_bullet = Bullet(self.settings, self.screen, self.ship)
            self.bullets.add(new_bullet)
            pg.mixer.Sound.play(new_bullet.shot)

    def update_bullets(self):
        # se llama el metodo update a cada una de las balas del grupo
        # este metodo actualiza la posicion de todas las balas en la pantalla
        self.bullets.update()
        for bullet in self.bullets.copy():
            # si la bala se va de la pantalla, sacarla del grupo
            if bullet.rect.left >= self.settings.width:
                self.bullets.remove(bullet)
                #print(len(balas))
        
        # despues de disparar balas, checkear colisiones
        self.bullet_enemies_collisions()

    def bullet_enemies_collisions(self): 
        """gestor  de colision entre balas y enemigos"""
        
        colissions = pg.sprite.groupcollide(self.bullets, self.enemies, True, True) # elimina los sprites que hayan chocado con alguna bala
        
        if colissions: # si es que hubieron colisiones en este loop
            for aliens in colissions.values():
                self.stats.score += self.settings.enemy_points * len(aliens)
                self.stats.enemy_count += 1
                self.enemies_new_life()
            
            self.sb.prep_enemy_count() # actualizamos contador de enemigos
            self.sb.prep_score() # actualizamos score
            self.check_highscore() # comprobamos si es que se supero el hs en este loop

        if not self.enemies:
            self.bullets.empty()
            #self.enemies_fleet()
            
            cooldown_ready = self.enemies_wait_cooldown_before_fleet() # esperamos un poco y creamos una flota
            # self.enemies_fleet()
            
            # aumentamos nivel
            if cooldown_ready:
                self.stats.level += 1
                self.sb.prep_level()

    def enemies_new_life(self):
        if self.stats.enemy_count > self.settings.enemies_killed_for_life:
            self.stats.available_ships += 1
            self.stats.enemy_count = 0
            self.sb.prep_enemy_count()
            self.sb.prep_ships()
            pg.mixer.Sound.play(self.settings.level_up_sound)

    # metodos que tienen que con enemigmos (movimiento y colisiones):
    def update_enemies(self): # esta funcion se ejecuta al final despues de las de abajo
        # primero se chekea que no hayan enemigos que hayan salido del pantalla
        # luego se ve su quedan en la pantalla

        self.check_enemies_on_screen()

        if len(self.enemies) != 0: # si quedan enemigos en pantalla
            self.move_one_enemy_in_zigzag() # hacemos mover a uno
            self.check_fleet_edges() # vemos si alguno toco un limite
            self.enemies.update() # actualizamos el valor de TODOS los enemigos
        else:
            # cooldown deja a los enemigos esperando una cantidad de ciclos antes de crear una nueva flota
            self.enemies_wait_cooldown_before_fleet()

        # checkeo de colision con nave
        if pg.sprite.spritecollideany(self.ship, self.enemies):
            pg.sprite.spritecollideany(self.ship, self.enemies).kill()
            self.ship_hit()

    def ship_hit(self):
        # funcion que se ejecuta al perder una vida
        if self.stats.available_ships > 0:
            self.stats.available_ships -= 1
            self.sb.prep_ships()

            self.bullets.empty()
            self.enemies.empty() # esto puede variar mas adelante
            self.enemies_fleet() # esto puede variar mas adelante
            self.ship.reset_pos()

            if self.stats.level <= self.settings.level_cap:
                self.settings.decrease_speed() # decrecemos la speed si aun no pasamos el cap
            
            time.sleep(0.8)
        else:
            self.stats.running = False
            pg.mouse.set_visible(True)
        
    def enemies_wait_cooldown_before_fleet(self):
        # funcion que hace esperar a la creacion de una flota antes de crear otra
        if self.settings.fleet_cooldown == 0:
            self.enemies_fleet()
            self.settings.fleet_cooldown = self.settings.fleet_cooldown_CONS
            if self.stats.level <= self.settings.level_cap:
                self.settings.increase_speed() # se crea la flota y aumentamos los valores de velocidad
            return True
        else:
            self.settings.fleet_cooldown -= 1
           # print(self.settings.fleet_cooldown)

    def enemies_fleet(self): # esta func crea una flota en la pantalla dado un grupo
        # creamos un alien y guardamos su valor de altura
        enemy = Enemy(self.settings, self.screen)
        enemy_height = enemy.rect.height
        
        # calcula el valor disponible en la pantalla
        disp_y = (self.settings.height - self.settings.bd_height) - 2*enemy_height
        # dado el espacio disponible, calcula cuantos enemigos caben dado el tamaño de uno generico
        number_of_enemies_y = math.ceil(disp_y/(2*enemy_height))
        #print(number_of_enemies_y)
        for j in range(7): # n columnas
            for i in range(number_of_enemies_y):
                # este loop crea una columna de enemigos
                enemy = Enemy(self.settings, self.screen)
                # despues de crear al alien, lo vamos moviendo a la derecha a otra columna
                # enemy.x = self.settings.width - 1.3*enemy.rect.width * j
                enemy.x = self.settings.width - 1.3*enemy.rect.width * j - 90
                
                # lo vamos cambiando de fila
                enemy.y = enemy.rect.y + 2*enemy.rect.height * i 
                
                # reasignamos los valores a rect para su posterior uso correcto en blit
                enemy.rect.x = enemy.x
                enemy.rect.y = enemy.y
                # lo añadimos al grupo
                self.enemies.add(enemy)

    def check_fleet_edges(self):
        # si algun enemigo toca la pantalla
        # cambiamos la direccion y de todos los enemigos y cerramos el loop
        for enemy in self.enemies.sprites():
            if enemy.check_edges():
                self.change_fleet_direction()
                break
                
    def change_fleet_direction(self):
        # por cada alien, cambiamos la direccion y su pos hacia la izq
        for enemy in self.enemies.sprites():
            enemy.dir *= -1 # -1 para cambiar la dir
            if not enemy.zigzag_move: # si es el que se esta moviendo en zz
                enemy.x -= self.settings.enemy_drop_spd
            
    def check_enemies_on_screen(self):
        # si algun enemigo esta fuera de la pantalla lo quitamos/perdemos el juego <-- añadir flag de dificultad
        for enemy in self.enemies.copy():
            if enemy.rect.left < 0: # and diffulty == easy, añadir en base al lv del dif
                #enemies.remove(enemy)
                self.ship_hit()
            #elif enemy.rect.y > opciones.largo:
            #    enemies.remove(enemy)

    def move_one_enemy_in_zigzag(self):
        # movimiento de un solo enemigo, se toma uno random de los sprites y se mueve
        # mientras la flota se mueve pasivamente
        if self.settings.zigzag_counter == 0:
            enemy = random.choice(self.enemies.sprites())
            enemy.zigzag_move = True
            self.settings.zigzag_counter = 1

        if self.settings.zigzag_counter == 1:
            #print('one moving!')
            self.settings.enemies_not_moving_cooldown -= 1 # valor de espera para que los demas sigan en su pos

        if self.settings.enemies_not_moving_cooldown == 0:
            self.settings.zigzag_counter = 0
            self.settings.enemies_not_moving_cooldown = 120*3


    # metodos que tengan que ver la pantalla
    def start_backround(self):
        #self.color_background = (5, 5, 24)
        self.background_image = pg.image.load('images/space_backround.png') # carga la imagen
        self.background_image = pg.transform.scale(self.background_image, (self.settings.width, self.settings.height)) # la escala 
        self.background_width = self.background_image.get_width()
        self.scroll = 0
        self.tiles = math.ceil(self.settings.width / self.background_width) + 1 # cuantas imagenes caben en la pantalla
        self.screen.blit(self.background_image, (0, 0)) # la bliteamos antes de iniciar el juego

    def update_screen(self):
        #self.screen.fill((0,0,0))     # testing purposes   

        for bullet in self.bullets.sprites(): # por cada bala, la dibujamos con el metodo, dada su posicion (actualizada)
            # y los otros parametros
            bullet.draw_bullet()

        self.ship.blitme() # bliteamos la nave (con sus posiciones actualizadas) a la pantalla con el metodo

        #self.enemies.draw(self.screen)  # blitea todos los sprites del grupo, hace lo mismo que abajo
        for enemy in self.enemies.sprites():
            # bliteamos todos los enemigos (con sus posiciones actualizadas) a la pantalla
            enemy.blitme()

        self.sb.show_score()

        # dibuja el boton si el juego no esta activo
        if not self.stats.running:
            self.button.draw_button()
        
        pg.display.flip() # refleja TODOS los cambios hechos en el loop, para luego iniciar otro, esto siempre
        # va al final
    
    def overwrite_highscore(self):
        arch = open("galapyhg.txt", 'w')
        print(str(int(self.stats.highscore)), file = arch)
        arch.close()

game = GalaPy()
game.run()
