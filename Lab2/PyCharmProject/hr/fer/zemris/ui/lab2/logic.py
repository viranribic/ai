import util 
import functools 

class Labels:
    """
    Labels describing the WumpusWorld
    """
    WUMPUS = 'w'
    TELEPORTER = 't'
    POISON = 'p'
    SAFE = 'o'

    """
    Some sets for simpler checks
    >>> if literal.label in Labels.DEADLY: 
    >>>     # Don't go there!!!
    """ 
    DEADLY = set([WUMPUS, POISON])
    WTP = set([WUMPUS, POISON, TELEPORTER])

    UNIQUE = set([WUMPUS, POISON, TELEPORTER, SAFE])

    POISON_CHEMICALS = 'c'
    TELEPORTER_GLOW = 'g'
    WUMPUS_STENCH = 's'

    INDICATORS = set([POISON_CHEMICALS, TELEPORTER_GLOW, WUMPUS_STENCH])


def stateWeight(state):
    """
    To ensure consistency in exploring states, they will be sorted 
    according to a simple linear combination. 
    The maps will never be larger than 20x20, and therefore this 
    weighting will be consistent.
    """
    x, y = state 
    return 20*x + y 


@functools.total_ordering
class Literal:
    """
    A literal is an atom or its negation
    In this case, a literal represents if a certain state (x,y) is or is not 
    the location of GhostWumpus, or the poisoned pills.
    """

    def __init__(self, label, state, negative=False):
        """
        Set all values. Notice that the state is remembered twice - you
        can use whichever representation suits you better.
        """
        x,y = state 
        
        self.x = x 
        self.y = y 
        self.state = state 

        self.negative = negative
        self.label = label 

    def __key(self):
        """
        Return a unique key representing the literal at a given point
        """
        return (self.x, self.y, self.negative, self.label)

    def __hash__(self):
        """
        Return the hash value - this operator overloads the hash(object) function.
        """
        return hash(self.__key())

    def __eq__(first, second):
        """
        Check for equality - this operator overloads '=='
        """
        return first.__key() == second.__key()

    def __lt__(self, other):
        """ 
        Less than check
        by using @functools decorator, this is enough to infer ordering
        """
        return stateWeight(self.state) < stateWeight(other.state)

    def __str__(self):
        """
        Overloading the str() operator - convert the object to a string
        """
        if self.negative: return '~' + self.label
        return self.label

    def __repr__(self):
        """
        Object representation, in this case a string
        """
        return self.__str__()

    def copy(self):
        """
        Return a copy of the current literal
        """
        return Literal(self.label, self.state, self.negative)

    def negate(self):
        """
        Return a new Literal containing the negation of the current one
        """
        return Literal(self.label, self.state, not self.negative)

    def isDeadly(self):
        """
        Check if a literal represents a deadly state
        """
        return self.label in Labels.DEADLY

    def isWTP(self):
        """
        Check if a literal represents GhostWumpus, the Teleporter or 
        a poisoned pill
        """
        return self.label in Labels.WTP

    def isSafe(self):
        """
        Check if a literal represents a safe spot
        """
        return self.label == Labels.SAFE

    def isTeleporter(self):
        """
        Check if a literal represents the teleporter
        """
        return self.label == Labels.TELEPORTER




class Clause: 
    """ 
    A disjunction of finitely many unique literals. 
    The Clauses have to be in the CNF so that resolution can be applied to them. The code 
    was written assuming that the clauses are in CNF, and will not work otherwise. 

    A sample of instantiating a clause (~B v C): 

    >>> premise = Clause(set([Literal('b', (0, 0), True), Literal('c', (0, 0), False)]))

    or; written more clearly
    >>> LiteralNotB = Literal('b', (0, 0), True)
    >>> LiteralC = Literal('c', (0, 0), False)

    >>> premise = Clause(set([[LiteralNotB, LiteralC]]))
    """ 

    def __init__(self, literals):
        """
        The constructor for a clause. The clause assumes that the data passed 
        is an iterable (e.g., list, set), or a single literal in case of a unit clause. 
        In case of unit clauses, the Literal is wrapped in a list to be safely passed to 
        the set.
        """
        if not type(literals) == set and not type(literals) == list:
            self.literals = set([literals])
        else:
            self.literals = set(literals)

    def isResolveableWith(self, otherClause):
        """
        Check if a literal from the clause is resolveable by another clause - 
        if the other clause contains a negation of one of the literals.
        e.g., (~A) and (A v ~B) are examples of two clauses containing opposite literals 
        """
        for literal in self.literals: 
            if literal.negate() in otherClause.literals:
                return True 
        return False 

    def isRedundant(self, otherClauses):
        """
        Check if a clause is a subset of another clause.
        """
        for clause in otherClauses:
            if self == clause: continue
            if clause.literals.issubset(self.literals):
                return True
        return False

    def isRedundant2(self, otherClauses):
        """
        Check if a clause is a superset of another clause.
        """
        for clause in otherClauses:
            if self == clause: continue
            if self.literals.issuperset(clause.literals):
                return True
        return False

    def negateAll(self):
        """
        Negate all the literals in the clause to be used 
        as the supporting set for resolution.
        """
        negations = set()
        for literal in self.literals:
            clause = Clause(literal.negate())
            negations.add(clause)
        return negations

    def __str__(self):
        """
        Overloading the str() operator - convert the object to a string
        """
        return ' V '.join([str(literal) for literal in self.literals])

    def __repr__(self):
        """
        The representation of the object
        """
        return self.__str__()

    def isValid(self):
        for literal in self.literals:
            if literal.negate() in self.literals:
                return True
        return False

    def __key(self):
       """
       Return a unique key representing the literal at a given point
       """
       fset=frozenset(self.literals)
       return (fset)

    def __hash__(self):
        """
        Return the hash value - this operator overloads the hash(object) function.
        """
        return hash(self.__key())

    def __eq__(first, second):
        """
        Check for equality - this operator overloads '=='
        """
        return first.__key() == second.__key()

