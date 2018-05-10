
"""
In pacard.py, you will implement the search algorithm  based on refutation resolution 
which will lead Pacard through the cave of the evil GhostWumpus.
"""

import util
from logic import * 
import sys
import inspect
import heapq, random

class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.

      Note that this PriorityQueue does not allow you to change the priority
      of an item.  However, you may insert the same item multiple times with
      different priorities.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        # FIXME: restored old behaviour to check against old results better
        # FIXED: restored to stable behaviour
        entry = (priority, self.count, item)
        # entry = (priority, item)
        #treat this queue as a set (like it should be)
        for element in self.heap:
            if element[2] == item :
                return
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        #  (_, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def remove(self,element):
        #TODO test!
        for index in range(0,self.heap):
            if self.heap[index][2]==element:
                del self.heap[index]
                break

class PriorityQueueWithFunction(PriorityQueue):
    """
    Implements a priority queue with the same push/pop signature of the
    Queue and the Stack classes. This is designed for drop-in replacement for
    those two classes. The caller has to provide a priority function, which
    extracts each item's priority.
    """
    def  __init__(self, priorityFunction):
        "priorityFunction (item) -> priority"
        self.priorityFunction = priorityFunction      # store the priority function
        PriorityQueue.__init__(self)        # super-class initializer

    def push(self, item):
        "Adds an item to the queue with priority from the priority function"
        PriorityQueue.push(self, item, self.priorityFunction(item))


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def miniWumpusSearch(problem): 
    """
    A sample pass through the miniWumpus layout. Your solution will not contain 
    just three steps! Optimality is not the concern here.
    """
    from game import Directions
    e = Directions.EAST 
    n = Directions.NORTH
    return  [e, n, n]

def logicBasedSearch(problem):
    """

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())

    print "Does the Wumpus's stench reach my spot?", 
               \ problem.isWumpusClose(problem.getStartState())

    print "Can I sense the chemicals from the pills?", 
               \ problem.isPoisonCapsuleClose(problem.getStartState())

    print "Can I see the glow from the teleporter?", 
               \ problem.isTeleporterClose(problem.getStartState())
    
    (the slash '\\' is used to combine commands spanning through multiple lines - 
    you should remove it if you convert the commands to a single line)
    
    Feel free to create and use as many helper functions as you want.

    A couple of hints: 
        * Use the getSuccessors method, not only when you are looking for states 
        you can transition into. In case you want to resolve if a poisoned pill is 
        at a certain state, it might be easy to check if you can sense the chemicals 
        on all cells surrounding the state. 
        * Memorize information, often and thoroughly. Dictionaries are your friends and 
        states (tuples) can be used as keys.
        * Keep track of the states you visit in order. You do NOT need to remember the
        tranisitions - simply pass the visited states to the 'reconstructPath' method 
        in the search problem. Check logicAgents.py and search.py for implementation.
    """
    # array in order to keep the ordering
    visitedStates = []
    pacardState = problem.getStartState()
    visitedStates.append(pacardState)

    pacardMemoryVisited=dict()
    pacardAssumptions=dict()

    safeOpenDirections=PriorityQueueWithFunction(stateWeight)
    unknownOpenDirections=PriorityQueueWithFunction(stateWeight)


    while not problem.isGoalState(pacardState) :

        #Step 1: Look into your memory. If this state isn't remembered add it.
        memoriseThisPlace(problem,pacardState,pacardMemoryVisited)

        #Step 2: Make a set of clauses and try to derive some information for every successor state.
        conclusions={}
        deriveInformation3(problem,pacardState,pacardMemoryVisited,conclusions)
        addToAssumptions(problem,pacardState,pacardAssumptions,conclusions)
        #Step 3: Using the derived informations, filter the possibilities and choose the next move
        nextState=decideForNextState(problem,pacardState,conclusions,pacardMemoryVisited,pacardAssumptions,safeOpenDirections,unknownOpenDirections)

        if nextState==pacardState: break
        pacardState=nextState
        visitedStates.append(pacardState)

    resList=problem.reconstructPath(visitedStates)
    return resList



