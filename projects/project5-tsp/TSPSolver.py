#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))


import time
import numpy as np
from TSPClasses import *
import heapq
import itertools
import copy


class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution,
		time spent to find solution, number of permutations tried during search, the
		solution found, and three null values for fields not used for this
		algorithm</returns>
	'''

	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this
		algorithm</returns>
	'''

	def greedy( self,time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities().copy()
		ncities = len(cities)
		foundTour = False
		count = 1
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			cur_city = np.random.choice(cities)
			all_cities_visited = False
			hit_dead_end = False
			route = [cur_city]
			while not all_cities_visited:
				least_cost = np.inf
				next_city = None
				at_least_one_edge = False
				for city in cities:
					if city not in route:
						cur_cost = cur_city.costTo(city)
						if  cur_cost <= least_cost:
							at_least_one_edge = True
							least_cost = cur_cost
							next_city = city

				if least_cost == np.inf and len(route) != ncities:
					hit_dead_end = True
					break
				else:
					route.append(next_city)
					cur_city = next_city
	
				if len(route) == ncities:
					all_cities_visited = True
			if not hit_dead_end:
				bssf = TSPSolution(route)
				if bssf.cost < np.inf:
					foundTour = True
		
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count # total num of solutions
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results

	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints:
		max queue size, total number of states created, and number of pruned states.</returns>
	'''

	def initialMatrix(self, ncities,cities):
		#initial cost matrix
		matrix = np.zeros((ncities,ncities))
		lower_bound = 0

		for i in range(ncities):
			for j in range(ncities):
				if i != j:
					matrix[i][j] = cities[i].costTo(cities[j])
				else:
					matrix[i][j] = np.inf

		return matrix

	def reduceMatrix(self, matrix):
		ncities = len(matrix)

		# min by rows
		for i in range(ncities):
			min_val = np.inf
			indices_to_decrease = []
			for j in range(ncities):
				if matrix[i][j] != np.inf:
					indices_to_decrease.append(j)
					if matrix[i][j] < min_val:
						min_val = matrix[i][j]
			if min_val != 0:
				lower_bound += min_val
				for k in range(len(indices_to_decrease)):
					matrix[i][indices_to_decrease[k]] -= min_val


		# min by columns
		for j in range(ncities):
			min_val = np.inf
			indices_to_decrease = []
			for i in range(ncities):
				if matrix[i][j] != np.inf:
					indices_to_decrease.append(i)
					if matrix[i][j] < min_val:
						min_val = matrix[i][j]
			if min_val != 0:
				lower_bound += min_val
				for k in range(len(indices_to_decrease)):
					matrix[indices_to_decrease[k]][j] -= min_val
		
		return lower_bound, matrix

	def setRowCol2Infinity(self, matrix, row_index, col_index):
		for i in range(len(matrix[row_index])):
			matrix[row_index][i] = np.inf 
		for i in range(len(matrix)):
			matrix[i][col_index] = np.inf
		
		# check if the infinites removed the last chance to unvisited city in the reduce Matrix function
		# set row and col to infinity or delete row and col
		# keep track of what rows and cols set to inifinty or have reduced cost matrix return None if any min_vals are infinity or there are no min_vals


		return matrix


	def branchAndBound( self, time_allowance=60.0 ):
		# create initial partial path
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		init_matrix = self.initialMatrix(ncities,cities)
		lower_bound, matrix = self.reduceMatrix(init_matrix)
		results = self.greedy()
		bssf = results['soln']
		start_city = cities[0]
		path = [start_city]
		partial_path = PartialPath(lower_bound, 0.0, 0, path, matrix)

		#push initial partial path into heap
		priority_queue = []
		heapq.heappush(priority_queue, partial_path)

		start_time = time.time()
		while priority_queue and time.time()-start_time < time_allowance:
			parent = heapq.heappop(priority_queue)
			parent_index = parent.index 
			if parent.lower_bound < bssf.cost:
				for child_index, child in enumerate(cities):
					if child not in parent.path:
						parent.path[-1].costTo(child)
						child_matrix = copy.deepcopy(parent.matrix)
						child_path = copy.copy(parent.path)
						child_matrix = self.setRowCol2Infinity(child_matrx, parent_index, child_index)
						if child_matrix is not None:
							print("reduce the matrix, create new cost, create new partial path object, add to heap")
						#use parent matrix to compute lowerbound

		



	


	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number of solutions found during search, the
		best solution found.  You may use the other three field however you like.
		algorithm</returns>
	'''

	def fancy( self,time_allowance=60.0 ):
		pass
