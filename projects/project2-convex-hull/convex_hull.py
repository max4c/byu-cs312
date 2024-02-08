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
import math

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
    rightmost = QPointF(0.0,0.0)

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

    def clock_compare(self,init_point,points,compare_point,clockwise):
        i = points.index(init_point)

        while True:
            point_1 = points[i]
            if(clockwise):
                point_2 = points[(i + 1) % len(points)]
            else:
                point_2 = points[(i - 1) % len(points)]
            
            deltaY, deltaX = point_1.y() - compare_point.y(), point_1.x() - compare_point.x()
            slope_1 = deltaY/deltaX   

            deltaY, deltaX = point_2.y() - compare_point.y(), point_2.x() - compare_point.x()
            slope_2 = deltaY/deltaX 

            if(clockwise):
                if(slope_1 > slope_2):
                    new_point = point_1
                    break
            else:
                if(slope_1 < slope_2):
                    new_point = point_1
                    break
            
            if(clockwise):
                i = (i + 1) % len(points)
            else:
                i = (i - 1) % len(points)

        return new_point

    def add_lines(self,top_point,low_point,points,clockwise):
        lines = []

        if(clockwise):
            i = points.index(top_point)
            for i in range(len(points)):
                point_1 = points[i]
                point_2 = points[(i + 1) % len(points)]
                line = QLineF(point_1,point_2)
                lines.append(line)
                if(point_2 == low_point):
                    break
        else:
            i = points.index(top_point)
            while True:
                point_1 = points[i]
                point_2 = points[(i - 1) % len(points)]
                line = QLineF(point_1,point_2)
                lines.append(line)
                if(point_2 == low_point):
                    break
                else:
                    i = (i - 1) % len(points)

        return lines



    def combine(self,l_points,r_points):

        l_point = max(l_points, key=lambda point: point.x()) #rightmost point in l_hull
        r_point = r_points[0] #leftmost point in the r_hull

        top_r_point = self.clock_compare(r_point,r_points,l_point,True)
        top_l_point = self.clock_compare(l_point,l_points,r_point,False)
        low_r_point = self.clock_compare(r_point,r_points,l_point,False)
        low_l_point = self.clock_compare(l_point,l_points,r_point,True)
        
        top_tan_line = QLineF(top_l_point,top_r_point)
        low_tan_line = QLineF(low_l_point,low_r_point)

        lines = []
        lines.append(top_tan_line)
        lines.append(low_tan_line)
        lines.extend(self.add_lines(top_r_point,low_r_point,r_points,True))
        lines.extend(self.add_lines(top_l_point,low_l_point,l_points,False))

        return lines
    
    def split_list(self,points):
        half = len(points)//2
        return points[:half], points[half:]

    def clockwise_angle(self,point,pivot):
        deltaX, deltaY = point.x() - pivot.x(), point.y() - pivot.y()
        if deltaX == 0:
            return float('-inf')  # or any other value that you see fit
        else:
            return deltaY/deltaX
    
    def divide_and_conquer(self,points):
        if len(points) <= 3:
            # sort into clockwise list
            pivot = points[0]
            points.sort(key=lambda point: self.clockwise_angle(point, pivot))
            return points
        
        l_points,r_points = self.split_list(points)

        l_points = self.divide_and_conquer(l_points)
        r_points = self.divide_and_conquer(r_points)
    
        return self.combine(l_points,r_points)



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
