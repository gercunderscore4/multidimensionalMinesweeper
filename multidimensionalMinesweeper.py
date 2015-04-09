# FILE:    multidimensionalMinesweeper.py
# PURPOSE: Generalized minesweeper for any size or dimensions (up to computer limits)
# AUTHOR:  Geoffrey Card
# DATE:    2015-03-23 - 2015-04-08
# NOTES:   UI is TERRIBLE, almost unplayable, but the math works.
#          Works in Python 2.7 and 3
#          Run as script (see end of file) or import and use class
# TODO:   Solver
#         Pretty GUI

import random
import math

class Minefield:
	
	# n = number of dimensions
	# sizes = sizes in each dimension
	# bases = poducts of sizes
	# COVERED = 2*(3**n+1), marker for cell is covered
	# MINES = 3**n+1, marker for cell contains mine
	# field = the actual minefield
	# numberOfMines = number of mines
	# total = total number of cells in field
	# DIGITS = number of decimal digits necessary to represent numbers
	
	def __init__(self):
		self.n = 0
		self.sizes = []
		self.bases = []
		self.COVERED = 2
		self.MINE = 1
		self.field = []
		self.numberOfMines = 0
	
	# these must be used AFTER dimensions have been set
	def isCovered(self, cell):
		return cell >= self.COVERED
	
	def isMine(self, cell):
		return (cell % self.COVERED) >= self.MINE
	
	def isNumbered(self, cell):
		return 0 < (cell % self.COVERED) < self.MINE
	
	def isEmpty(self, cell):
		return 0 == (cell % self.COVERED)
	
	def isValid(pos):
		for i in range(self.n):
			if not (0 < pos[i] < self.sizes[i]):
				return False
		return True
	
	def getNumber(self, cell):
		return cell % self.MINE
	
	def getCellRec(self, currN, cell, pos):
		if currN < self.n:
			return self.getCellRec(currN+1, cell[pos[currN]], pos)
		else:
			return cell
	
	def getCell(self, pos):
		return self.getCellRec(0, self.field, pos)
	
	def setCellRec(self, currN, cell, pos, value):
		if currN < self.n:
			cell[pos[currN]] = self.setCellRec(currN+1, cell[pos[currN]], pos, value)
			return cell
		else:
			return value
	
	def setCell(self, pos, value):
		self.field = self.setCellRec(0, self.field, pos, value)
	
	def getDimensions(self):
		print('dimensions (1-inf):')
		self.n = int(input())
		self.MINE = 3**self.n+1
		self.COVERED = 2*self.MINE
		self.DIGITS = int(math.log10(3**self.n)+1)
	
	def setDimensions(self, newN):
		print('dimensions (1-inf):')
		print(newN)
		self.n = newN
		self.MINE = 3**self.n+1
		self.COVERED = 2*self.MINE
		self.DIGITS = math.log10(3**self.n)
	
	def getSizes(self):
		self.total = 1
		self.bases.append(self.total)
		for i in range(self.n):
			print('sizes %i of %i (4-inf):' % (i+1, self.n))
			self.sizes.append(int(input()))
			self.total *= self.sizes[i]
			self.bases.append(self.total)
	
	def setSizes(self, newSizes):
		self.total = 1
		self.bases.append(self.total)
		for i in range(self.n):
			print('sizes %i of %i (4-inf):' % (i+1, self.n))
			print(newSizes[i])
			self.sizes.append(newSizes[i])
			self.total *= self.sizes[i]
			self.bases.append(self.total)
	
	def getMines(self):
		print('number of mines (1-%i):' % (self.total-3**self.n))
		self.numberOfMines = int(input())
	
	def setMines(self, newNumberOfMines):
		print('number of mines (1-%i):' % (self.total-3**self.n))
		print(self.numberOfMines)
		self.numberOfMines = newNumberOfMines
	
	def validDimensions(self):
		return 1 <= self.n
	
	def validSizes(self):
		for i in range(self.n):
			if not (4 <= self.sizes[i]):
				return False
		return True
	
	def validMines(self):
		return 1 <= self.numberOfMines <= self.total-3**self.n
	
	def validPos(self, pos):
		for i in range(self.n):
			if not (pos[i] < self.sizes[i]):
				return False
		return True
	
	def buildEmptyFieldRec(self, currN):
		if currN < self.n:
			cell = [0 for i in range(self.sizes[currN])]
			for i in range(self.sizes[currN]):
				cell[i] = self.buildEmptyFieldRec(currN+1)
			return cell
		else:
			return self.COVERED
	
	def buildEmptyField(self):
		self.field = self.buildEmptyFieldRec(0)
	
	def displayCell(self, cell):
		if self.isCovered(cell):
			return '[' + (' '*self.DIGITS) + ']'
		elif self.isEmpty(cell):
			return '[' + (' '*(self.DIGITS-1)) + '0' + ']'
		elif self.isNumbered(cell):
			return '[' + (('%%%ii' % self.DIGITS) % cell) + ']'
		elif self.isMine(cell):
			return '[' + ('*'*self.DIGITS) + ']'
		else:
			return '[' + ('?'*self.DIGITS) + ']'
	
	# horizontal is even
	def displayRecHoriz(self, currN, pos):
		if currN % 2 != 0:
			return ''
		if currN > 0:
			line = ''
			for i in range(self.sizes[currN]):
				pos[currN] = i
				line += self.displayRecHoriz(currN-2, pos)
				line += '  '
			line += '  '
			return line
		elif self.n == 0:
			line = ''
			line += self.displayCell(self.field)
			return line
		else:
			line = ''
			for i in range(self.sizes[currN]):
				pos[currN] = i
				cell = self.getCell(pos)
				line += self.displayCell(cell)
			return line
	
	# vertical is odd
	def displayRecVert(self, currN, pos):
		if currN % 2 != 1:
			return
		if currN > 1:
			for i in range(self.sizes[currN]):
				pos[currN] = i
				self.displayRecVert(currN-2, pos)
				print('')
			print('')
		elif currN == 1:
			for i in range(self.sizes[currN]):
				pos[currN] = i
				# highest even dimension
				evenN = ((self.n-1)//2)*2
				line = self.displayRecHoriz(evenN, pos)
				print(line)
		else: # no vertical dimensions
			# highest even dimension
			evenN = ((self.n-1)//2)*2
			line = self.displayRecHoriz(evenN, pos)
			print(line)

	def display(self):
		pos = [0]*self.n
		# highest odd dimension
		oddN = (self.n//2)*2-1
		self.displayRecVert(oddN, pos)
	
	def displayDataCell(self, cell):
		return '%5i' % cell
	
	# horizontal is even
	def displayDataRecHoriz(self, currN, pos):
		if currN % 2 != 0:
			return ''
		if currN > 0:
			line = ''
			for i in range(self.sizes[currN]):
				pos[currN] = i
				line += self.displayDataRecHoriz(currN-2, pos)
				line += '  '
			line += '  '
			return line
		elif self.n == 0:
			line = ''
			line += self.displayDataCell(self.field)
			return line
		else:
			line = ''
			for i in range(self.sizes[currN]):
				pos[currN] = i
				cell = self.getCell(pos)
				line += self.displayDataCell(cell)
			return line
	
	# vertical is odd
	def displayDataRecVert(self, currN, pos):
		if currN % 2 != 1:
			return
		if currN > 1:
			for i in range(self.sizes[currN]):
				pos[currN] = i
				self.displayDataRecVert(currN-2, pos)
				print('')
			print('')
		elif currN == 1:
			for i in range(self.sizes[currN]):
				pos[currN] = i
				# highest even dimension
				evenN = ((self.n-1)//2)*2
				line = self.displayDataRecHoriz(evenN, pos)
				print(line)
		else: # no vertical dimensions
			# highest even dimension
			evenN = ((self.n-1)//2)*2
			line = self.displayDataRecHoriz(evenN, pos)
			print(line)

	def displayData(self):
		pos = [0]*self.n
		# highest odd dimension
		oddN = (self.n//2)*2-1
		self.displayDataRecVert(oddN, pos)
	
	def click(self):
		pos = []
		for i in range(self.n):
			print('position %i/%i (0-%i)' % (i+1, self.n, self.sizes[self.n-1]-1))
			pos.append(int(input()))
		return pos
	
	def posToNumber(self,pos):
		number = 0
		for i in range(self.n):
			number += pos[i]*self.bases[i]
		return number

	def numberToPos(self, number):
		return [(number%self.bases[i+1])//self.bases[i] for i in range(self.n)]
	
	def getAdjacentRec(self, currN, pos, queue):
		if currN < self.n:
			# -1
			if 0 < pos[currN]:
				pos[currN] -= 1
				self.getAdjacentRec(currN+1, pos, queue)
				pos[currN] += 1
			# 0
			self.getAdjacentRec(currN+1, pos, queue)
			# +1
			if pos[currN] < self.sizes[currN]-1:
				pos[currN] += 1
				self.getAdjacentRec(currN+1, pos, queue)
				pos[currN] -= 1
		else:
			queue.append([])
			for i in pos:
				queue[-1].append(i)
	
	def getAdjacent(self, pos):
		queue = []
		self.getAdjacentRec(0, pos, queue)
		return queue
	
	def placeMines(self, pos):
		everyPos = [i for i in range(0,self.total)]
		random.shuffle(everyPos)
		ind = 0
		mineCount = 0
		while True:
			currentPos = self.numberToPos(everyPos[ind])
			# check that current position is not near click position
			adj = True
			for i in range(self.n):
				if abs(currentPos[i] - pos[i]) > 1:
					adj = False
			if not adj:
				# if not adjacent, then make mine
				currentCell = self.getCell(currentPos)
				self.setCell(currentPos, currentCell + self.MINE)
				# add to adjacent numbers
				queue = self.getAdjacent(currentPos)
				for i in queue:
					cell = self.getCell(i)
					self.setCell(i, cell + 1)
				# check count
				mineCount += 1
				if mineCount == self.numberOfMines:
					return
			ind += 1
				
	
	# no diagonals or self
	def getCoveredAdjacent(self, pos, queue):
		for i in range(self.n):
			# -1
			if 0 < pos[i]:
				queue.append([])
				for j in range(self.n):
					if j == i:
						queue[-1].append(pos[j] - 1)
					else:
						queue[-1].append(pos[j])
			# +1
			if pos[i] < self.sizes[i]-1:
				queue.append([])
				for j in range(self.n):
					if j == i:
						queue[-1].append(pos[j] + 1)
					else:
						queue[-1].append(pos[j])
	
	def uncover(self, pos):
		cell = self.getCell(pos)
		if self.isCovered(cell):
			# cell covered, figure out what to do
			if self.isMine(cell):
				# uncover and lose
				self.setCell(pos, cell - self.COVERED)
			elif self.isEmpty(cell):
				# uncover and all adjacent too
				queue = [pos]
				while len(queue) > 0:
					pos = queue.pop(0)
					cell = self.getCell(pos)
					if self.isCovered(cell):
						if self.isNumbered(cell):
							# uncover number
							self.setCell(pos, cell - self.COVERED)
						elif self.isEmpty(cell):
							# uncover empty, get adjacent
							self.setCell(pos, cell - self.COVERED)
							self.getCoveredAdjacent(pos, queue)
			else:
				# well, probably a number, let's just uncover it
				self.setCell(pos, cell - self.COVERED)
	
	def uncoverAll(self):
		for i in range(self.total):
			pos = self.numberToPos(i)
			cell = self.getCell(pos)
			if self.isCovered(cell):
					self.setCell(pos, cell - self.COVERED)
	
	def uncoverMines(self):
		for i in range(self.total):
			pos = self.numberToPos(i)
			cell = self.getCell(pos)
			if self.isMine(cell) and self.isCovered(cell):
					self.setCell(pos, cell - self.COVERED)
	
	def checkVictory(self):
		for i in range(self.total):
			pos = self.numberToPos(i)
			cell = self.getCell(pos)
			if not self.isMine(cell):
				if self.isCovered(cell):
					return False
			elif not self.isCovered(cell):
				return False
		return True
		
	def checkFailure(self):
		for i in range(self.total):
			pos = self.numberToPos(i)
			cell = self.getCell(pos)
			if self.isMine(cell) and not self.isCovered(cell):
					return True
		return False
		
	def displayWin(self):
		self.uncoverMines()
		self.display()
		print('YOU LIVE!')
	
	def displayLose(self):
		self.uncoverMines()
		self.display()
		print('YOU DIED!')
	
	def loop(self):
		while True:
			print('')
			self.display()
			pos = self.click()
			self.uncover(pos)
			if self.checkFailure():
				self.displayLose()
				return
			if self.checkVictory():
				self.displayWin()
				return
	
	def main(self):
		self.getDimensions()
		if not self.validDimensions():
			print('INVALID NUMBER OF DIMENSIONS')
			return
		self.getSizes()
		if not self.validSizes():
			print('INVALID SIZES')
			return
		self.getMines()
		if not self.validMines():
			print('INVALID NUMBER OF MINES')
			return
		
		self.buildEmptyField()
		print('')
		self.display()
		pos = self.click()
		self.placeMines(pos)
		self.uncover(pos)
		if self.checkVictory():
			self.displayWin()
			return
		
		self.loop()
		return
	
	def test(self):
		self.setDimensions(2)
		self.setSizes([5]*self.n)
		self.setMines(1*self.n)
		self.buildEmptyField()
		pos = [2]*self.n
		print(' ')

		print(self.n)
		print(self.sizes)
		print(self.field)
		print(' ')

		self.placeMines(pos)
		self.uncover(pos)
		
		self.loop()

a = Minefield()
a.main()
