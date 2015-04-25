# FILE:    mine
# PURPOSE: Any-dimensional minesweeper
# AUTHOR:  Geoffrey Card
# DATE:    2015-03-23 - 2015-04-25
# VERSION: 1.0.1
# TODO:    split matrices before solving
#          displayLoss seems to have some issues
#          combine checkVictory and checkFailure
#          clean up and comment
# NOTES:   graphics are poor
#
# Game becomes dramatically more difficult per dimension, for both humans and machines.
# Assuming a field with n dimensions.
# Assuming each dimension has length m greater than or equal to 5:
# Assuming player's first click is a non-edge:
#
# Total number of cells = m^n
# Total number of adjacent cells to any non-edge: 3^n-1
# 
# To solve the simplest possible opening (after first click), an automatic solver must solve a matrix of 3^n-1 equations and 5^n-3^n unknowns.
#
# As a matrix, it would be a sparse matrix with 3^n-1 rows and 5^n-3^n columns.
# For each row, there would be fewer than 3^n-1 elements.
# That means fewer than (3^n-1)^2 elements out of (3^n-1)*(5^n-3^n) elements total.
# Since each unknown can only be a mine or not, for the number of unknowns k, there are 2^k potential solutions.
# 
#  n | m^n (m=5) | 3^n-1 | 5^n-3^n | (3^n-1)^2 | (3^n-1)x(5^n-3^n) | 2^(5^n-3^n) |
# ---+-----------+-------+---------+-----------+-------------------+-------------+
#  1 |         5 |     2 |       2 |         4 |                 4 |           4 |
#  2 |        25 |     8 |      16 |        64 |               128 |       65536 |
#  3 |       125 |    26 |      98 |       676 |              2548 |     3x10^29 |
#  4 |       625 |    80 |     544 |      6400 |             43520 |    6x10^163 |
#  5 |      3125 |   242 |    2882 |     58564 |            697444 |    4x10^867 |
#  6 |     15625 |   728 |   14896 |    529984 |          10844288 |   1x10^4484 |
#  7 |     78125 |  2186 |   75938 |   4778596 |         166000468 |  4x10^22859 |
#
# Solving as a matrix:
# Using brute force, the number of solutions would be proportional to at least the number of solutions, > O(2^(5^n)).
# Using optimized algorithms should take time proportional to the number of non-zero elements, > O(9^n).
# Using unoptimized algorithms sould take time proportional to the total number of elements, > O(15^n).
# I don't know the complexity of my algorithm, I use a trick with the binary nature of the solutions and sparsity of the matrix, even that is slow.
#
# There are tricks and certain simpified and trivial cases (e.g. all mines), but that's the simplest opening possible for a non-edge.

import random, math, time, sys