def decideForNextState(problem,pacardState,conclusions,pacardMemoryVisited,pacardAssumptions,safeOpenDirections,unknownOpenDirections):
    #Ways of doing this:
        #   1. Search for a T in councusions
        #   2. Search for a O in councusions
        #   3. If no informations are availeable go by weights formula
        #   4. Pacard can't move
    succStates=problem.getSuccessors(pacardState)

    nextState=checkIfTeleporter(succStates,conclusions,pacardMemoryVisited)
    if nextState!=None: return nextState

    nextState=checkIfGlow(succStates,conclusions,pacardMemoryVisited)
    if nextState!=None: return nextState

    nextState=checkIfSafePlaceAhead(succStates,conclusions,pacardMemoryVisited,safeOpenDirections)
    if nextState!=None: return nextState

    if not safeOpenDirections.isEmpty():
        return safeOpenDirections.pop()


    nextState=checkIfUnknownAhead(succStates,conclusions,pacardMemoryVisited,unknownOpenDirections)
    if nextState!=None: return nextState

    if not unknownOpenDirections.isEmpty():
            return unknownOpenDirections.pop()

    return pacardState

def checkIfTeleporter(succStates,conclusions,pacardMemoryVisited):

    for succ in succStates:
         #check if teleporter was concluded
         succConclusions=conclusions[succ[0]]
         if succConclusions==None: continue
         #pacardMemoryVisited[succ[0]]=(False,succConclusions) #don't add anything if you havent stepped on it
         if Labels.TELEPORTER == succConclusions:
             return succ[0]
         #check if teleporter is in memory TODO not for my implementation!
         if succ[0] in pacardMemoryVisited:
             pacMemSet=pacardMemoryVisited[succ[0]]
             for pacMem in pacMemSet:
                 if pacMem[1]==Labels.TELEPORTER and pacMem[0]==True:
                     return succ[0]
    return None

def checkIfGlow(succStates,conclusions,pacardMemoryVisited):

    for succ in succStates:
         #check if teleporter was concluded
         succConclusions=conclusions[succ[0]]
         if succConclusions==None: continue
         #pacardMemoryVisited[succ[0]]=(False,succConclusions) #don't add anything if you havent stepped on it
         if Labels.TELEPORTER_GLOW == succConclusions:
             return succ[0]
         #check if teleporter is in memory TODO not for my implementation!
         if succ[0] in pacardMemoryVisited:
             pacMemSet=pacardMemoryVisited[succ[0]]
             for pacMem in pacMemSet:
                 if pacMem[1]==Labels.TELEPORTER_GLOW and pacMem[0]==True:
                     return succ[0]
    return None


def checkIfSafePlaceAhead(succStates,conclusions,pacardMemoryVisited,openDirections):
    elementsProcessed=0
    #search for next open
    for succ in succStates:
         #check if teleporter was concluded
         succConclusions=conclusions[succ[0]]
         if succConclusions==None or succ[0] in pacardMemoryVisited: continue #skip positions if they are already visited or if no conclusion was made for them
         if Labels.SAFE == succConclusions:
             openDirections.push(succ[0])
             elementsProcessed+=1
             continue
    if elementsProcessed >0 :
        return openDirections.pop()
    else: return None

def checkIfUnknownAhead(succStates,conclusions,pacardMemoryVisited,unknownOpenDirections):
    elementsProcessed=0
    #search for next unknown
    nextState=0
    for succ in succStates:
         #check if teleporter was concluded
         succConclusions=conclusions[succ[0]]
         if succConclusions==None:
             if succ[0] not in pacardMemoryVisited:
                 unknownOpenDirections.push(succ[0])
                 elementsProcessed+=1
                 continue

    if elementsProcessed >0 :
        return unknownOpenDirections.pop()
    else: return None


def deriveInformation3(problem,pacardState,pacardMemoryVisited,conclusions):
    succStates=problem.getSuccessors(pacardState)
    memorySet=genMemoryClausesSet_Relevant(pacardState,pacardMemoryVisited,succStates)

    possilities=Labels.INDICATORS|Labels.UNIQUE

    for succState in succStates:
        # Make a simple clausula from the state with questions asking: is the position at state
        #for every next position, pacard asks himself what could it be on the other

        #conclude for unknown positions only
        #if succState[0] in pacardMemoryVisited: continue

        succStateDecision=None
        for outcome in possilities:
            clauses=generateClausesSet(pacardState,succStates) | memorySet
            goal = Clause([Literal(outcome+str(succState[0]), succState[0])])
            if resolution(clauses,goal):
                succStateDecision=outcome
                break
        conclusions[succState[0]]=succStateDecision


