from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
    from PyQt6.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
    def __init__( self):
        super().__init__()
        self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line,color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self,line,color):
        self.showTangent(line,color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon,color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self,polygon):
        self.view.clearLines(polygon)

    def showText(self,text):
        self.view.displayStatusText(text)

    def remove_inner(upper,lower):
        return None

    def find_tangent(self,points):
        return None

    def combine(self,l_hull,r_hull):
        upper = find_tangent(l_hull,r_hull)
        lower = find_tangent(l_hull,r_hull)
        convex_hull = remove_inner(upper,lower)
        return convex_hull
    
    def split_list(points):
        half = len(points)//2
        return points[:half], points[half:]
    
    def divide_and_conquer(self, points):
        if len(points) <= 3:
            return [QLineF(points[i], points[(i + 1) % len(points)]) for i in range(len(points))] #smallest subhull
        
        l_points,r_points = self.split_list(points)

        l_hull = self.divide_and_conquer(l_points)
        r_hull = self.divide_and_conquer(r_points)
    
        return combine(l_hull,r_hull)

        '''
        - i have a list of points ordered from leftmost to rightmost
        - I split that list into subhulls until I have two subhulls of a size <= 3
        - with those two subhulls, I find the upper and lower tangent to find the convex hull
        - then I continue the clockwise/counter clockwise movement
        - Continue the clockwise position, and only keep the points that are between the top and lower tangent points 
        - and remove everything else.
        - so for the left sub-hull, start going counter clockwise until you hit upper tangent point 
        - and then continue counter clockwise until you hit lower tangent point. Remove al other points
        '''



# This is the method that gets called by the GUI and actually executes
# the finding of the hull
    def compute_hull( self, points, pause, view):
        self.pause = pause
        self.view = view
        assert( type(points) == list and type(points[0]) == QPointF )

        # Time Complexity: O(n log n)
        points.sort(key=lambda point: point.x())

        t2 = time.time()

        t3 = time.time()

        polygon = self.divide_and_conquer(points)

        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon,RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