class Minefield:
    '''
    # n = number of dimensions
    # sizes = sizes in each dimension
    # bases = poducts of sizes
    # thingy = poducts of sizes up to length of sizes (I ran out of short, useful names)
    # MAX_ADJ = 3**n
    # TAG = MAX_ADJ+1
    # MINE    = 1*TAG, marker for cell contains mine
    # COVERED = 2*TAG, marker for cell is covered
    # FLAGGED = 4*TAG, marker for cell is covered
    # field = the actual minefield, 1D array
    # numberOfMines = number of mines
    # total = total number of cells in field
    # DIGITS = number of decimal digits necessary to represent numbers
    '''
    
    def dot(self, a, b):
        value = 0
        if len(a) == len(b):
            for i in range(len(a)):
                value += a[i]*b[i]
        return value

    # for 2.7/3 compatibility
    def getChar(self, words):
        # 2.7/3 compatibility
        if sys.version_info[0] < 3:
            return raw_input(words)
        else:
            return input(words)

    # for 2.7/3 compatibility
    def getNum(self, words):
        # 2.7/3 compatibility
        if sys.version_info[0] < 3:
            return input(words)
        else:
            return eval(input(words))

    def __init__(self):
        self.n = 0
        self.sizes = []
        self.bases = []
        self.thingy = []
        self.total = 0
        self.numberOfMines = 0
        self.firstMove = False
        self.playing   = False
        self.MAX_ADJ = 3**self.n
        self.TAG     = self.MAX_ADJ+1
        self.MINE    = 1*self.TAG
        self.COVERED = 2*self.TAG
        self.FLAGGED = 4*self.TAG
        self.DIGITS = int(math.log10(self.MAX_ADJ)+1)
        self.DIGITS_DEBUG = int(math.log10(self.FLAGGED)+1)
        self.field = []
    
    ################################
    #     INDICES AND POSITION     #
    ################################
    
    def posToInd(self, pos):
        ind = 0;
        for i in range(self.n):
            ind += pos[i]*self.thingy[i]
        return ind
    
    def indToPos(self, ind):
        return [(ind%self.bases[i+1])//self.bases[i] for i in range(self.n)]
    
    ################################
    #        GET AND SET CELL      #
    ################################
    
    def getCell(self, ind):
        if not (0 <= ind < self.total):
            print('ERROR: Index {} = {} out of bounds {} = {}.'.format(ind, self.indToPos(ind), self.total, self.sizes))
        return self.field[ind]
    
    def setCell(self, ind, value):
        self.field[ind] = value
    
    ################################
    #         CHECK CELL           #
    ################################
    
    def isFlagged(self, cell):
        return cell >= self.FLAGGED
    
    def isCovered(self, cell):
        return (cell % self.FLAGGED) >= self.COVERED
    
    def isMine(self, cell):
        return (cell % self.COVERED) >= self.MINE
    
    def isNumbered(self, cell):
        return 0 < (cell % self.COVERED) < self.MINE
    
    def isEmpty(self, cell):
        return 0 == (cell % self.COVERED)
    
    def getNumber(self, cell):
        return cell % self.MINE
    
    ################################
    #       PLACE AND UNCOVER      #
    ################################
    
    # excluding ind
    def getAdjacent(self, ind):
        pos = self.indToPos(ind)
        queue = [ind]
        for n in range(self.n):
            if 0 < pos[n] < self.sizes[n]-1:
                # -1, 0, +1
                for i in range(len(queue)):
                    queue.append(queue[i]+self.thingy[n])
                    queue.append(queue[i]-self.thingy[n])
            elif 0 < pos[n]:
                # -1, 0
                for i in range(len(queue)):
                    queue.append(queue[i]-self.thingy[n])
            elif pos[n] < self.sizes[n]-1:
                # 0, +1
                for i in range(len(queue)):
                    queue.append(queue[i]+self.thingy[n])
            else:
                # 0
                pass
        queue.pop(queue.index(ind))
        return queue
    
    def placeMines(self, ind):
        pos = self.indToPos(ind)
        everyInd = [i for i in range(0,self.total)]
        random.shuffle(everyInd)
        mineCount = 0
        for ind in everyInd:
            # check that current position is not near click position
            adj = True
            currPos = self.indToPos(ind)
            for i in range(self.n):
                if abs(currPos[i] - pos[i]) > 1:
                    adj = False
            if not adj:
                # if not adjacent, then make mine
                currCell = self.getCell(ind)
                self.setCell(ind, currCell + self.MINE)
                # add to adjacent numbers
                queue = self.getAdjacent(ind)
                for i in queue:
                    cell = self.getCell(i)
                    self.setCell(i, cell + 1)
                # check count
                mineCount += 1
            if mineCount == self.numberOfMines:
                return
    
    def getCoveredAdjacent(self, ind, queue):
        newQueue = self.getAdjacent(ind)
        for i in newQueue:
            if self.isCovered(self.getCell(i)):
                queue.append(i)
    
    def uncover(self, ind):
        cell = self.getCell(ind)
        if self.isCovered(cell):
            # cell covered, figure out what to do
            if self.isMine(cell):
                # uncover and lose
                self.setCell(ind, cell - self.COVERED)
            elif self.isEmpty(cell):
                # uncover and all adjacent too
                queue = [ind]
                while len(queue) > 0:
                    ind = queue.pop(0)
                    cell = self.getCell(ind)
                    if self.isCovered(cell):
                        if self.isNumbered(cell):
                            # uncover number
                            self.setCell(ind, cell - self.COVERED)
                        elif self.isEmpty(cell):
                            # uncover empty, get adjacent
                            self.setCell(ind, cell - self.COVERED)
                            self.getCoveredAdjacent(ind, queue)
            else:
                # probably a number, let's just uncover it
                self.setCell(ind, cell - self.COVERED)
    
    def uncoverAll(self):
        for ind in range(self.total):
            cell = self.getCell(ind)
            if self.isCovered(cell):
                    self.setCell(ind, cell - self.COVERED)
    
    def uncoverMines(self):
        for ind in range(self.total):
            cell = self.getCell(ind)
            if self.isMine(cell) and self.isCovered(cell) and not self.isFlagged(cell):
                    self.setCell(ind, cell - self.COVERED)
    
    ################################
    #         CHECK FIELD          #
    ################################
    
    def checkVictory(self):
        for ind in range(self.total):
            cell = self.getCell(ind)
            if not self.isMine(cell):
                if self.isCovered(cell):
                    # still have work to do
                    return False
            elif not self.isCovered(cell):
                # you is died
                return False
        return True
        
    def checkFailure(self):
        for ind in range(self.total):
            cell = self.getCell(ind)
            if self.isMine(cell) and not self.isCovered(cell):
                    return True
        return False
        
    ################################
    #             FLAG             #
    ################################
    
    def flag(self, ind):
        cell = self.getCell(ind)
        if self.isCovered(cell) and not self.isFlagged(cell):
            self.setCell(ind, cell + self.FLAGGED)
    
    def unflag(self, ind):
        cell = self.getCell(ind)
        if self.isCovered(cell) and self.isFlagged(cell):
            self.setCell(ind, cell - self.FLAGGED)
    
    ################################
    #            DISPLAY           #
    ################################
    
    def clearScreen(self):
        print('\n'*100)
    
    def displayIndCell(self, cell):
        return (' %%%ii' % int(math.log10(self.total)+1) ) % cell
    
    def displayDataCell(self, cell):
        return (' %%%ii' % self.DIGITS_DEBUG) % cell
    
    def displayCell(self, cell):
        if self.isFlagged(cell):
            return '[' + ('+'*self.DIGITS) + ']'
        elif self.isCovered(cell):
            return '[' + (' '*self.DIGITS) + ']'
        elif self.isEmpty(cell):
            return '[' + (' '*(self.DIGITS-1)) + '0' + ']'
        elif self.isNumbered(cell):
            return '[' + (('%%%ii' % self.DIGITS) % self.getNumber(cell)) + ']'
        elif self.isMine(cell):
            return '[' + ('*'*self.DIGITS) + ']'
        else:
            return '[' + ('?'*self.DIGITS) + ']'
    
    def displayLossCell(self, cell):
        if self.isMine(cell):
            if self.isFlagged(cell):
                return '[' + ('+'*self.DIGITS) + ']'
            elif self.isCovered(cell):
                return '[' + ('#'*self.DIGITS) + ']'
            else:
                return '[' + ('*'*self.DIGITS) + ']'
        else:
            if self.isCovered(cell):
                return '[' + (' '*self.DIGITS) + ']'
            elif self.isNumbered(cell):
                return '[' + (('%%%ii' % self.DIGITS) % self.getNumber(cell)) + ']'
            elif self.isEmpty(cell):
                return '[' + (' '*(self.DIGITS-1)) + '0' + ']'
        return '[' + ('?'*self.DIGITS) + ']'
    
    def iterateDisplay(self, displayFunction):
        self.clearScreen()
        # rearrange sizes, evens then odds
        supinds = []
        for i in range(0,self.n,2):
            supinds.append(i)
        for i in range(1,self.n,2):
            supinds.append(i)
        # iterate through every pos
        line = ''
        pos = [0]*self.n
        for i in range(self.total):
            # draw cell
            line += displayFunction(self.getCell(self.posToInd(pos)))
            # increment
            for i in supinds:
                if pos[i] >= self.sizes[i]-1:
                    pos[i] = 0
                    if i & 1:
                        while line[-1] == ' ':
                            line = line[:-1]
                        line += '\n'
                    else:
                        line += '  '
                else:
                    pos[i] += 1
                    if i & 1:
                        while line[-1] == ' ':
                            line = line[:-1]
                        print(line)
                        line = ''
                    break
        while line[-1] == '\n':
            line = line[:-1]
        print(line)
    
    def display(self):
        self.iterateDisplay(self.displayCell)
    
    def displayData(self):
        self.iterateDisplay(self.displayDataCell)
    
    def displayWin(self):
        self.display()
        print('YOU LIVE!')
    
    def displayLoss(self):
        self.iterateDisplay(self.displayLossCell)
        print('YOU DIED!')
    
    ################################
    #            SOLVER            #
    ################################
    
    def solverFirst(self):
        #print('solverFirst') # DEBUG
        # if everything is mines
        if self.total <= self.numberOfMines:
            return ['F', 0]
        # otherwise, center has most potential
        pos = []
        for i in self.sizes:
            pos.append(i//2)
        return ['U', self.posToInd(pos)]
    
    # if a number has adjacent covered cells:
    #   if that number is equal to the number of adjacent cells:
    #     flag adjacent covered cells
    #   if number is equal to adjacent flags and there are adj unflaged cells
    #     uncover adj unflaged cells
    # if number of covered cells equals remaining mines
    #   flag
    def solverSimple(self):
        #print('solverSimple') # DEBUG
        totalCovered = 0
        lastCovered = -1
        for ind in range(self.total):
            cell = self.getCell(ind)
            if self.isCovered(cell):
                totalCovered += 1
                lastCovered = ind
            elif self.isNumbered(cell):
                number = self.getNumber(cell)
                adjInd = self.getAdjacent(ind)
                adjFlagged = 0
                adjCoveredNF = 0
                for j in adjInd:
                    cell = self.getCell(j)
                    if self.isFlagged(cell):
                        adjFlagged += 1
                    elif self.isCovered(cell): # and not isFlagged()
                        adjCoveredNF += 1
                # 
                if adjCoveredNF == 0:
                    pass
                elif number == adjFlagged + adjCoveredNF:
                    # all should be flagged, flag rest
                    for j in adjInd:
                        cell = self.getCell(j)
                        if self.isCovered(cell) and not self.isFlagged(cell):
                            return ['F', j]
                elif number == adjFlagged:
                    # all are flagged, uncover rest
                    for j in adjInd:
                        cell = self.getCell(j)
                        if self.isCovered(cell) and not self.isFlagged(cell):
                            return ['U', j]
        if totalCovered == self.numberOfMines and 0 < lastCovered < self.total:
            return ['F', lastCovered]
        return ['N', -1]
    
    ################################################################
    ################################################################
    
    def solverBetter(self):
        #print('solverBetter') # DEBUG
        [A, b, places, mineCount, coveredCount] = self.getMatrix()
        #self.printMatrix(A, b, places) # DEBUG
        prob = self.solveMatrixLogic(A, b, places, mineCount)
        if prob == None:
            cmd = 'Q'
            ind = -1
        else:
            # decide on move
            cmd = 'N'
            ind = 0
            err = 1.1 # > 1.0
            for i in range(len(places)):
                #print('{} {}'.format(self.indToPos(places[i]), prob[i])) # DEBUG
                if 1.0 - prob[i] < err:
                    cmd = 'F'
                    ind = places[i]
                    err = 1.0 - prob[i]
                if prob[i] < err:
                    cmd = 'U'
                    ind = places[i]
                    err = prob[i]
                if err == 0.0:
                    #pass # DEBUG
                    break
            # is this better than clicking any non-adjacent point?
            if err > 0 and coveredCount - len(places) > 0:
                #print('else: {} / {} = {}'.format((mineCount - sum(prob)), (coveredCount - len(places)), (mineCount - sum(prob)) / (coveredCount - len(places)))) # DEBUG
                if (mineCount - sum(prob)) / (coveredCount - len(places)) < err:
                    # better to try random non-adj
                    cmd = 'N'
                    ind = -1
        #return ['Q', -1] # DEBUG
        return [cmd, ind]
    
    # separates any separate matrix from inputs
    # IMPORTANT: EDITS INPUTS
    def splitMatrix(self, A, b, places):
        return [[], [], []]
    
    # to improve, use rref first
    def solveMatrixLogic(self, A, b, places, mineCount):
        # initialize partial solutions with zeros
        partials = [[0]*len(places)] 
        # indices of used/known positions in x
        unused = [i for i in range(len(places))]
        used = []
        # for each line in A
        #   find non-zero, unused values
        #     move to in-use
        #   iterate through all permutations of in-use with each partial solution
        #     permutations that solve current line form the new set of partial solutions
        #   move in-use values to used
        for i in range(len(A)):
            #print('') # DEBUG
            #print('{} = [{}]'.format(A[i], b[i])) # DEBUG
            if A[i].count(0) < len(A[i]):
                # find non-zero, unused values
                inUse = []
                for j in range(len(A[i])):
                    if A[i][j] != 0 and unused.count(j) > 0:
                        inUse.append(j)
                        unused.remove(j)
                #print('used = {}, in-use = {}, unused = {}'.format(used, inUse, unused)) # DEBUG
                #for x in partials: # DEBUG
                #    print(x) # DEBUG
                #print('iterate') # DEBUG
                # iterate through all permutations of in-use with each partial solution
                newPartials = []
                for x in partials:
                    count = 0
                    while count < 2**len(inUse):
                        # permutations that solve current line form the new set of partial solutions
                        #line = '{} = [{}]'.format(x, self.dot(A[i],x)) # DEBUG
                        if self.dot(A[i], x) == b[i] and sum(x) <= mineCount:
                            #line += ' *' # DEBUG
                            newPartials.append([])
                            for j in x:
                                newPartials[-1].append(j)
                        #print(line) # DEBUG
                        # iterating in-use
                        for j in inUse:
                            if x[j] == 0:
                                x[j] = 1
                                break
                            else:
                                x[j] = 0
                        count += 1
                partials = []
                for x in newPartials:
                    partials.append([])
                    for j in x:
                        partials[-1].append(j)
                # move in-use values to used
                for j in inUse:
                    used.append(j)
        # get probabilities
        if len(partials) > 0:
            prob = [0.0]*len(places)
            for i in range(len(prob)):
                for j in range(len(partials)):
                    prob[i] += partials[j][i]
                prob[i] /= len(partials)
        else:
            prob = None
            print('ERROR: CANNOT SOLVE')
        return prob
    
    def solveMatrixBrute(self, A, b, places, mineCount):
        x = [0]*len(places)
        count = 0
        probs = []
        while count < 2**len(x):
            #print(x) # DEBUG
            isSol = True
            for i in range(len(A)):
                if self.dot(A[i],x) != b[i]:
                    isSol = False
                    break
            if isSol and sum(x) <= mineCount:
                probs.append([])
                for i in x:
                    probs[-1].append(i)
            # increment
            for i in range(len(x)):
                if x[i] == 0:
                    x[i] = 1
                    break
                else:
                    x[i] = 0
            count += 1
        # get probabilities
        prob = [0.0]*len(places)
        for i in range(len(prob)):
            for j in range(len(probs)):
                prob[i] += probs[j][i]
            prob[i] /= len(probs)
        return prob
    
    def getMatrix(self):
        A = []
        b = []
        places = []
        mineCount = self.numberOfMines
        coveredCount = 0
        for ind in range(self.total):
            cell = self.getCell(ind)
            if self.isFlagged(cell):
                mineCount -= 1
            elif self.isCovered(cell):
                coveredCount += 1
            elif self.isNumbered(cell):
                number = self.getNumber(cell)
                adjInds = self.getAdjacent(ind)
                adjPlaces = []
                for adjInd in adjInds:
                    adjCell = self.getCell(adjInd)
                    if self.isFlagged(adjCell):
                        number -= 1
                    elif self.isCovered(adjCell):
                        adjPlaces.append(adjInd)
                if len(adjPlaces) > 0:
                    A.append([0]*len(places))
                    b.append(number)
                    for p in adjPlaces:
                        if places.count(p) == 0:
                            places.append(p)
                            for j in range(len(A)):
                                A[j].append(0)
                        A[-1][places.index(p)] = 1
        return [A, b, places, mineCount, coveredCount]
    
    def printMatrix(self, A, b, places):
        print(r'places = {}'.format(places))
        for i in range(len(A)):
            line = ''
            for j in range(len(A[i])):
                if A[i][j] == 1:
                    line += '1'
                else:
                    line += ' '
            line += '={}'.format(b[i])
            print(line)
    
    ################################################################
    ################################################################
    
    def solverRandom(self):
        #print('solverRandom') # DEBUG
        everyInd = [ind for ind in range(self.total)]
        random.shuffle(everyInd)
        for ind in everyInd:
            cell = self.getCell(ind)
            if self.isCovered(cell) and not self.isFlagged(cell):
                return ['U', ind]
        return ['N', -1]
    
    def solverRandomNonAdj(self):
        #print('solverRandomNonAdj') # DEBUG
        everyInd = [ind for ind in range(self.total)]
        random.shuffle(everyInd)
        for ind in everyInd:
            cell = self.getCell(ind)
            if self.isCovered(cell) and not self.isFlagged(cell):
                noAdj = True
                for j in self.getAdjacent(ind):
                    adjCell = self.getCell(j)
                    if not self.isCovered(adjCell):
                        noAdj = False
                        break
                if noAdj:
                    return ['U', ind]
        return ['N', -1]
    
    # cheats, unflags and uncovers non-mines
    # randomized traversal because it can
    def solverCheat(self):
        #print('solverCheat') # DEBUG
        everyInd = [ind for ind in range(self.total)]
        random.shuffle(everyInd)
        for ind in everyInd:
            cell = self.getCell(ind)
            if self.isMine(cell):
                if not self.isFlagged(cell):
                    return ['F', ind]
            else:
                if self.isFlagged(cell):
                    return ['F', ind]
                if self.isCovered(cell):
                    return ['U', ind]
        return ['N', -1]
    
    ################################
    #           CONTROL            #
    ################################
    
    def validPos(self, pos):
        for i in range(self.n):
            if not (0 <= pos[i] < self.sizes[i]):
                return False
        return True
    
    def getCommand(self):
        print('Q -> quit')
        #print('N -> nop, do nothing')
        print('R -> reset, same settings')
        print('F -> flag/unflag')
        print('U -> uncover')
        #print('S -> solver')
        #print('C -> cheat')
        # cmd
        cmd = self.getChar('Command:').upper()
        # sizes
        ind = -1
        if cmd == 'F' or cmd == 'U':
            pos = []
            for i in range(self.n):
                pos.append(self.getNum(r'position {} of {} (1-{}):'.format(i+1, self.n, self.sizes[i]))-1)
            if self.validPos(pos):
                ind = self.posToInd(pos)
            else:
                cmd = 'N'
        elif cmd == 'N' or cmd == 'R' or cmd == 'S' or cmd == 'C' or cmd == 'Q':
            pass
        else:
            cmd = 'N'
        return [cmd, ind]
    
    def getSettings(self):
        # dimensions
        n = self.getNum(r'dimensions (1-inf):')
        # sizes
        sizes = []
        total = 1
        adj = 1
        for i in range(n):
            sizes.append(self.getNum(r'sizes {} of {} (1-inf):'.format(i+1, n)))
            total *= sizes[i]
            if sizes[i] > 3:
                adj *= 3
            else:
                adj *= sizes[i]
        # number of mines
        numberOfMines = self.getNum('number of mines (1-{}):'.format(total-adj))
        return self.setSettings(n, sizes, numberOfMines)
    
    def setSettings(self, n, sizes, numberOfMines):
        # check dimensions
        if not (n > 0):
            print('ERROR: Too few dimensions.')
            return False
        # check sizes
        if not (len(sizes) == n):
            print('ERROR: Sizes do not match dimensions.')
            return False
        size = 0
        greaterThanThree = False
        adj = 1
        total = 1
        bases = [total]
        for i in range(n):
            total *= sizes[i]
            bases.append(total)
            if sizes[i] == 0:
                print('ERROR: Size must be greater than zero.')
                return False
            elif sizes[i] > 3:
                greaterThanThree = True
                adj *= 3
            else:
                adj *= sizes[i]
        thingy = bases[0:n]
        if not greaterThanThree:
            print('ERROR: Size must be greater than three in at least one dimension.')
            #return False
        # check number of mines
        if not (0 <= numberOfMines <= total - adj):
            print('ERROR: Invalid number of mines.')
            #return False
        # set values
        self.n = n
        self.sizes = []
        for i in sizes:
            self.sizes.append(i)
        self.numberOfMines = numberOfMines
        self.total = total
        self.bases = []
        for i in bases:
            self.bases.append(i)
        self.thingy = []
        for i in thingy:
            self.thingy.append(i)
        self.firstMove = True
        self.playing   = True
        self.MAX_ADJ = adj
        self.TAG     = self.MAX_ADJ+1
        self.MINE    = 1*self.TAG
        self.COVERED = 2*self.TAG
        self.FLAGGED = 4*self.TAG
        self.DIGITS = int(math.log10(self.MAX_ADJ)+1)
        self.DIGITS_DEBUG = int(math.log10(self.FLAGGED)+1)
        self.field = [] # direct method doesn't seem to work
        for i in range(total):
            self.field.append(self.COVERED)
        return True
    
    def printAll(self):
        print('n = {}'.format(self.n))
        print('sizes = {}'.format(self.sizes))
        print('numberOfMines = {}'.format(self.numberOfMines))
        print('total = {}'.format(self.total))
        print('bases = {}'.format(self.bases))
        print('thingy = {}'.format(self.thingy))
        print('firstMove = {}'.format(self.firstMove))
        print('playing = {}'.format(self.playing))
        print('MAX_ADJ = {}'.format(self.MAX_ADJ))
        print('TAG = {}'.format(self.TAG))
        print('MINE = {}'.format(self.MINE))
        print('COVERED = {}'.format(self.COVERED))
        print('FLAGGED = {}'.format(self.FLAGGED))
        print('DIGITS = {}'.format(self.DIGITS))
        print('DIGITS_DEBUG = {}'.format(self.DIGITS_DEBUG))
        print('field = {}'.format(self.field))
    
    # 'Q' -> quit
    # 'N' -> nop (no operation), do nothing
    # 'R' -> reset, new field, same properties
    # 'F' -> toggle flag
    # 'U' -> uncover
    # 'S' -> solver (1 step)
    # 'C' -> cheat (1 step), solver that cheats
    # returns True on win, False on lose, else None
    def click(self, cmd, ind=-1):
        #print(r'[{}, {}]'.format(cmd, self.indToPos(ind))) # DEBUG
        if cmd == 'N':
            return None
        elif cmd == 'Q':
            self.placeMines(ind) # kind pointless, but adds to UX
            return False
        elif cmd == 'R':
            self.setSettings(self.n, self.sizes, self.numberOfMines)
            return None
        elif cmd == 'F':
            if 0 <= ind < self.total:
                cell = self.getCell(ind)
                if self.isFlagged(cell):
                    self.unflag(ind)
                elif self.isCovered(cell):
                    self.flag(ind)
            return self.checkLoop()
        elif cmd == 'U':
            if 0 <= ind < self.total:
                cell = self.getCell(ind)
                if self.isCovered(cell) and not self.isFlagged(cell):
                    if self.firstMove:
                        self.firstMove = False
                        self.placeMines(ind)
                    self.uncover(ind)
            return self.checkLoop()    
        elif cmd == 'S':
            if self.firstMove:
                [cmd, ind] = self.solverFirst()
            else:
                [cmd, ind] = self.solverSimple()
                if cmd == 'N':
                    [cmd, ind] = self.solverBetter()
                    if cmd == 'N':
                        [cmd, ind] = self.solverRandomNonAdj()
                        if cmd == 'N':
                            [cmd, ind] = self.solverRandom()
            return self.click(cmd, ind) # meta, but it should work
        elif cmd == 'C':
            if self.firstMove:
                [cmd, ind] = self.solverFirst()
            else:
                [cmd, ind] = self.solverCheat()
            return self.click(cmd, ind)
        else:
            return self.checkLoop()
    
    def checkLoop(self):
        if self.checkVictory():
            return True
        elif self.checkFailure():
            return False
        else:
            return None
    
    ################################
    #          AUTO-PLAY           #
    ################################
    
    def autoplay(self, n, sizes, numberOfMines):
        # initialize
        self.clearScreen()
        if not self.setSettings(n, sizes, numberOfMines):
            return None
        self.printAll()
        # steps
        victory = None
        while victory == None:
            self.clearScreen()
            self.display()
            time.sleep(0.5)
            victory = self.click('S', -1)
        # check victory condition
        if victory == True:
            self.displayWin()
        elif victory == False:
            self.displayLoss()
        else:
            self.display()
        return victory

    ################################
    #            PLAY              #
    ################################
    
    def play(self):
        # initialize
        self.clearScreen()
        while not self.getSettings():
            pass
        # steps
        victory = None
        while victory == None:
            self.display()
            [cmd, ind] = self.getCommand()
            victory = self.click(cmd, ind)
            print(victory)
        # check victory condition
        if victory == True:
            self.displayWin()
        elif victory == False:
            self.displayLoss()
        else:
            self.display()
        return victory

if __name__ == '__main__':
    a = Minefield()
    #a.autoplay(2, [9,9], 10)
    a.play()
