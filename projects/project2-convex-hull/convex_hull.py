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

    def top_clock_walk(self,r_point,l_point,r_points,l_points):
        count = 0
        compare_point_l = l_point
        compare_point_r = r_point
        i = 0
        j = l_points.index(l_point)

        while count != 2:
            change_in_r = change_in_l = True

            r_point_1 = r_points[i]
            r_point_2 = r_points[(i + 1) % len(r_points)]

            deltaY, deltaX = r_point_1.y() - compare_point_l.y(), r_point_1.x() - compare_point_l.x()
            slope_1 = deltaY/deltaX   

            deltaY, deltaX = r_point_2.y() - compare_point_l.y(), r_point_2.x() - compare_point_l.x()
            slope_2 = deltaY/deltaX 

            if(slope_1 < slope_2):
                i = (i + 1) % len(r_points)
                compare_point_r = r_point_2
                count = 0
            else:
                change_in_r = False
                
            l_point_1 = l_points[(j) % len(l_points)]
            l_point_2 = l_points[(j - 1) % len(l_points)]

            deltaY, deltaX = l_point_1.y() - compare_point_r.y(), l_point_1.x() - compare_point_r.x()
            slope_1 = deltaY/deltaX   

            deltaY, deltaX = l_point_2.y() - compare_point_r.y(), l_point_2.x() - compare_point_r.x()
            slope_2 = deltaY/deltaX 

            if(slope_1 > slope_2):
                j = (j - 1) % len(l_points)
                compare_point_l = l_point_2
                count = 0
            else:
                change_in_l = False
            
            if(not change_in_r and not change_in_l):
                count+=1

        top_r_point = compare_point_r
        top_l_point = compare_point_l

        return top_r_point, top_l_point

    def low_clock_walk(self,r_point,l_point,r_points,l_points): 
        count = 0
        compare_point_l = l_point
        compare_point_r = r_point
        i = 0
        j = l_points.index(l_point)

        while count != 2:
            change_in_r = change_in_l = True

            r_point_1 = r_points[i]
            r_point_2 = r_points[(i - 1) % len(r_points)]

            deltaY, deltaX = r_point_1.y() - compare_point_l.y(), r_point_1.x() - compare_point_l.x()
            slope_1 = deltaY/deltaX   

            deltaY, deltaX = r_point_2.y() - compare_point_l.y(), r_point_2.x() - compare_point_l.x()
            slope_2 = deltaY/deltaX 

            if(slope_1 > slope_2):
                i = (i - 1) % len(r_points)
                compare_point_r = r_point_2
            else:
                change_in_r = False
                
            l_point_1 = l_points[(j) % len(l_points)]
            l_point_2 = l_points[(j + 1) % len(l_points)]

            deltaY, deltaX = l_point_1.y() - compare_point_r.y(), l_point_1.x() - compare_point_r.x()
            slope_1 = deltaY/deltaX   

            deltaY, deltaX = l_point_2.y() - compare_point_r.y(), l_point_2.x() - compare_point_r.x()
            slope_2 = deltaY/deltaX 

            if(slope_1 < slope_2):
                j = (j + 1) % len(l_points)
                compare_point_l = l_point_2
            else:
                change_in_l = False
            
            if(not change_in_r and not change_in_l):
                count+=1

        low_r_point = compare_point_r
        low_l_point = compare_point_l

        return low_r_point, low_l_point

    def add_right_side(self,top_point,low_point,points):
        #top to bottom
        side_points = []

        i = points.index(top_point)
        while True:
            point_1 = points[i]
            point_2 = points[(i + 1) % len(points)]
            side_points.append((point_1,point_2))
            if(point_2 == low_point):
                break
            else:
                i = (i + 1) % len(points)
 
        return side_points
    
    def add_left_side(self,top_point,low_point,points):
        # bottom to top
        side_points = []

        i = points.index(low_point)
        while True:
            point_1 = points[i]
            point_2 = points[(i - 1) % len(points)]
            side_points.append((point_1,point_2))
            if(point_2 == top_point):
                break
            else:
                i = (i - 1) % len(points)
 
        return side_points

    def combine(self,l_points,r_points):

        l_point = max(l_points, key=lambda point: point.x()) #rightmost point in l_hull
        r_point = r_points[0] #leftmost point in the r_hull

        top_r,top_l = self.top_clock_walk(r_point,l_point,r_points,l_points)
        low_r,low_l = self.low_clock_walk(r_point,l_point,r_points,l_points)


        # must be Tl, TR, BR, BL  in clockwise order
        points = []
        points.extend([top_l,top_r])
        points.extend(self.add_right_side(top_r,low_r,r_points))
        points.append([low_r,low_l])
        points.extend(self.add_left_side(top_l,low_l,l_points))

        return points
    
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
        # polygon.addlines

        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon,RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