def resolution(clauses, goal=None):
    """
    Implement refutation resolution. 

    The pseudocode for the algorithm of refutation resolution can be found 
    in the slides. The implementation here assumes you will use set of support 
    and simplification strategies. We urge you to go through the slides and 
    carefully design the code before implementing.
    """

    #no need to factorise since the list of literals is wrapped in set

    if len(clauses)==0:
        return False


    resolvedPairs = set()
    setOfSupport = goal.negateAll()
    new = set()

    while(True):
        simplifier(clauses,setOfSupport)
        for (c1,c2) in selectClauses(clauses,setOfSupport,resolvedPairs):
            resolvents=resolvePair(c1,c2)
            resolvedPairs.add((c1,c2))
            if NIL(resolvents):
                return True
            new |= resolvents
        #These line are a part to the new solution:
        if len(new)==0:return False
        clauses|=setOfSupport
        setOfSupport=new
        new=set()
        # These three lines represent the old solution
        #if new <= setOfSupport: return False
        #setOfSupport|=new



def NIL(resolvents):
    for clause in resolvents:
        if len(clause.literals)==0:
            return True
    return False

# simplyfing tecniques----------------------------------------------------
def simplifier(clauses,setOfSupport):
    removeRedundant(clauses,setOfSupport)
    removeValid(clauses)
    removeValid(setOfSupport)


def removeRedundant(clauses, setOfSupport):
    """
    Remove redundant clauses (clauses that are subsets of other clauses)
    from the aforementioned sets.
    Be careful not to do the operation in-place as you will modify the
    original sets. (why?)
    """


    toBeRemovedSOS=set()
    toBeRemovedClauses=set()

    #--------clean clauses--------------------
    for clause in clauses:
        if clause.isRedundant2(clauses):
            toBeRemovedClauses.add(clause)
        # I forgot why this is a bad idea...
        if clause.isRedundant2(setOfSupport):
            toBeRemovedClauses.add(clause)
    for c in toBeRemovedClauses:
        clauses.remove(c)
    #-----------------------------------------


   #????? what if ?????
    #--------clean set of support-------------
    for sos in setOfSupport:
        if sos.isRedundant2(setOfSupport):
            toBeRemovedSOS.add(sos)
            # I forgot why this is a bad idea...
        if sos.isRedundant2(clauses):
            toBeRemovedSOS.add(sos)
    for s in toBeRemovedSOS:
        setOfSupport.remove(s)
        #print s,"\n"
    #-----------------------------------------

def removeValid(clauses):

    toBeRemovedClauses=set()

    #--------clean clauses--------------------
    for clause in clauses:
        if clause.isValid():
            toBeRemovedClauses.add(clause)

    for c in toBeRemovedClauses:
        clauses.remove(c)
    #-----------------------------------------


def resolvePair(firstClause, secondClause):
    """
    Resolve a pair of clauses.
    """
    resolvents=set()
    for literal in firstClause.literals:
            if literal.negate() in secondClause.literals:
                result= firstClause.literals | secondClause.literals
                result.remove(literal)
                result.remove(literal.negate())
                resolvents.add(Clause(result))
    return resolvents
# ------------------------------------------------------------------------

def selectClauses(clauses, setOfSupport, resolvedPairs):
    """
    Select pairs of clauses to resolve.
    """
    list=[]
    #try to make a resolution of setOfSuport clauses with one of the given input clauses
    for sosElement in setOfSupport:
        for clause in clauses:
            if sosElement.isResolveableWith(clause) and (sosElement,clause) not in resolvedPairs:
                list+=[(sosElement,clause)]
    #ass the algorithm progresses and the newer clauses are added, check if one of them reduces with other setOfSupport clauses
    for sosElement1 in setOfSupport:
        for sosElement2 in setOfSupport:
            if sosElement1==sosElement2: continue
            if sosElement1.isResolveableWith(sosElement2) and (sosElement1,sosElement2) not in resolvedPairs:
                list+=[(sosElement1,sosElement2)]

    return set(list)

