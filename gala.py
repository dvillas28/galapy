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
import math
import random
import time
from settings import Settings
from stats import Stats
from ship import Ship
from bullet import Bullet
from enemy import Enemy
from button import Button
from scoreboard import Scoreboard

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
        arch = open("Galapy/galapyhg.txt", 'w')
        print(str(int(self.stats.highscore)), file = arch)
        arch.close()

game = GalaPy()
game.run()
