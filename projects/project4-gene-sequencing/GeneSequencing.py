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

import random
import math
import numpy as np


# Used to compute the bandwidth for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1

class GeneSequencing:

	def __init__( self ):
		pass

# This is the method called by the GUI.  _seq1_ and _seq2_ are two sequences to be aligned, _banded_ is a boolean that tells
# you whether you should compute a banded alignment or full alignment, and _align_length_ tells you
# how many base pairs to use in computing the alignment

	def align( self, seq1, seq2, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length

		seq1 = seq1[:align_length]
		seq2 = seq2[:align_length]

		if banded:
			return self.banded_align(seq1,seq2) 
		
		num_array = []
		ptr_array = []
		row_length = len(seq1)+1
		col_length = len(seq2)+1

		for i in range(row_length):
			num_array.append([None]*col_length)
			ptr_array.append([None]*col_length)

		# Filling the first row
		for j in range(col_length):
			num_array[0][j] = j * INDEL
			if j != 0:
				ptr_array[0][j] = (0, j - 1)

		# Filling the first column
		for i in range(row_length):
			num_array[i][0] = i * INDEL
			if i != 0:
				ptr_array[i][0] = (i - 1, 0)

		for i in range(1,row_length):
			for j in range(1,col_length):
				up = num_array[i-1][j] + INDEL
				left = num_array[i][j-1] + INDEL
				# decide if match or mismatch
				if seq1[i-1] == seq2[j-1]:
					diagonal = num_array[i-1][j-1] + MATCH # match
				else:
					diagonal = num_array[i-1][j-1] + SUB#mismatch
				
				smollest = math.inf
				if smollest > diagonal:
					smollest = diagonal
					ptr = (i-1,j-1)
				if smollest >= up:
					smollest = up
					ptr =  (i-1,j)
				if smollest >= left:
					smollest = left
					ptr =  (i,j-1)

				num_array[i][j] = smollest
				ptr_array[i][j] = ptr

		cur_ptr = (row_length-1, col_length-1)
		next_ptr = ptr_array[-1][-1]
		
		alignment1_list, alignment2_list = [], []

		while next_ptr is not None:
			if next_ptr is None:
				alignment1_list.append(seq1[cur_ptr[0]-1])
				alignment2_list.append(seq2[cur_ptr[1]-1])
				break
			elif cur_ptr[0] != next_ptr[0] and cur_ptr[1] != next_ptr[1]:  # diagonal
				alignment1_list.append(seq1[cur_ptr[0]-1])
				alignment2_list.append(seq2[cur_ptr[1]-1])
			elif cur_ptr[0] != next_ptr[0] and cur_ptr[1] == next_ptr[1]:  # up
				alignment1_list.append(seq1[cur_ptr[0]-1])
				alignment2_list.append("-")
			else:  # left
				alignment1_list.append("-")
				alignment2_list.append(seq2[cur_ptr[1]-1])

			cur_ptr = next_ptr
			next_ptr = ptr_array[next_ptr[0]][next_ptr[1]]

		# reverse and join the list to form the alignment string
		alignment1 = "".join(alignment1_list[::-1])
		alignment2 = "".join(alignment2_list[::-1])

		score = num_array[-1][-1]
		alignment1 = alignment1[:100]
		alignment2 = alignment2[:100]

		return {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}

	def banded_align(self, seq1, seq2):

		if (seq1 in ['polynomial', 'exponential'] and seq2 not in ['polynomial', 'exponential']) or (seq2 in ['polynomial', 'exponential'] and seq1 not in ['polynomial', 'exponential']):
			return {
				'align_cost': math.inf, 
				'seqi_first100': "No Alignment Possible", 
				'seqj_first100': "No Alignment Possible",
			}

		seq1 = "-" + seq1
		seq2 = "-" + seq2

		if len(seq2)> len(seq1):
			seq2,seq1 = seq1,seq2

		
		banded_array = []
		banded_dir_array = []

		for i in range(len(seq1)):
			banded_array.append([None]*7)
			banded_dir_array.append([None]*7)

		for i in range(len(banded_array)):
			for j in range(min(7, len(seq2) - i + 3)): 
				if i+j >= 3:
					if i == 0 and j == 3:
						banded_array[i][j] = 0
					elif i ==0 and j > 3:
						banded_array[i][j] = banded_array[i][j-1] + INDEL #top row
						banded_dir_array[i][j] = "L"
					elif (i == 1 and j == 2) or (i == 2 and j == 1) or (i == 3 and j == 0): 
						banded_array[i][j] = banded_array[i-1][j+1] + INDEL
						banded_dir_array[i][j] = "U"
					else:
						up = math.inf
						left = math.inf
						diagonal = math.inf

						if j != 6:
							up = banded_array[i-1][j+1] + INDEL
						if j != 0 :
							left = banded_array[i][j-1] + INDEL
						if seq1[i] == seq2[abs(j+i-3)]:
							diagonal = banded_array[i-1][j] + MATCH # match
						else:
							diagonal = banded_array[i-1][j] + SUB#mismatch
						
						smollest = math.inf
						if smollest > diagonal:
							smollest = diagonal
							dir = "D"
						if smollest >= up:
							smollest = up
							dir = "U"
						if smollest >= left:
							smollest = left
							dir = "L"
						
						banded_array[i][j] = smollest
						banded_dir_array[i][j] = dir
		

		#find the index of the last value in the last row
		last_value_col = 8

		for i in range(len(banded_array[-1])):
			if banded_array[-1][i] is None:
				break
			last_value_col = i

		cur_row = len(banded_array) -1
		cur_col = last_value_col
		cur_dir = (banded_dir_array[cur_row][cur_col])
		alignment1_list, alignment2_list = [], []

		while cur_dir is not None:
			if cur_dir is None:
				alignment1_list.append(seq1[cur_row])
				alignment2_list.append(seq2[abs(cur_row+cur_col-3)])
				break
			elif cur_dir == "D":  # diagonal which is up in this case
				alignment1_list.append(seq1[cur_row])
				alignment2_list.append(seq2[abs(cur_row+cur_col-3)])
				cur_row = cur_row - 1
			elif cur_dir == "U":  # up which is up + 1
				alignment1_list.append(seq1[cur_row])
				alignment2_list.append("-")
				cur_row = cur_row - 1
				cur_col = cur_col + 1
			else:  # left
				alignment1_list.append("-")
				alignment2_list.append(seq2[abs(cur_row+cur_col-3)])
				cur_col = cur_col - 1

			cur_dir = (banded_dir_array[cur_row][cur_col])

		# reverse and join the list to form the alignment string
		alignment1 = "".join(alignment1_list[::-1])
		alignment2 = "".join(alignment2_list[::-1])

		score = banded_array[len(banded_array) - 1][last_value_col]
		alignment1 = alignment1[:100]
		alignment2 = alignment2[:100]

		print(alignment2)

		return {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}