#-----------------Pacard memory adding methods------------------------
def addToAssumptions(problem,pacardState,pacardAssumptions,conclusions):
    possilities=Labels.INDICATORS|Labels.UNIQUE
    succStates=problem.getSuccessors(pacardState)

    for succ in succStates:
        succConclusions=conclusions[succ[0]]
        if succConclusions==None: continue
        posSet=set()
        for outcome in possilities:
            if outcome==succConclusions: posSet.add((True,succConclusions))
            else: posSet.add((False,outcome))

        pacardAssumptions[succ[0]]=posSet

def memoriseThisPlace(problem,pacardState,pacardMemoryVisited):
    if pacardState not in pacardMemoryVisited:
            label=None
            if problem.isWumpusClose(pacardState):
                label=Labels.WUMPUS_STENCH
            elif problem.isPoisonCapsuleClose(pacardState):
                label=Labels.POISON_CHEMICALS
            elif problem.isTeleporterClose(pacardState):
                label=Labels.TELEPORTER_GLOW
            else:
                #assume it's safe since you're standing on it
                label=Labels.SAFE
            #memory record consists of a boolean flag telling if pacard acctualy stepped in the field
            # and the label of the field
            addAllForLabel(label,pacardMemoryVisited,pacardState)

def blindStep(problem,pacardState,pacardMemoryVisited):
    if pacardState not in pacardMemoryVisited:
            if problem.isWumpusClose(pacardState):
                addAllForLabel(Labels.WUMPUS_STENCH,pacardMemoryVisited,pacardState)
            elif problem.isPoisonCapsuleClose(pacardState):
                addAllForLabel(Labels.POISON_CHEMICALS,pacardMemoryVisited,pacardState)
            elif problem.isTeleporterClose(pacardState):
                addAllForLabel(Labels.TELEPORTER_GLOW,pacardMemoryVisited,pacardState)

def addAllForLabel(label,pacardMemoryVisited,pacardState):
    possilities=Labels.INDICATORS|Labels.UNIQUE
    posSet=set()
    for outcome in possilities:
         if outcome==label: posSet.add((True,label))
         else: posSet.add((False,outcome))
    pacardMemoryVisited[pacardState]=posSet
#---------------------------------------------------------------------

#-----------------Memory to clauses ----------------------------------
def genMemoryClausesSet_Relevant(pacardState,pacardMemoryVisited,succStates):
    list=[]
    memKeys=pacardMemoryVisited.keys()
    possilities=Labels.INDICATORS|Labels.UNIQUE

    relevant=set()
    relevant.add(pacardState)
    for succ in succStates:
        relevant.add(succ[0])

    for key in memKeys:
        if key in relevant:
            setForPos=pacardMemoryVisited[key]
            for litPos in setForPos:
                list.append(Clause(set ( [ Literal(litPos[1]+str(key),key,not litPos[0]) ] ) ))

    return set(list)

def genMemoryClauses_NOTList(pacardMemoryVisited):
    list=[]
    memKeys=pacardMemoryVisited.keys()
    possilities=Labels.INDICATORS|Labels.UNIQUE
    for key in memKeys:
        label=pacardMemoryVisited[key][1]
        list.append( Literal(label+str(key),key,True) ) # it is know that every position in memory is true for the label
        #append everything that this position is not        #keep those positions negated in a list of literals, so when they are added to the goal and negated, we can use them for reducing the main clausula
        for outcome in possilities:
            if outcome==label: continue
            list.append( Literal(outcome+str(key),key,False) )
    return list
def genMemoryClausesSet(pacardMemoryVisited):
    list=[]
    memKeys=pacardMemoryVisited.keys()
    for key in memKeys:
        label=pacardMemoryVisited[key][1]
        list.append(Clause(set ( [ Literal(label+str(key),key) ] ) ))

    return set(list)
def genMemoryClauses_NOTList_Relevant(pacardMemoryVisited,pacardState,succStates):
    list=[]
    memKeys=pacardMemoryVisited.keys()
    possilities=Labels.INDICATORS|Labels.UNIQUE

    relevant=set()
    relevant.add(pacardState)
    for succ in succStates:
        relevant.add(succ[0])

    for key in memKeys:
        if key in relevant:
            label=pacardMemoryVisited[key][1]
            list.append( Literal(label+str(key),key,True) ) # it is know that every position in memory is true for the label
            #append everything that this position is not        #keep those positions negated in a list of literals, so when they are added to the goal and negated, we can use them for reducing the main clausula
            for outcome in possilities:
                if outcome==label: continue
                list.append( Literal(outcome+str(key),key,False) )
    return list
