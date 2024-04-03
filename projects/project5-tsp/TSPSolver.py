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

	def reduceMatrix(self, matrix, init_bound, deleted_rows=None, deleted_cols=None):
		ncities = len(matrix)
		valid_matrix = True
		lower_bound = init_bound
		if deleted_rows is None:
			deleted_rows = []
		if deleted_cols is None:
			deleted_cols = []

		# min by rows
		for i in range(ncities):
			if i not in deleted_rows:
				min_val = np.inf
				indices_to_decrease = []
				for j in range(ncities):
					if j not in deleted_cols:
						if matrix[i][j] < min_val:
							min_val = matrix[i][j]
						indices_to_decrease.append(j)
				if min_val != np.inf:
					lower_bound += min_val
					for index in indices_to_decrease:
						matrix[i][index] -= min_val
				else:
					valid_matrix = False

		# min by columns
		for j in range(ncities):
			if j not in deleted_cols:
				min_val = np.inf
				indices_to_decrease = []
				for i in range(ncities):
					if i not in deleted_rows:
						if matrix[i][j] < min_val:
							min_val = matrix[i][j]
						indices_to_decrease.append(i)
				if min_val != np.inf:
					lower_bound += min_val
					for index in indices_to_decrease:
						matrix[index][j] -= min_val
				else:
					valid_matrix = False
		
		return lower_bound, matrix, valid_matrix

	def markCityAsVisited(self, matrix, row_index, col_index):
		cost_of_new_edge = matrix[row_index][col_index]
		valid_edge = True

		if cost_of_new_edge == np.inf:
			valid_edge = False

		if valid_edge:
			for i in range(len(matrix[row_index])):
				matrix[row_index][i] = np.inf 
			for i in range(len(matrix)):
				matrix[i][col_index] = np.inf
		
		return matrix, cost_of_new_edge, valid_edge


	def branchAndBound( self, time_allowance=60.0 ):
		# create initial partial path
		results = {}
		max_queue_size = 0
		num_states_created = 0
		num_states_pruned = 0
		count = 0

		cities = self._scenario.getCities()
		ncities = len(cities)
		init_matrix = self.initialMatrix(ncities,cities)
		lower_bound = 0
		lower_bound, matrix, valid_matrix = self.reduceMatrix(init_matrix, lower_bound)
		results = self.greedy()
		bssf = results['soln']
		start_city = cities[0]
		path = [start_city]
		partial_path = PartialPath(lower_bound, 0, path, matrix)

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
						child_matrix = copy.deepcopy(parent.matrix)
						child_path = copy.copy(parent.path)
						child_deleted_rows = copy.copy(parent.deleted_rows)
						child_deleted_cols = copy.copy(parent.deleted_cols)
						valid_edge = False
						valid_matrix = False
						num_states_created += 1

						child_matrix, cost_of_new_edge, valid_edge = self.markCityAsVisited(child_matrix, parent_index, child_index)
						child_path.append(child)
						child_deleted_rows.append(parent_index)
						child_deleted_cols.append(child_index)
						
						if valid_edge:
							new_lower_bound, child_matrix, valid_matrix =self.reduceMatrix(child_matrix,parent.lower_bound + cost_of_new_edge,child_deleted_rows, child_deleted_cols)

						if valid_matrix:
							new_partial_path = PartialPath(new_lower_bound, child_index, child_path, child_matrix, child_deleted_rows, child_deleted_cols)
							heapq.heappush(priority_queue, new_partial_path)
							if len(priority_queue) > max_queue_size:
								max_queue_size = len(priority_queue)
						else:
							num_states_pruned += 1
						
						if len(child_path) == len(cities):
							new_solution = TSPSolution(child_path)
							if new_solution.cost < bssf.cost:
								bssf = new_solution
								count += 1

		if len(priority_queue) != 0:
			for state in priority_queue:
				if state.lower_bound > bssf.cost:
					num_states_pruned += 1

		end_time = time.time()
		results['cost'] = bssf.cost
		results['time'] = end_time - start_time
		results['count'] = count # total num of solutions
		results['soln'] = bssf
		results['max'] = max_queue_size
		results['total'] = num_states_created
		results['pruned'] = num_states_pruned
		return results


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
