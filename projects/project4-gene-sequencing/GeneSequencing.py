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
		
		num_array = []
		ptr_array = []
		row_length = len(seq1)+1
		col_length = len(seq2)+1

		for i in range(row_length):
			num_array.append([None]*col_length)
			ptr_array.append([None]*col_length)

		for i in range(row_length):
			for j in range(col_length):
				if i == 0 and j == 0:
					num_array[i][j] = 0
				elif i == 0 and j!=0:
					num_array[0][j] = num_array[0][j-1] + 5
					ptr_array[0][j] = (0,j-1)
					#ptr_array[0][j] = "L"
				elif i != 0 and j==0:
					num_array[i][0] = num_array[i-1][0] + 5
					ptr_array[i][0] = (i-1,0)
					#ptr_array[i][0] = "U"
				else:
					up = num_array[i-1][j] + 5
					left = num_array[i][j-1] + 5
					# decide if match or mismatch
					if seq1[i-1] == seq2[j-1]:
						diagonal = num_array[i-1][j-1] -3 # match
					else:
						diagonal = num_array[i-1][j-1] + 1 #mismatch
					
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
		alignment1 = ""
		alignment2 = ""

		while next_ptr != None:
			if cur_ptr[0] != next_ptr[0] and cur_ptr[1] != next_ptr[1]: # diagonal
				alignment1 = seq1[cur_ptr[0]-1] + alignment1
				alignment2 = seq2[cur_ptr[1]-1] + alignment2
			elif cur_ptr[0] != next_ptr[0] and cur_ptr[1] == next_ptr[1]: # up
				alignment1 = seq1[cur_ptr[0]-1] + alignment1
				alignment2 = "-" + alignment2
			else: # left
				alignment1 = "-" + alignment1
				alignment2 = seq2[cur_ptr[1]-1] + alignment2
			# update next and cur
			cur_ptr = next_ptr
			next_ptr = ptr_array[next_ptr[0]][next_ptr[1]]


		print(num_array)
###################################################################################################
# your code should replace these three statements and populate the three variables: score, alignment1 and alignment2
		score = random.random()*100;
		alignment1 = 'abc-easy  DEBUG:({} chars,align_len={}{})'.format(
			len(seq1), align_length, ',BANDED' if banded else '')
		alignment2 = 'as-123--  DEBUG:({} chars,align_len={}{})'.format(
			len(seq2), align_length, ',BANDED' if banded else '')
###################################################################################################

		return {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}