#---------------------------------------------------------------------

#----------------------Everything about clauses-----------------------
def generateClausesSet(curState,succStates):
    s=set()
    s|=isStenchClause(curState,succStates)
    s|=isnStenchClause(curState,succStates)
    s|=isChemicalsClause(curState,succStates)
    s|=isntChemicalsClause(curState,succStates)
    s|=isLightClause(curState,succStates)
    s|=isntLightClause(curState,succStates)
    s|=isWumpus(curState,succStates)
    s|=isPassable(curState,succStates)

    #s|=chemThreePoints(curState,succStates)
    #s|=glowThreePoints(curState,succStates)
    #s|=stenchThreePoints(curState,succStates)
    #s|=ifIsThenNotElse(curState,succStates)

    #s1=chemThreePoints(curState,succStates)
    #s2=glowThreePoints(curState,succStates)
    #s3=stenchThreePoints(curState,succStates)
    #s4=ifIsThenNotElse(curState,succStates)
    #s|=s1|s2|s3|s4
    return s

def generateClausesList(curState,succStates):
    s=[]
    s.append(isStenchClause(curState,succStates))
    s.append(isnStenchClause(curState,succStates))
    s.append(isChemicalsClause(curState,succStates))
    s.append(isntChemicalsClause(curState,succStates))
    s.append(isLightClause(curState,succStates))
    s.append(isntLightClause(curState,succStates))
    s.append(isWumpus(curState,succStates))
    s.append(isPassable(curState,succStates))

    return s

def isStenchClause(curState,succStates):
    literals=[]
    literals.append(Literal(Labels.WUMPUS_STENCH+str(curState),curState,True))
    for nS in succStates:
        literals.append(Literal(Labels.WUMPUS+str(nS[0]),nS[0],False))
    return set([Clause(set(literals))])

def isnStenchClause(curState,succStates):
    #literals=[]
    #literals.append(Literal(Labels.WUMPUS_STENCH+str(curState),curState,False))
    #for nS in succStates:
    #    literals.append(Literal(Labels.WUMPUS+str(nS[0]),nS[0],True))
    #return set([Clause(set(literals))])
    list=[]
    for nS in succStates:
        list.append( Clause( set( [ Literal(Labels.WUMPUS_STENCH+str(curState),curState,False), Literal(Labels.WUMPUS+str(nS[0]),nS[0],True) ] ) )  )
    return set(list)

def isChemicalsClause(curState,succStates):
    literals=[]
    literals.append(Literal(Labels.POISON_CHEMICALS+str(curState),curState,True))
    for nS in succStates:
        literals.append(Literal(Labels.POISON+str(nS[0]),nS[0],False))
    return set([Clause(set(literals))])

def isntChemicalsClause(curState,succStates):
    #literals=[]
    #literals.append(Literal(Labels.POISON_CHEMICALS+str(curState),curState,False))
    #for nS in succStates:
    #    literals.append(Literal(Labels.POISON+str(nS[0]),nS[0],True))
    #return set([Clause(set(literals))])
    list=[]
    for nS in succStates:
        list.append( Clause( set( [ Literal(Labels.POISON_CHEMICALS+str(curState),curState,False), Literal(Labels.POISON+str(nS[0]),nS[0],True) ] ) )  )
    return set(list)

def isLightClause(curState,succStates):
    literals=[]
    literals.append(Literal(Labels.TELEPORTER_GLOW+str(curState),curState,True))
    for nS in succStates:
        literals.append(Literal(Labels.TELEPORTER+str(nS[0]),nS[0],False))
    return set([Clause(set(literals))])

def isntLightClause(curState,succStates):
    #literals=[]
    #literals.append(Literal(Labels.TELEPORTER_GLOW+str(curState),curState,True))
    #for nS in succStates:
    #    literals.append(Literal(Labels.TELEPORTER+str(nS[0]),nS[0],False))
    #return set([Clause(set(literals))])
    list=[]
    for nS in succStates:
        list.append( Clause( set( [ Literal(Labels.TELEPORTER_GLOW+str(curState),curState,False), Literal(Labels.TELEPORTER+str(nS[0]),nS[0],True) ] ) )  )
    return set(list)

