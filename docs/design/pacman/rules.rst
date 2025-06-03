Zasady gry
==========
- Gra toczy się na planszy, która jest podzielona na komórki. Gracz porusza się po planszy, zbierając punkty i unikając duchów.
- Aktor może poruszać się w czterech kierunkach: góra, dół, lewo, prawo.
- Aktor nie może wykonywać ruchu w kierunku przeciwnym do kierunku w którym się porusza (są wyjątki).
- Aktor może wykonywać ruch tylko w kierunku, w którym jest wolna przestrzeń (tj. nie ma ściany).
- Jedyny przypadek, w którym aktor może i musi stanąć w miejscu, to gdy w kierunku w którym wcześniej się poruszał znajduje się ściana. W takim przypadku aktor nie może wykonać ruchu i pozostaje w tej samej komórce.
- Pozycja składa się z dwóch współrzędnych: x i y, które określają położenie aktora na planszy, gdzie x to współrzędna pozioma, a y to współrzędna pionowa.
   - Współrzędne są liczone od lewego górnego rogu planszy, gdzie (0, 0) to lewy górny róg, a (width-1, height-1) to prawy dolny róg.
   - Pozycja jest *dyskretna* - Aktor nie może znajdować się pomiędzy dwoma komórkami, zawsze zajmuje całkowicie jedną komórkę.
- Gracz startuje z określną liczbą żyć. 
   - W przypadku kolizji z duchem, gracz traci jedno życie i wraca do swojego punktu startowego.
   - Wyjątkiem jest sytuacja, gdy gracz zjada super punkt, wtedy duchy stają się wrażliwe i gracz może je zjeść, zdobywając dodatkowe punkty.
   - Gra kończy się, gdy gracz zbierze wszystkie punkty lub straci wszystkie życia.
  
=================
Zachowanie duchów
=================
.. plantuml:: ghost_behavior.puml
   :alt: Diagram stanów opisujący zachowanie duchów w grze Pacman.