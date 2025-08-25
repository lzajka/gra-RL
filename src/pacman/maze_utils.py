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
        m = max([n[1] for n in graph.nodes]) + 1

        for n in graph.nodes:
            pos[n] = (n[0], m - n[1])

        e_cleared = [e for e in graph.edges if graph.edges[e].get('cleared')]
        e_not_cleared = [e for e in graph.edges if not graph.edges[e].get('cleared')]
        n_cleared = [n for n in graph.nodes if graph.nodes[n].get('cleared')]
        n_not_cleared = [n for n in graph.nodes if not graph.nodes[n].get('cleared')]
        
        interesting_nodes = self.__class__._find_interesting_nodes(graph)

        nx.draw_networkx_nodes(graph, pos, nodelist=interesting_nodes, node_color='black', node_size=400, ax=ax)
        nx.draw_networkx(graph, pos, with_labels=True, nodelist=n_not_cleared, edgelist=e_not_cleared, edge_color='r', node_color='r', width=3, ax=ax)
        nx.draw_networkx(graph, pos, with_labels=True, nodelist=n_cleared, edgelist=e_cleared, edge_color='g', node_color='g', width=2, ax=ax)
    
    @staticmethod
    def _find_interesting_nodes(graph):
        edges = list(graph.edges)
        nodes = list(graph.nodes)

        ret = set()

        for e in edges:
            if not graph.edges[e]['cleared']:
                ret.add(e[0])
                ret.add(e[1])
        
        for n in nodes:
            if not graph.nodes[n]['cleared']:
                ret.add(n)

        return list(ret)
        

    def _init_graph(self, maze : Maze) -> nx.Graph:
        """Metoda tworzy graf przedstawiający jakie skrzyżowania są ze sobą połączone.

        :param maze: Labirynt do przekształcenia w graf 
        :type Maze: Maze
        :return: Powstały graf
        :rtype: Graph
        """
        # Przyszykuj zmienne
        maze_size = maze
        self.graph = nx.Graph()
        stack : Deque[Tuple[Position, Position]] = deque()     # Dequeue używana jako stos
        visited : set = set()       # visited
        # Znajdź pierwsze lepsze skrzyżowanie
        initial_node = self._find_initial_intersection(maze)
        # Dodaj skrzyżowanie
        self.graph.add_node(initial_node)
        visited.add(initial_node)        
        # Znajdź sąsiadów
        neighbors = maze.get_neighbors(initial_node)
        # Dodaj ich na stos      
        for n in neighbors:
            stack.append((
                initial_node,       # Początek
                n,                  # następny wierzchołek wierzchołek
                set([initial_node]),# Zawarte wierzchołki oprócz następnego

            ))


        while len(stack) > 0:
            origin : Position
            position : Position
            nodes : Set
            origin, position, nodes = stack.pop()


            was_visited = position in visited
            is_intersection = maze.is_intersection(position)


            if is_intersection:
                nodes.remove(origin)
                self.graph.add_nodes_from([origin, position], cleared=True)
                self.graph.add_edge(origin, position, contains=nodes, cleared=True, length=len(nodes))
                self._assign_edges2positions(self.graph, maze, (origin, position))

                nodes = set()
                origin = position

            if was_visited:
                continue
            
            nodes.add(position)
            neighbors = maze.get_neighbors(position)
            visited.add(position)
            for i in neighbors:
                if origin != i: stack.append((origin, i, nodes.copy()))

        self._detect_cleared()

    def _detect_cleared(self):
        from src.pacman.maze.objects import Point
        objects = self._maze.get_all_objects()
        for s in objects:
            for o in s:
                if isinstance(o, Point): 
                    pos = o.get_position()
                    is_intersection = self._maze.is_intersection(pos)

                    if is_intersection:
                        self.graph.nodes[pos]['cleared'] = False
                    else:
                        e = self._pos2edge[pos]
                        self.graph.edges[e]['cleared'] = False

    def _detect_energizers(self, maze : Maze) -> List[Energizer]:
        objects = maze.get_all_objects()
        for s in objects:
            for o in s:
                if isinstance(o, Energizer): self._energizers.append(o)


    def _assign_edges2positions(self, graph: nx.Graph, maze : Maze, edge):
        positions = graph.edges[*edge].get('contains')
        for pos in positions:
            self._pos2edge[pos] = edge
    
    def _find_initial_intersection(self, maze : Maze) -> Position:
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
                if maze.is_intersection(pos):
                    return pos

    def update(self, pacman_pos : Position):


        pacman_pos = self._maze.handle_outside_positions(pacman_pos)
        if self._prev_pacman_pos == pacman_pos:
            return
        edge = None
        pacman_on_intersection = self._maze.is_intersection(pacman_pos)

        if pacman_on_intersection:
            self.graph.nodes[pacman_pos]['cleared'] = True
        else:
            edge = self._pos2edge[pacman_pos]
            self.graph.edges[edge]['cleared'] = True

    def get_associated_edges(self, pos : Position) -> Tuple[Position, Position]:
        """Metoda zwraca krawędź na której dany punkt jest zawarty. 
        Jeżeli punkt jest skrzyżowaniem zwracane są wszystkie krawędzie w których on się znajduje.

        :param pos: Pozycja
        :type pos: Position
        :return: Lista krawędzi
        :rtype: List[Tuple[Position, Position]]
        """
        return self._pos2edge[pos]
    
    def get_energizers(self) -> List[Energizer]:
        return self._energizers

    def normalize_position(self, position : Position):
        maze_size = self._maze.get_size()
        return float(position[0] / maze_size[0]), float(position[1] / maze_size[1])
    

    def get_distance_to_closest_not_cleared(self, origin : Position, neighbor : Position):
        
        if neighbor not in self.graph.nodes:
            raise ValueError("Punkt startowy nie jest węzłem grafu (Podaj skrzyżowanie).")
        
        # 1. Sprawdź czy krawędź między origin i position jest oczyszczona
        if not self.graph.edges[origin, neighbor]['cleared']:
            # Jeżeli nie wystarczy zmiana kierunku
            return 0


        # Nie interesuje mnie to, czy na wierzchołku startowym znajduje się punkt, ponieważ jest to skrzyżowanie, które tak, czy tak aktywuje
        dist_1 = self.graph.edges[origin, neighbor]['length']


        
        graph = self.graph.copy()

        # Zapobiegnij powracaniu
        graph.remove_edge(origin, neighbor)

        # Szukam najkrótszej możliwej ścieżki do najbliższego punktu który ma nieodwiedzoną ścieżkę.
        # Aby to zrobić utworzę wirtualny punkt do którego wszystkie te wierzchołki będą połączone krawędzią o długości 0

        # Oznaczam wszystkie interesujące mnie wierzchołki
        interesting_nodes = self.__class__._find_interesting_nodes(graph)
        for n in interesting_nodes:
            graph.add_edge(n, 'v', length=0)
        
        @staticmethod
        def distance_calc(start, end, attributes : Dict):
            ret = 0
            # Jeżeli punktu nie ma w wierzchołku
            if graph.nodes[start]['cleared']: ret += 1

            ret += attributes['length']

            return ret
        dist_2 = 99999
        try:
            dist_2 = nx.shortest_path_length(graph, neighbor, 'v', distance_calc)
        except:
            pass
        
        ret = dist_1 + dist_2
        return ret

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

    def get_shortest_distances_from_intersection(self, state : GameState, origin : Position):
        """Metoda zwraca odległość od najbliższej nie odwiedzonej krawędzi w zależności od wyboru kierunku na skrzyżowaniu"""
        neighbours = self.graph.neighbors(origin)

        order = [
            Direction.LEFT,
            Direction.RIGHT,
            Direction.UP,
            Direction.DOWN
        ]

        for i in range(len(order)):
            order[i] = order[i].add_rotation(state.a_Pacman.direction)

        ret = [1024] * 4

        for neighbour in neighbours:
            dir = self.from_which_direction(neighbour, origin)
            e=neighbour, origin
            ret[order.index(dir)] = self.get_distance_to_closest_not_cleared(origin, neighbour)
        # Znormalizuj (Podzielenie przez 1024 może być i tak dłuższej ścieżki nie będzie oraz float dobrze dzieli przez potęgi 2)
        
        for i in range(len(ret)):
            ret[i] = 1/(ret[i]+1)

        return ret