def isWumpus(curState,succStates):
    """
    Whatch how you use this. It could break some kode.
    :param curState:
    :param succStates:
    :return:
    """
    #literals=[]
    #literals.append(Literal(Labels.WUMPUS+str(curState),curState,False))
    #for nS in succStates:
    #    literals.append(Literal(Labels.WUMPUS+str(nS[0]),nS[0],True))
    #return set([Clause(set(literals))])
    list=[]
    for nS in succStates:
        list.append( Clause( set( [ Literal(Labels.WUMPUS+str(curState),curState,True), Literal(Labels.WUMPUS+str(nS[0]),nS[0],True) ] ) )  )
    return set(list)

def isPassable(curState,succStates):
    """

    """
    list=[]
    for nS in succStates:
        list.append( Clause( set( [ Literal(Labels.WUMPUS_STENCH+str(curState),curState,False), Literal(Labels.POISON_CHEMICALS+str(curState),curState,False), Literal(Labels.TELEPORTER_GLOW+str(curState),curState,False), Literal(Labels.SAFE+str(nS[0]),nS[0],False) ] ) )  )
    return set(list)
#----------------------additional clauses-----------------------------

def glowThreePoints(curState,succStates):
    list=[]

    base=curState

    top=(base[0],base[1]+1)
    right=(base[0]+1,base[1])
    bottom=(base[0],base[1]-1)
    left=(base[0]-1,base[1])

    topRight=(base[0]+1,base[1]+1)
    topLeft=(base[0]-1,base[1]+1)
    bottomRight=(base[0]+1,base[1]-1)
    bottomLeft=(base[0]-1,base[1]-1)

    # all for teleporter right
    rightR=Clause( set( [
        Literal(Labels.TELEPORTER_GLOW+str(base),base,True), \
        Literal(Labels.TELEPORTER_GLOW+str(topRight),topRight,True), \
        Literal(Labels.TELEPORTER_GLOW+str(bottomRight),bottomRight,True), \
        Literal(Labels.TELEPORTER+str(right),right,False), \
    ] ) )

    # ------------------------

    # all for teleporter bottom
    bottomR=Clause( set( [
        Literal(Labels.TELEPORTER_GLOW+str(base),base,True), \
        Literal(Labels.TELEPORTER_GLOW+str(bottomRight),bottomRight,True), \
        Literal(Labels.TELEPORTER_GLOW+str(bottomLeft),bottomLeft,True), \
        Literal(Labels.TELEPORTER+str(bottom),bottom,False), \
    ] ) )

    # ------------------------

    # all for teleporter left
    leftR=Clause( set( [
        Literal(Labels.TELEPORTER_GLOW+str(base),base,True), \
        Literal(Labels.TELEPORTER_GLOW+str(bottomLeft),bottomLeft,True), \
        Literal(Labels.TELEPORTER_GLOW+str(topLeft),topLeft,True), \
        Literal(Labels.TELEPORTER+str(left),left,False), \
    ] ) )
    # ------------------------

    # all for teleporter top
    topR=Clause( set( [
        Literal(Labels.TELEPORTER_GLOW+str(base),base,True), \
        Literal(Labels.TELEPORTER_GLOW+str(topRight),topRight,True), \
        Literal(Labels.TELEPORTER_GLOW+str(topLeft),topLeft,True), \
        Literal(Labels.TELEPORTER+str(top),top,False), \
    ] ) )

    # ------------------------

    list.append( bottomR  )
    list.append( leftR  )
    list.append( rightR  )
    list.append( topR  )

    return set(list)