def testResolution():
    """
    A sample of a resolution problem that should return True. 
    You should come up with your own tests in order to validate your code. 
    """
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
    testP1()
    testLast()


def test1():
    """
    Test A |- A
    :return:
    """
    premise1 = Clause(set([Literal('A', (0, 0))]))
    goal = Clause([Literal('A', (0,0))])

    print "1.Test A |- A ",resolution(set([premise1]), goal)

def test2():
    """
    Test A |- B
    :return:
    """
    premise1 = Clause(set([Literal('A', (0, 0))]))
    goal = Clause([Literal('B', (0,0))])

    print "2.Test A |- B ",resolution(set([premise1]), goal)

def test3():
    """
    Test AvAvA |- A
    :return:
    """
    premise1 = Clause(set([Literal('A', (0, 0)), Literal('A', (0, 0)), Literal('A', (0, 0))]))
    goal = Clause([Literal('A', (0,0))])

    print "3.Test AvAvA |- A ",resolution(set([premise1]), goal)

def test4():
    """
    Test Av~A |-A
    :return:
    """
    premise1 = Clause(set([Literal('A', (0, 0), True), Literal('A', (0, 0), False)]))
    goal = Clause([Literal('A', (0,0))])

    print "4.Test Av~A |-A ",resolution(set([premise1]), goal)

def test5():
    """
    Test Bv~A |-A
    :return:
    """
    premise1 = Clause(set([Literal('A', (0, 0), True), Literal('B', (0, 0), False)]))
    goal = Clause([Literal('A', (0,0))])

    print "5.Test Bv~A |-A ",resolution(set([premise1]), goal)

def test6():
    """
    Test Av~A, BvC, C |- C
    :return:
    """
    premise1 = Clause(set([Literal('A', (0, 0), True), Literal('A', (0, 0), False)]))
    premise2 = Clause(set([Literal('B', (0, 0), False), Literal('C', (0, 0), False)]))
    premise3 = Clause(set([Literal('C', (0, 0), False)]))

    goal = Clause([Literal('C', (0,0))])

    print "6.Test Av~A, BvC, C |- C ",resolution(set([premise1,premise2,premise3]), goal)

def test7():
    """
    Test ~CvB, ~BvE, ~EvB, C, ~Dv~E |- ~D v ~A
    :return:
    """
    premise1 = Clause(set([Literal('B', (0, 0), False), Literal('C', (0, 0), True)]))
    premise2 = Clause(set([Literal('B', (0, 0), True), Literal('E', (0, 0), False)]))
    premise3 = Clause(set([Literal('E', (0, 0), True), Literal('B', (0, 0), False)]))
    premise4 = Clause(set([Literal('C', (0, 0), False)]))
    premise5 = Clause(set([Literal('D', (0, 0), True), Literal('E', (0, 0), True)]))


    goal = Clause([Literal('D', (0,0),True),Literal('A', (0,0),True)])

    print "7.Test ~CvB, ~BvE, ~EvB, C, ~Dv~E |- ~D v ~A ",resolution(set([premise1,premise2,premise3,premise4,premise5]), goal)

def testP1():
    """
    Test ~SvW1vW2vW3vW4, S,W1,W2,W3 |- W4
    One stench but all other explored.
    :return:
    """
    premise1 = Clause(set([Literal('S', (0, 0), True), Literal('W1', (0, 0), False), Literal('W2', (0, 0), False), Literal('W3', (0, 0), False), Literal('W4', (0, 0), False)]))
    premise2 = Clause(set([Literal('W1', (0, 0),True)]))
    premise3 = Clause(set([Literal('W2', (0, 0),True)]))
    premise4 = Clause(set([Literal('W3', (0, 0),True)]))
    premise5 = Clause(set([Literal('S', (0, 0))]))

    goal = Clause(set([Literal('W4', (0, 0))]))

    print "Pacard1: ~SvW1vW2vW3vW4, S,~W1,~W2,~W3 |- W4 ",resolution(set([premise1,premise2,premise3,premise4,premise5]), goal)



def testLast():
    """
    Test ~PvQvR, ~QvS, ~RvS |- ~PvS
    :return:
    """
    premise1 = Clause(set([Literal('P', (0, 0), True), Literal('Q', (0, 0), False), Literal('R', (0, 0), False)]))
    premise2 = Clause(set([Literal('Q', (0, 0), True), Literal('S', (0, 0), False)]))
    premise3 = Clause(set([Literal('R', (0, 0), True), Literal('S', (0, 0), False)]))
    goal = Clause([Literal('P', (0,0),True),Literal('S', (0,0))])

    print "~PvQvR, ~QvS, ~RvS |- ~P ^ S ",resolution(set([premise1, premise2, premise3]), goal)


if __name__ == '__main__':
    """
    The main function - if you run logic.py from the command line by 
    >>> python logic.py 

    this is the starting point of the code which will run. 
    """ 
    testResolution() 