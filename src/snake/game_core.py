#!/usr/bin/env python3

import pygame
from src.general import AGameCore, Direction as SnakeDir
from .game_config import GameConfig
from .game_state import GameState
from random import randint
import logging


class GameCore(AGameCore):
    def __init__(self):
        pygame.init()
        self.config = GameConfig()
        super().__init__(
            window_dimensions=self.config.WINDOW_DIMENSIONS,
            surface_order=['background','fruit','snake']
            )

        self.fps_controller = pygame.time.Clock()
        self.log = logging.getLogger(__name__)

    def __increase_speed(self):
        TICKRATE_INCREASE = self.config.TICKRATE_INCREASE
        TICKRATE_MAX = self.config.TICKRATE_MAX

        current_speed = self.game_state.speed

        new_speed = min(current_speed + TICKRATE_INCREASE, TICKRATE_MAX)
        self.game_state.speed = new_speed


    def on_restart(self, config : GameConfig):
        '''Metoda restartuję grę. Wykorzystuje podaną konfigurację. Zwraca stan gry'''
        if config is None:
            config = GameConfig()
        self.config = config
        self.surface_dict['background'].fill(color=config.BACKGROUND_COLOR)
        self.clock = pygame.time.Clock()
        self.cell_size = config.CELL_SIZE

        pygame.display.set_caption(config.CAPTION)
        
        
        snake_pos = tuple([config.BOARD_SIZE // 2, config.BOARD_SIZE // 2])
        self.game_state = GameState(snake_pos) # Ustawienie snake'a na środku planszy
        self.__draw_snake_head()

        self.__spawn_fruit()
        self.game_state.speed = self.config.TICKRATE_INITIAL
        self.render()
        self.fps_controller.tick(self.game_state.speed)
        self.game_state.events = pygame.event.get()
        self.game_first_move = True
        
        return self.game_state
    
    def get_default_config(self):
        return GameConfig()

    def __draw_snake_head(self):
        self.draw_box(self.game_state.snake_position, self.config.SNAKE_COLOR, self.cell_size, 'snake')
    
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
        self.draw_box(tail_pos, self.config.BACKGROUND_COLOR, self.cell_size, 'snake')


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
        
    

    def check_fruit(self):
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
        self.draw_box(fruit_pos, self.config.FRUIT_COLOR, self.cell_size, 'fruit')
        return True
    
    def __show_score(self):
        self.display_text(tuple([0, 0]), f'Wynik: {round(self.game_state.score,2)}', self.config.SCORE_FONT_SIZE, self.config.SCORE_FONT, self.config.SCORE_FONT_COLOR)


    def __game_logic(self, prev_dir : SnakeDir, new_dir : SnakeDir):
        '''Metoda wykonuje logikę gry. Wykonuje powyższe metody w odpowiedniej kolejności'''
        
        self.__show_score()

        
        self.__update_snake_position()

        if self.check_fruit():
            self.__increase_speed()
            self.game_state.score += self.config.FRUIT_REWARD
            self.__spawn_fruit()
        elif len(self.game_state.snake_tail_set) > GameConfig.INITIAL_LENGTH: 
            self.__remove_last_segment()
        self.__draw_snake_head()

        if self.check_death(prev_dir, new_dir, self.game_state.snake_position, False):
            self.game_state.score += self.config.DEATH_REWARD
            self.game_state.is_game_over = True
        else:
            self.game_state.score += self.config.SURVIVAL_REWARD
        



    def on_make_move(self, move : SnakeDir):
        prev_dir = self.game_state.direction
        if self.game_first_move:
            self.game_first_move = False
            prev_dir = move
        self.game_state.direction = move
        self.__game_logic(prev_dir, move)

    
        self.render()
        self.fps_controller.tick(self.game_state.speed)
        self.game_state.events = pygame.event.get()

        return self.game_state

    def quit(self):
        pygame.quit()