#!/usr/bin/env python3

import pygame
from src.general.agame_core import AGameCore
from .game_config import GameConfig
from .game_state import GameState
from .snake_dir import Direction as SnakeDir
from random import randint
import logging

class GameCore(IGameCore):
    def __init__(self):
        pygame.init()
        self.fps_controller = pygame.time.Clock()
        self.window_mode = None
        self.log = logging.getLogger(__name__)

    def __increase_speed(self):
        TICKRATE_INCREASE = self.config.TICKRATE_INCREASE
        TICKRATE_MAX = self.config.TICKRATE_MAX

        current_speed = self.game_state.speed

        new_speed = min(current_speed + TICKRATE_INCREASE, TICKRATE_MAX)
        self.game_state.speed = new_speed

    def __change_window_mode(self, size):
        new_window_mode = [size, size]

        if self.window_mode != new_window_mode:
            self.window_mode = new_window_mode
            self.screen = pygame.display.set_mode(new_window_mode)

    def on_restart(self, config : GameConfig):
        '''Metoda restartuję grę. Wykorzystuje podaną konfigurację. Zwraca stan gry'''
        if config is None:
            config = GameConfig()
        self.config = config
        self.__change_window_mode(config.WINDOW_DIMENSION)

        self.clock = pygame.time.Clock()
        self.screen.fill(color=config.BACKGROUND_COLOR)
        self.cell_size = config.WINDOW_DIMENSION / config.BOARD_SIZE

        pygame.display.set_caption(config.CAPTION)
        
        
        snake_pos = tuple([config.BOARD_SIZE // 2, config.BOARD_SIZE // 2])
        self.game_state = GameState(snake_pos) # Ustawienie snake'a na środku planszy
        self.__draw_snake_head()

        self.__spawn_fruit()
        self.game_state.speed = self.config.TICKRATE_INITIAL
        pygame.display.update()
        self.fps_controller.tick(self.game_state.speed)

        
        return self.game_state
    

    def __draw_box(self, pos, color):
        '''Metoda rysuje kwadrat o podanym kolorze na podanej pozycji'''
        [left, top] = pos
        width = self.cell_size
        leftpx = left * width
        toppx = top * width
        #print(f'rysuję kwadrat {left} ({leftpx}), {top} ({toppx}) o szerokości {width}, kolor: {color}')
        pygame.draw.rect(self.screen,color, pygame.Rect(leftpx, toppx, width, width))

    def __draw_snake_head(self):
        self.__draw_box(self.game_state.snake_position, self.config.SNAKE_COLOR)
    
    def __update_snake_position(self):
        '''Metoda aktualizuje pozycję snake'a'''
        direction = self.game_state.direction
        snake_pos = self.game_state.snake_position
        self.game_state.snake_tail_queue.put(snake_pos)
        self.game_state.snake_tail_set.add(snake_pos)

        snake_pos = list(snake_pos)

        if direction == SnakeDir.UP:
            snake_pos[1] -= 1
        elif direction == SnakeDir.DOWN:
            snake_pos[1] += 1
        elif direction == SnakeDir.LEFT:
            snake_pos[0] -= 1
        elif direction == SnakeDir.RIGHT:
            snake_pos[0] += 1
        else:
            raise ValueError(f"Nieznany kierunek: {direction}")
        snake_pos = tuple(snake_pos)
        self.game_state.snake_position = snake_pos



    def __remove_last_segment(self):
        '''Metoda skraca ogon snake'a do długości równej wynikowi'''
        queue = self.game_state.snake_tail_queue
        set = self.game_state.snake_tail_set

        tail_pos = queue.get()
        set.remove(tail_pos)
        self.__draw_box(tail_pos, self.config.BACKGROUND_COLOR)


    def check_death(self, prev_direction : SnakeDir, new_direction : SnakeDir, snake_pos : tuple[int, int], is_prediction = True):
        '''Metoda sprawdza czy snake zjadł siebie lub uderzył w ścianę (w przypadku w którym ściana jest śmiertelna). Jeśli tak, zwraca `True`, w przeciwnym wypadku zwraca `False`'''
        if not self.config.EDGES_KILL:
            raise NotImplementedError("Opcja EDGES_KILL=False nie jest jeszcze zaimplementowana")
        
        # Sprawdź czy snake zjadł siebie.

        BOARD_SIZE = self.config.BOARD_SIZE
        ate_itself = snake_pos in self.game_state.snake_tail_set
        hit_wall = snake_pos[0] < 0 or snake_pos[0] >= BOARD_SIZE or snake_pos[1] < 0 or snake_pos[1] >= BOARD_SIZE
        
        # Jeżeli nagle się cofnie to też się zje
        ate_itself_by_going_back = prev_direction.opposite() == new_direction


        death_msg = 'śmierć - nieznana przyczyna'

        if ate_itself:
            death_msg = 'śmierć - zjadł siebie'
        elif hit_wall:
            death_msg = 'śmierć - uderzył w ścianę'
        elif ate_itself_by_going_back:
            death_msg = 'śmierć - zjadł siebie przez cofnięcie'
        else:
            return False

        if not is_prediction:
            self.log.info(death_msg)
        return True
        
    

    def __check_fruit(self):
        '''Metoda sprawdza czy snake zjadł owoc. Jeśli tak, zwraca `True`. W przeciwnym wypadku zwraca `False`'''
        snake_pos = self.game_state.snake_position
        fruit_positions = self.game_state.fruit_position

        return snake_pos == fruit_positions
            

    def __spawn_fruit(self):
        '''Metoda tworzy owoc w losowym punkcie, który nie jest zajęty przez snake'a'''
        free_positions = self.config.BOARD_SIZE ** 2 - len(self.game_state.snake_tail_set)
        if free_positions == 0:
            return False
        
        fruit_pos = tuple(self.game_state.snake_position)

        while fruit_pos in self.game_state.snake_tail_set or fruit_pos == self.game_state.snake_position:
            fruit_pos = tuple([randint(0, self.config.BOARD_SIZE - 1), randint(0, self.config.BOARD_SIZE - 1)])

        self.game_state.fruit_position = fruit_pos
        self.__draw_box(fruit_pos, self.config.FRUIT_COLOR)
        return True
    def __show_score(self):
        self.display_text(tuple([0, 0]), f'Wynik: {self.game_state.score}', self.config.SCORE_FONT_SIZE, self.config.SCORE_FONT, self.config.SCORE_FONT_COLOR)

    def __show_game_over(self):
        pass

    def __game_logic(self):
        '''Metoda wykonuje logikę gry. Wykonuje powyższe metody w odpowiedniej kolejności'''
        self.__update_snake_position()
        self.__show_score()

        if self.__check_fruit():
            self.__increase_speed()
            self.game_state.score += self.config.FRUIT_REWARD
            self.__spawn_fruit()
        else:
            self.__remove_last_segment()

        self.__draw_snake_head()

        if self.__check_death():

            self.game_state.score += self.config.DEATH_REWARD
            self.game_state.is_game_over = True
        else:
            self.game_state.score += self.config.SURVIVAL_REWARD




    def on_make_move(self, move : SnakeDir):

        self.game_state.direction = move
        self.__game_logic()

    
        pygame.display.update()
        self.fps_controller.tick(self.game_state.speed)
        self.game_state.events = pygame.event.get()

        return self.game_state

    def quit(self):
        pygame.quit()