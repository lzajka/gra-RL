from src.general.maze import Maze, Position
import networkx as nx
from copy import copy
from collections import deque, namedtuple
from typing import Deque, Tuple, List
from src.pacman.maze.objects import Energizer


class MazeUtils:
    """Klasa dodająca dodatkowe metody związane z analizą labiryntów
    """
    def __init__(self, state):
        self._state = state
        self._maze = state.maze
        self._pos2edge = dict()
        self._energizers : List[Energizer] = []
        self._init_graph(self._maze)
        self._detect_energizers(self._maze)
        self._prev_pacman_pos = (-1, -1)
    
    def debug_display(self):
        if self._prev_pacman_pos == (-1, -1):
            raise RuntimeError('MazeUtils musi zostać zaktualizowany przed wyświetleniem grafu.')

        
        import tkinter as tk
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.pyplot as plt
        
        root = tk.Tk()
        root.title('Labirynt jako graf')
        graph = self.graph
        f = plt.figure(figsize=(13,13), dpi=60)
        pos = {}
        m = max([n[1] for n in graph.nodes]) + 1

        for n in graph.nodes:
            pos[n] = (n[0], m - n[1])

        nx.draw_networkx(graph,pos, with_labels=True)
        visited_edges = [e for e in graph.edges if graph.edges[e].get('visited')]
        not_visited_edges = [e for e in graph.edges if not graph.edges[e].get('visited')]

        nx.draw_networkx(graph, pos, with_labels=True)
        nx.draw_networkx_edges(graph, pos, edgelist=not_visited_edges, edge_color='r', width=3)
        nx.draw_networkx_edges(graph, pos, edgelist=visited_edges, edge_color='g', width=2)
    

        canvas = FigureCanvasTkAgg(f, root)
        canvas.draw()
        canvas.get_tk_widget().pack()
        root.protocol('WM_DELETE_WINDOW', root.quit)
        root.mainloop()
        root.destroy()
    
        

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
            origin, position, nodes = stack.pop()


            was_visited = position in visited
            is_intersection = maze.is_intersection(position)


            if is_intersection:
                nodes.add(position)
                self.graph.add_edge(origin, position, contains=nodes, visited=False)
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

    def _detect_energizers(self, maze : Maze) -> List[Energizer]:
        objects = maze.get_all_objects()
        for s in objects:
            for o in s:
                if isinstance(o, Energizer): self._energizers.append(o)


    def _assign_edges2positions(self, graph: nx.Graph, maze : Maze, edge):
        positions = graph.edges[*edge].get('contains')
        for pos in positions:
            edges : List = self._pos2edge.get(pos, [])
            edges.append(edge)
            self._pos2edge[pos] = edges
    
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
        if len(self.get_associated_edges(pacman_pos)) == 1:
            edge = self.get_associated_edges(pacman_pos)[0]
        elif len(self.get_associated_edges(self._prev_pacman_pos)) == 1:
            edge = self.get_associated_edges(self._prev_pacman_pos)[0]
        else:
            raise ValueError("Nie można znaleźć krawędzi dla pacmana")

        self.graph.edges[*edge]['visited'] = True
        self._prev_pacman_pos = pacman_pos

    def get_associated_edges(self, pos : Position) -> List[Tuple[Position, Position]]:
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
    

