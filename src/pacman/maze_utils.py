from enum import Enum
from src.general import Direction
from src.general.maze import Maze, Position, PrecisePosition
import networkx as nx
from copy import copy
from collections import deque, namedtuple
from typing import Deque, Dict, Tuple, List, Set
from src.pacman.maze.objects import Energizer
from src.general.utils import TupleOperations as TO
from src.pacman.game_state import GameState
from logging import getLogger

class NodeTypes(Enum):
    REGULAR         = 'regular'
    VIRTUAL   = 'not_collected'

class MazeUtils:
    """Klasa dodająca dodatkowe metody związane z analizą labiryntów
    """
    def __init__(self, state):
        self._state = state
        self._maze : Maze = state.maze
        self._pos2edge = dict()
        self._energizers : List[Energizer] = []
        self.real_nodes : List[Position]= []
        self._energizers = []
        self._init_graph(self._maze)
        self._prev_pacman_pos = (-1, -1)
        self._logger = getLogger(__name__)

    
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
        
        nx.draw_networkx_nodes(graph, pos, nodelist=n_not_cleared, node_color='r', ax=ax, node_size=100)
        nx.draw_networkx_nodes(graph, pos, nodelist=n_cleared, node_color='g', ax=ax, node_size=100)
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
        # Znajdź pierwszy lepszy wierzchołek
        initial_node = self._find_initial_node(maze)
        # Dodaj pierwszy wierzchołek
        self.graph.add_node(initial_node, node_type=NodeTypes.REGULAR)
        # Dodaj wirtualne wierzchołki

        self.graph.add_node('nc', node_type=NodeTypes.VIRTUAL)
        self.graph.add_node('intersections', node_type=NodeTypes.VIRTUAL)
        self.graph.add_node('energizers', node_type=NodeTypes.VIRTUAL)

        visited.add(initial_node)        
        # Znajdź sąsiadów
        neighbors = maze.get_neighbors(initial_node)
        # Dodaj ich na stos      
        for n in neighbors:
            stack.append(n)

        while len(stack) > 0:
            position: Position = stack.pop()
            
            # Sprawdź czy pusty
            present = [False, False]
            objects = self._maze.get_objects_at(position)


            for o in objects:
                if isinstance(o, Point): present[0] = True
                if isinstance(o, Energizer): 
                    present[1] = True
                    self._energizers.append(o)
            
            self._set_tag(position, present[0], 'nc')
            self._set_tag(position, present[1], 'energizers')
            # Skanuj sąsiadów
            neighbors = maze.get_neighbors(position)
            visited.add(position)

            # Tutaj termin skrzyżowanie jest inaczej używany niż w reszcie tego projektu.
            # Jest to punkt który sąsiaduje z min. 3 dostępnymi pozycjami
            if len(neighbors) >= 3:
                self._set_tag(position, True, 'intersections')

            for n in neighbors:
                self.graph.add_node(n, node_type=NodeTypes.REGULAR)
                self.graph.add_edge(position, n)
                if n not in visited:
                    stack.append(n)

        self.real_nodes = [n for n in self.graph.nodes if isinstance(n, Tuple)]

    def _set_tag(self, position : Position, should_set : bool, master):
        self.graph.add_edge(position, master)
        
        if not should_set:
            self.graph.remove_edge(position, master)
            
    @property
    def real_edges(self):
        real_nodes = set(self.real_nodes)
        graph = self.graph

        edges = []
        for (u, v) in self.graph.edges:
            if u in real_nodes and v in real_nodes:
                edges.append((u, v))
        
        return edges


    
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
        self._prev_pacman_pos = pacman_pos
        self._set_tag(pacman_pos, False, 'energizers')
        self._set_tag(pacman_pos, False, 'nc')
    
    def get_energizers(self) -> List[Energizer]:
        return self._energizers

    def normalize_position(self, position : Position):
        maze_size = self._maze.get_size()
        return float(position[0] / maze_size[0]), float(position[1] / maze_size[1])
    
    @staticmethod
    def crossed_center(pos_a : PrecisePosition, pos_b : PrecisePosition) -> bool:
        """Metoda zwraca true jeżeli przekroczono środek.

        :param pos_a: Pozycja punktu A
        :type pos_a: PrecisePosition
        :param pos_b: Pozycja punktu B
        :type pos_b: PrecisePosition
        :return: Jeżeli linia pomiędzy punktami A oraz B przechodzi przez środek bloku zwraca `True`. W przeciwieństwie `False`
        :rtype: bool
        """
        # Sprawdzanie, czy pozycja jest po przejściu przez tunel nie jest konieczne.
        # Jeśli przeskoczy na drugą stronę - zmieni blok, a więc poniższe if zwróci fałsz

        # Ponieważ długość skoku jest < 0.5 . Pozycja może jedynie przeskoczyć przez środek, jeżeli oba pozycje znajdują się w bloku.
        if TO.round_tuple(pos_a) != TO.round_tuple(pos_b):
            return False
        
        # Jeżeli pozycja się nie zmieniła zwróć Fałsz
        if pos_a == pos_b:
            return False
        
        center_a = Maze.to_center_pos(pos_a)
        center_b = Maze.to_center_pos(pos_b)


        block : PrecisePosition = TO.round_tuple(pos_a)
        block_center = Maze.to_center_pos(block)

        # Znajdź oś po której się poruszono
        axis : List[PrecisePosition, PrecisePosition, PrecisePosition] = None

        for i in range(2):
            p = [center_a[i], center_b[i]]
            # Posortuj pozycje, aby kolejność koordynatów była rosnąca.
            p.sort()
            p.append(block_center[i])
            # Dodaj środek

            axis_changed = p[0] != p[1]

            if axis_changed and axis is not None:
                # W moim przypadku jeżeli nastąpiła zmiana osi to oznacza, że przeszedł przez środek
                return True
            elif axis_changed:
                axis = p

        crossed_center = axis[0] <= axis[2] <= axis[1]
        return crossed_center


    
    def distance_to(self, position : Position, target):
        graph = self.graph

        def w(start, end, _):
            # Można dać praktycznie nieskończony koszt jeżeli wracamy z wierzchołka wirtualnego
            stype : NodeTypes = graph.nodes[start]['node_type']
            etype : NodeTypes = graph.nodes[end]['node_type']
            if stype == etype == NodeTypes.VIRTUAL:
                raise ValueError('Nie można iść z wirtualnego do wirtualnego')
            elif stype == NodeTypes.VIRTUAL:
                return 1024
            elif etype == NodeTypes.VIRTUAL:
                return 0
            else:
                return 1
        
        shortest = 1024
        try:
            shortest = nx.shortest_path_length(graph, position, target, w)
        except:
            pass

        return min(shortest, 1024)

    def _distance_to_closest_by_neighbor(self, origin : Position, neighbor : Position, master):
        
        graph = self.graph
        graph.remove_edge(origin, neighbor)


        shortest = self.distance_to(neighbor, master) + 1


        self.graph.add_edge(origin, neighbor)
        return min(shortest, 1024)

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

    def get_closest_dist_for_dirs(self, state : GameState, origin : Position, master = 'nc', normalize = True):
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
            if not isinstance(neighbor, tuple): continue
            dir = self.from_which_direction(neighbor, origin)
            # Koszt dojścia do wirtualnego wierzchołka zastępuje nam koszt zaoszczędzony przez ucięcie krawędzi origin-neighbor
            ret[order.index(dir)] = self._distance_to_closest_by_neighbor(origin, neighbor, master)
        # Znormalizuj (Podzielenie przez 1024 może być i tak dłuższej ścieżki nie będzie oraz float dobrze dzieli przez potęgi 2)
        
        if normalize:
            for i in range(len(ret)):
                ret[i] = 1/(ret[i])

        return ret
    
    def weight_select_nodes(self, ignored : Set[NodeTypes]):
        """zwraca funkcję pozwalającą na ignorowanie odpowiednich wierzchołków podczas szukania najkrótszej ścieżki.  

        :param ignored: Ignorowane wierzchołki.
        :type ignored: Set[NodeTypes]
        """

        def weight(a,b,_):
            g = self.graph

            t1 : NodeTypes = g.nodes[a]['node_type']
            t2 : NodeTypes = g.nodes[b]['node_type']

            if t1 in ignored or t2 in ignored:
                return 1024
            else:
                return 1

        return weight


            
    
    def navigate_to_position(self, origin : Position, target : Position, origin_dir = Direction.UP, closer0 = True, normalize = True) -> List[float]:
        """Pozwala na nawigację do danej pozycji. Zwraca podobną wartość, co get_closest_not_collected

        :param origin: Start
        :type origin: Position
        :param target: Cel
        :type target: Position
        :param origin_dir: Kierunek w którym zwrócona lista ma być uporządkowana
        :type origin_dir: Direction, opcjonalny
        :param closer0: Czy bliższy cel ma mieć wartość bliższą zeru.
        :type closer0: bool, opcjonalny
        :return: Lista złożona z 4 floatów. Tym większa wartość tym dany obiekt bliżej
        :rtype: List[float]
        """
        order = [
            Direction.LEFT,
            Direction.RIGHT,
            Direction.UP,
            Direction.DOWN
        ]

        for i in range(len(order)):
            order[i] = order[i].add_rotation(origin_dir)

        
        ret = [1024] * 4

        neighbors = list(self.graph.neighbors(origin))
        for neighbor in neighbors:
            if not isinstance(neighbor, tuple): continue
            dir = self.from_which_direction(neighbor, origin)

            i = order.index(dir)
            weight_f = self.weight_select_nodes(set([NodeTypes.VIRTUAL]))
            self.graph.remove_edge(origin, neighbor)
            try:
                ret[i] = nx.shortest_path_length(self.graph, neighbor, target, weight=weight_f) + 1
            except:
                self._logger.info(f'Brak ścieżki z {origin} do {target} przez {neighbor}')
            self.graph.add_edge(origin, neighbor)

        if normalize:
            for i in range(len(ret)):
                ret[i] = 1/(ret[i])

            if not closer0:
                for i in range(len(ret)): ret[i] = 1 - ret[i]

        return ret