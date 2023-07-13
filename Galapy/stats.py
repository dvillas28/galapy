class Stats():
    # clase para variables que vayan cambiando, se inicia una vez por run del .py
    def __init__(self, settings):
        self.settings = settings
        self.reset_stats()

        arch = open('Galapy/galapyhg.txt', 'r')
        self.highscore = int(arch.readline().strip()) # este valor no deberia cambiar
        arch.close()
        self.running = True

    def reset_stats(self):
        # valores que se deben reinciar
        self.available_ships = self.settings.lives
        self.score = 0
        self.level = 1
        self.enemy_count = 0