def stenchThreePoints(curState,succStates):
    list=[]

    base=curState

    top=(base[0],base[1]+1)
    right=(base[0]+1,base[1])
    bottom=(base[0],base[1]-1)
    left=(base[0]-1,base[1])

    topRight=(base[0]+1,base[1]+1)
    topLeft=(base[0]-1,base[1]+1)
    bottomRight=(base[0]+1,base[1]-1)
    bottomLeft=(base[0]-1,base[1]-1)

    # all for teleporter right
    rightR=Clause( set( [
        Literal(Labels.WUMPUS_STENCH+str(base),base,True), \
        Literal(Labels.WUMPUS_STENCH+str(topRight),topRight,True), \
        Literal(Labels.WUMPUS_STENCH+str(bottomRight),bottomRight,True), \
        Literal(Labels.WUMPUS+str(right),right,False), \
    ] ) )

    # ------------------------

    # all for teleporter bottom
    bottomR=Clause( set( [
        Literal(Labels.WUMPUS_STENCH+str(base),base,True), \
        Literal(Labels.WUMPUS_STENCH+str(bottomRight),bottomRight,True), \
        Literal(Labels.WUMPUS_STENCH+str(bottomLeft),bottomLeft,True), \
        Literal(Labels.WUMPUS+str(bottom),bottom,False), \
    ] ) )

    # ------------------------

    # all for teleporter left
    leftR=Clause( set( [
        Literal(Labels.WUMPUS_STENCH+str(base),base,True), \
        Literal(Labels.WUMPUS_STENCH+str(bottomLeft),bottomLeft,True), \
        Literal(Labels.WUMPUS_STENCH+str(topLeft),topLeft,True), \
        Literal(Labels.WUMPUS+str(left),left,False), \
    ] ) )
    # ------------------------

    # all for teleporter top
    topR=Clause( set( [
        Literal(Labels.WUMPUS_STENCH+str(base),base,True), \
        Literal(Labels.WUMPUS_STENCH+str(topRight),topRight,True), \
        Literal(Labels.WUMPUS_STENCH+str(topLeft),topLeft,True), \
        Literal(Labels.WUMPUS+str(top),top,False), \
    ] ) )

    # ------------------------

    list.append( bottomR  )
    list.append( leftR  )
    list.append( rightR  )
    list.append( topR  )

    return set(list)

def chemThreePoints(curState,succStates):
    list=[]

    base=curState

    top=(base[0],base[1]+1)
    right=(base[0]+1,base[1])
    bottom=(base[0],base[1]-1)
    left=(base[0]-1,base[1])

    topRight=(base[0]+1,base[1]+1)
    topLeft=(base[0]-1,base[1]+1)
    bottomRight=(base[0]+1,base[1]-1)
    bottomLeft=(base[0]-1,base[1]-1)

    # all for teleporter right
    rightR=Clause( set( [
        Literal(Labels.POISON_CHEMICALS+str(base),base,True), \
        Literal(Labels.POISON_CHEMICALS+str(topRight),topRight,True), \
        Literal(Labels.POISON_CHEMICALS+str(bottomRight),bottomRight,True), \
        Literal(Labels.POISON+str(right),right,False), \
    ] ) )

    # ------------------------

    # all for teleporter bottom
    bottomR=Clause( set( [
        Literal(Labels.POISON_CHEMICALS+str(base),base,True), \
        Literal(Labels.POISON_CHEMICALS+str(bottomRight),bottomRight,True), \
        Literal(Labels.POISON_CHEMICALS+str(bottomLeft),bottomLeft,True), \
        Literal(Labels.POISON+str(bottom),bottom,False), \
    ] ) )

    # ------------------------

    # all for teleporter left
    leftR=Clause( set( [
        Literal(Labels.POISON_CHEMICALS+str(base),base,True), \
        Literal(Labels.POISON_CHEMICALS+str(bottomLeft),bottomLeft,True), \
        Literal(Labels.POISON_CHEMICALS+str(topLeft),topLeft,True), \
        Literal(Labels.POISON+str(left),left,False), \
    ] ) )
    # ------------------------

    # all for teleporter top
    topR=Clause( set( [
        Literal(Labels.POISON_CHEMICALS+str(base),base,True), \
        Literal(Labels.POISON_CHEMICALS+str(topRight),topRight,True), \
        Literal(Labels.POISON_CHEMICALS+str(topLeft),topLeft,True), \
        Literal(Labels.POISON+str(top),top,False), \
    ] ) )

    # ------------------------

    list.append( bottomR  )
    list.append( leftR  )
    list.append( rightR  )
    list.append( topR  )

    return set(list)

def ifIsThenNotElse(curState,succStates):
    resSet=set()
    for succSt in succStates:
        sucState=succSt[0]
        resSet|=uniquePos(sucState)
    # resState|=uniquePos(curState)
    return resSet

def uniquePos(state):
    possilities=Labels.INDICATORS|Labels.UNIQUE
    list=[]
    for itIs in possilities:
        for itCantBe in possilities:
            if itIs == itCantBe:continue
            list.append(Clause( set( [ Literal(itIs+str(state),state,True), Literal(itCantBe+str(state),state,True) ] ) ))
    return set(list)
#---------------------------------------------------------------------
# Abbreviations
lbs = logicBasedSearch
