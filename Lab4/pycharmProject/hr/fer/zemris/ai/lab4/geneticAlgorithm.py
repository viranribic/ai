import numpy as np

class GeneticAlgorithm(object): 
    """
        Implement a simple generationl genetic algorithm as described in the instructions
    """

    def __init__(	self, chromosomeShape,
                    errorFunction,
                    elitism = 1,
                    populationSize = 25,
                    mutationProbability  = .1,
                    mutationScale = .5,
                    numIterations = 10000,
                    errorTreshold = 1e-6,
                    alpha= 5
                    ):

        self.populationSize = populationSize # size of the population of units
        self.p = mutationProbability # probability of mutation
        self.numIter = numIterations # maximum number of iterations
        self.e = errorTreshold # threshold of error while iterating
        self.f = errorFunction # the error function (reversely proportionl to fitness)
        self.keep = elitism  # number of units to keep for elitism
        self.k = mutationScale # scale of the gaussian noise
        self.alpha=alpha

        self.i = 0 # iteration counter

        # initialize the population randomly from a gaussian distribution
        # with noise 0.1 and then sort the values and store them internally

        self.population = []
        for _ in range(populationSize):
            chromosome = np.random.randn(chromosomeShape) * 0.1

            fitness = self.calculateFitness(chromosome)
            self.population.append((chromosome, fitness))

        # sort descending according to fitness (larger is better)
        self.population = sorted(self.population, key=lambda t: -t[1])

    def step(self):
        """
            Run one iteration of the genetic algorithm. In a single iteration,
            you should create a whole new population by first keeping the best
            units as defined by elitism, then iteratively select parents from
            the current population, apply crossover and then mutation.

            The step function should return, as a tuple:

            * boolean value indicating should the iteration stop (True if
                the learning process is finished, False othwerise)
            * an integer representing the current iteration of the
                algorithm
            * the weights of the best unit in the current iteration

        """
        isDone=False
        self.i += 1

        #############################
        #       YOUR CODE HERE      #
        #############################
        nextPopulation= self.population[0:self.keep]
		#nextPopulation= self.bestN(self.keep)
		
        for _ in range(0,len(self.population[self.keep:])):
            parA=self.selectParents()
            parB=self.selectParents()
            child=self.crossover(parA,parB)
            #child=self.BLXalpha(parA,parB)
            child=self.mutate(child)
            fitness=self.calculateFitness(child)
            nextPopulation.append((child,fitness))

        self.population = sorted(nextPopulation, key=lambda t: -t[1])
        isDone=False
        if self.i < self.numIter:
            isDone=False
        else:
            isDone=True
        iterBestErr=1./self.best()[1]
        if iterBestErr <= self.e:
            isDone=True
        return isDone,self.i,self.best()[0]




    def calculateFitness(self, chromosome):
        """
            Implement a fitness metric as a function of the error of
            a unit. Remember - fitness is larger as the unit is better!
        """
        chromosomeError = self.f(chromosome)
        if chromosomeError == 0:
            return float("inf")
        else:
            return 1./chromosomeError
        #############################
        #       YOUR CODE HERE      #
        #############################
        pass

    def bestN(self, n):
        """
            Return the best n units from the population
        """
        #############################
        #       YOUR CODE HERE      #
        #############################
        self.population = sorted(self.population, key=lambda t: -t[1])
        best = [ x[0] for x in self.population[0:n]]
		#best=self.population[0:n]
        return best
        pass

    def best(self):
        """
            Return the best unit from the population
        """

        #############################
        #       YOUR CODE HERE      #
        #print self.population[0]  ###
        return self.population[0]
        pass

    def selectParents(self):
        """
            Select two parents from the population with probability of
            selection proportional to the fitness of the units in the
            population
        """
        #############################
        #       YOUR CODE HERE      #
        #############################
        import random as rand
        totalFit=0
        for rec in self.population:
            totalFit+=rec[1]
        targetFit=rand.uniform(0,totalFit)
        minFit=0
        maxFit=0
        for chromosome,fitness in self.population:
            maxFit+=fitness
            if minFit <= targetFit < maxFit:
                return chromosome
            minFit+=fitness
        return self.population[0][0] #return best
        pass

    def crossover(self, p1, p2):
        """
            Given two parent units p1 and p2, do a simple crossover by
            averaging their values in order to create a new child unit
        """
        #############################
        #       YOUR CODE HERE      #
        #############################
        return (p1+p2)/2
        pass

    def mutate(self, chromosome):
        """
            Given a unit, mutate its values by applying gaussian noise
            according to the parameter k
        """
        import numpy as np
        p=np.random.uniform(0,1)
        if p<self.p:
            for i in range(0,len(chromosome)):
                chromosome[i]+=np.random.normal(loc=0.0, scale=self.k,size=None)
            return chromosome
        else:
            return chromosome
        #############################
        #       YOUR CODE HERE      #
        #############################
        pass


    def BLXalpha(self,p1,p2):
        chromosome=np.copy(p1)
        for i in range(0,len(chromosome)):
            cmin=min(chromosome[i],p2[i])
            cmax=max(chromosome[i],p2[i])
            I=cmax-cmin
            chromosome[i]=np.random.uniform(cmin-I*self.alpha,cmax+I*self.alpha)
            #chromosome[i]+=np.random.normal(loc=0.0, scale=self.k,size=None)
        return chromosome


