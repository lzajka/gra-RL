from src.general import Direction
from src.general.maze import Maze, Position
import networkx as nx
from copy import copy
from collections import deque, namedtuple
from typing import Deque, Dict, Tuple, List, Set
from src.pacman.maze.objects import Energizer
from src.general.utils import TupleOperations as TO
from src.pacman.game_state import GameState

class MazeUtils:
    """Klasa dodająca dodatkowe metody związane z analizą labiryntów
    """
    def __init__(self, state):
        self._state = state
        self._maze : Maze = state.maze
        self._pos2edge = dict()
        self._energizers : List[Energizer] = []
        self.real_nodes : List[Position]= []
        self._init_graph(self._maze)
        self._detect_energizers(self._maze)
        self._prev_pacman_pos = None
    
    def debug_display(self):
        import tkinter as tk
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.pyplot as plt
        
        root = tk.Tk()
        root.title('Labirynt jako graf')

        f = plt.figure(figsize=(13,13), dpi=40)
        ax = f.add_subplot(1, 1, 1)
        self.draw(ax)
        canvas = FigureCanvasTkAgg(f, root)
        canvas.draw()
        canvas.get_tk_widget().pack()
        root.protocol('WM_DELETE_WINDOW', root.quit)
        root.mainloop()
        root.destroy()
    
    def draw(self, ax):
        import matplotlib.pyplot as plt
        graph = self.graph
        
        pos = {}
        
        m = max([n[1] for n in self.real_nodes]) + 1

        for n in self.real_nodes:
            pos[n] = (n[0], m - n[1])


        n_not_cleared = [n for n in graph.neighbors('nc')]
        n_cleared = [n for n in self.real_nodes if n not in n_not_cleared]
        
        nx.draw_networkx_nodes(graph, pos, nodelist=n_not_cleared, node_color='r', ax=ax)
        nx.draw_networkx_nodes(graph, pos, nodelist=n_cleared, node_color='g', ax=ax)
        nx.draw_networkx_edges(graph, pos, edgelist=self.real_edges, ax=ax)


    def _init_graph(self, maze : Maze) -> nx.Graph:
        """Metoda tworzy graf przedstawiający jakie skrzyżowania są ze sobą połączone.

        :param maze: Labirynt do przekształcenia w graf 
        :type Maze: Maze
        :return: Powstały graf
        :rtype: Graph
        """
        from src.pacman.maze.objects import Point
        # Przyszykuj zmienne
        maze_size = maze
        self.graph = nx.Graph()
        stack : Deque[Position] = deque()     # Dequeue używana jako stos
        visited : set = set()       # visited
        # Znajdź pierwsze lepsze skrzyżowanie
        initial_node = self._find_initial_node(maze)
        # Dodaj skrzyżowanie
        self.graph.add_node(initial_node)
        visited.add(initial_node)        
        # Znajdź sąsiadów
        neighbors = maze.get_neighbors(initial_node)
        # Dodaj ich na stos      
        for n in neighbors:
            stack.append(n)

        while len(stack) > 0:
            position: Position = stack.pop()
            
            # Sprawdź czy pusty
            cleared = True
            objects = self._maze.get_objects_at(position)
            for object in objects:
                if isinstance(object, Point): cleared = False
            
            self._mark_cleared(position, cleared)

            # Skanuj sąsiadów
            neighbors = maze.get_neighbors(position)
            visited.add(position)

            for n in neighbors:
                if n not in visited:
                    stack.append(n)
                    self.graph.add_edge(position, n)

        self.real_nodes = [n for n in self.graph.nodes if isinstance(n, Tuple)]

    def _mark_cleared(self, position : Position, is_cleared : bool):
        self.graph.add_edge(position, 'nc')
        
        if is_cleared:
            self.graph.remove_edge(position, 'nc')
            
    @property
    def real_edges(self):
        real_nodes = set(self.real_nodes)
        graph = self.graph

        edges = []
        for (u, v) in self.graph.edges:
            if u in real_nodes and v in real_nodes:
                edges.append((u, v))
        
        return edges


    def _detect_energizers(self, maze : Maze) -> List[Energizer]:
        objects = maze.get_all_objects()
        for s in objects:
            for o in s:
                if isinstance(o, Energizer): self._energizers.append(o)

    
    def _find_initial_node(self, maze : Maze) -> Position:
        """Znajduje początkowe skrzyżowanie w labiryncie.

        :param maze: Labirynt do przeszukania
        :type maze: Maze
        :return: Pozycja skrzyżowania
        :rtype: Position
        """
        maze_size = maze.get_size()
        for x in range(maze_size[0]):
            for y in range(maze_size[1]):
                pos = (x,y)
                if not maze.check_wall(pos):
                    return pos

    def update(self, pacman_pos : Position):


        pacman_pos = self._maze.handle_outside_positions(pacman_pos)
        if self._prev_pacman_pos == pacman_pos:
            return

        self._mark_cleared(pacman_pos, True)
    
    def get_energizers(self) -> List[Energizer]:
        return self._energizers

    def normalize_position(self, position : Position):
        maze_size = self._maze.get_size()
        return float(position[0] / maze_size[0]), float(position[1] / maze_size[1])
    

    def _distance_to_closest_point(self, origin : Position, neighbor : Position):
        
        self.graph.remove_edge(origin, neighbor)

        
        shortest = nx.shortest_path_length(self.graph, neighbor, 'nc')
        self.graph.add_edge(origin, neighbor)
        return shortest

    def from_which_direction(self, other : Position, me : Position) -> Direction:
        """Metoda zwraca kierunek z którego nadeszła pacman w danym skrzyżowaniu."""
        x = me[0] - other[0]
        y = me[1] - other[1]

        if x > 0:
            return Direction.LEFT
        elif x < 0:
            return Direction.RIGHT
        elif y > 0:
            return Direction.UP
        elif y < 0:
            return Direction.DOWN

    def get_closest_not_collected(self, state : GameState, origin : Position):
        """Metoda zwraca odległość od najbliższej nie odwiedzonej krawędzi w zależności od wyboru kierunku na skrzyżowaniu"""
        neighbors = list(self.graph.neighbors(origin))

        order = [
            Direction.LEFT,
            Direction.RIGHT,
            Direction.UP,
            Direction.DOWN
        ]

        for i in range(len(order)):
            order[i] = order[i].add_rotation(state.a_Pacman.direction)

        ret = [1024] * 4

        for neighbor in neighbors:
            dir = self.from_which_direction(neighbor, origin)
            ret[order.index(dir)] = self._distance_to_closest_point(origin, neighbor)
        # Znormalizuj (Podzielenie przez 1024 może być i tak dłuższej ścieżki nie będzie oraz float dobrze dzieli przez potęgi 2)
        
        for i in range(len(ret)):
            ret[i] = 1/(ret[i]+1)

        return ret
