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
        compare_point_l = l_point
        compare_point_r = r_point
        i = r_points.index(r_point) # r_index
        j = l_points.index(l_point) # l_index
        change_in_r = True
        change_in_l = True

        while change_in_r or change_in_l:
            change_in_r = False
            change_in_l = False

            while True:
                r_point_1 = r_points[i]
                r_point_2 = r_points[(i + 1) % len(r_points)]

                deltaY, deltaX = r_point_1.y() - compare_point_l.y(), r_point_1.x() - compare_point_l.x()
                slope_1 = deltaY/deltaX   

                deltaY, deltaX = r_point_2.y() - compare_point_l.y(), r_point_2.x() - compare_point_l.x()
                slope_2 = deltaY/deltaX 

                if slope_1 < slope_2:
                    i = (i + 1) % len(r_points)
                    compare_point_r = r_point_2
                    change_in_r = True
                else:
                    break

            #counter clockwise
            while True:        
                l_point_1 = l_points[(j) % len(l_points)]
                l_point_2 = l_points[(j - 1) % len(l_points)]

                deltaY, deltaX = l_point_1.y() - compare_point_r.y(), l_point_1.x() - compare_point_r.x()
                slope_1 = deltaY/deltaX  

                deltaY, deltaX = l_point_2.y() - compare_point_r.y(), l_point_2.x() - compare_point_r.x()
                slope_2 = deltaY/deltaX 

                if slope_1 > slope_2:
                    j = (j - 1) % len(l_points)
                    compare_point_l = l_point_2
                    change_in_l = True
                else:
                    break
                
        return compare_point_r, compare_point_l


    def low_clock_walk(self,r_point,l_point,r_points,l_points): 
        compare_point_l = l_point
        compare_point_r = r_point
        i = r_points.index(r_point)
        j = l_points.index(l_point)
        change_in_r = True
        change_in_l = True

        while change_in_r or change_in_l:
            change_in_r = False
            change_in_l = False

            while True:   
                r_point_1 = r_points[i]
                r_point_2 = r_points[(i - 1) % len(r_points)]

                deltaY, deltaX = r_point_1.y() - compare_point_l.y(), r_point_1.x() - compare_point_l.x()
                slope_1 = deltaY/deltaX 

                deltaY, deltaX = r_point_2.y() - compare_point_l.y(), r_point_2.x() - compare_point_l.x()
                slope_2 = deltaY/deltaX

                if slope_1 > slope_2:
                    i = (i - 1) % len(r_points)
                    compare_point_r = r_point_2
                    change_in_r = True
                else:
                    break

            #clockwise
            while True:   
                l_point_1 = l_points[(j) % len(l_points)]
                l_point_2 = l_points[(j + 1) % len(l_points)]

                deltaY, deltaX = l_point_1.y() - compare_point_r.y(), l_point_1.x() - compare_point_r.x()
                slope_1 = deltaY/deltaX 

                deltaY, deltaX = l_point_2.y() - compare_point_r.y(), l_point_2.x() - compare_point_r.x()
                slope_2 = deltaY/deltaX

                if slope_1 < slope_2:
                    j = (j + 1) % len(l_points)
                    compare_point_l = l_point_2
                    change_in_l = True
                else:
                    break
                

        return compare_point_r, compare_point_l


    def combine(self,l_points,r_points):

        l_point = max(l_points, key=lambda point: point.x()) #rightmost point in l_hull
        r_point = r_points[0] #leftmost point in the r_hull

        top_r,top_l = self.top_clock_walk(r_point,l_point,r_points,l_points)
        low_r,low_l = self.low_clock_walk(r_point,l_point,r_points,l_points)

        top_r_index = r_points.index(top_r)
        low_r_index = r_points.index(low_r)
        top_l_index = l_points.index(top_l)
        low_l_index = l_points.index(low_l)

        # must be Tl, TR, BR, BL in clockwise order starting with the leftmost point
        points = l_points[:top_l_index+1]
        if low_r_index > top_r_index:
            points = points + r_points[top_r_index:low_r_index+1]
        elif low_r_index == top_r_index:
                points.append(r_points[low_r_index])
        else:
            points = points + r_points[top_r_index:] + r_points[:low_r_index+1] 
        if low_l_index != 0:
            points = points + l_points[low_l_index:]

        return points
    
    def split_list(self,points):
        half = len(points)//2
        return points[:half], points[half:]
    
    def divide_and_conquer(self,points):
        if len(points) <= 3:
            if len(points) == 2:
                return points
            # sort into clockwise list
            pivot = points[0]

            dx_1 = points[1].x() - pivot.x()
            dy_1 = points[1].y() - pivot.y()

            dx_2 = points[2].x() - pivot.x()
            dy_2 = points[2].y() - pivot.y()

            if (dy_2/dx_2) > (dy_1/dx_1):
                temp  = points[2]
                points[2] = points[1]
                points[1] = temp

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

        t1 = time.time()

        # Time Complexity: O(n log n)
        points.sort(key=lambda point: point.x())
        polygon_points = self.divide_and_conquer(points)
        polygon = [QLineF(polygon_points[i], polygon_points[(i+1) % len(polygon_points)]) for i in range(len(polygon_points))]


        t2 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon,RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t2-t1))
