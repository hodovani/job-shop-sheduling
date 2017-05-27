from .jobshop import *

import random
import time


def select_best(jobs, population, fraction=0.5):
    """Keep best fraction (in [0, 1]) of population"""
    population.sort()
    # get an even number of individuals
    # return population[:(populationSize//4) * 2]
    # select best half
    return population[:max(int(fraction * len(population)), 1)]

def select_richard(jobs, population, dividend=5):
    # richard selection: partition population and keep best of fraction of group
    nextGen = []
    counter = 0
    while counter < len(population):
        nextOffset = random.randint(2, int(len(population)/dividend))
        subPopulation = population[counter:counter+nextOffset]
        nextGen.extend(select_best(jobs, subPopulation))
        counter += nextOffset
    return nextGen

def select_stochastic(jobs, population):
    # stochastic selection
    # better solutions have greater chance to stay but may also be killed
    population = sorted(population)
    nextGen = []
    populationSize = len(population)
    while nextGen == []:
        for i in range(populationSize):
            randomNumber = random.randint(0,populationSize)
            if i < randomNumber:
                nextGen.append(population[i])
            else:
                pass
    return nextGen

def recombine_simpleCrossover(jobs, s1, s2):
    # Recombine with classic crossover
    cut = random.randint(0, len(s1) - 1)
    return normalizeSchedule(jobs, s1[:cut] + s2[cut:])

def mutate_permuteSubsequence(jobs, s, max_shuffle_fraction=4):
    """Mutate by random.shuffling a subsequence of a schedule."""
    a, b = sorted([random.randint(0, len(s) - 1), random.randint(0, len(s) - 1)])

    # The mutation should not be too large.
    # TODO maybe just:
    # b = random.randint(a, j*m//constant)
    # TODO think about probabilities...
    b = min(b, a + len(s) // max_shuffle_fraction)

    shuffle(s, a, b)


def mutate_swap(jobs, s, num_swaps=5):
    """Mutate by swapping two instructions."""
    for swap in range(num_swaps):
        a = random.randint(0, len(s) - 1)
        b = random.randint(0, len(s) - 1)
        s[a], s[b] = s[b], s[a]


def geneticSearchTemplate(jobs, recombine, mutate=mutate_permuteSubsequence, select=select_best,
        populationSize=100, maxTime=None):
    """
    Genetic algorithm for the jobshop scheduling problem.
    """

    numGenerations = 10   # generations calculated between logging
    solutions = []   # list of (time, schedule) with decreasing time
    best = 10000000  # TODO set initial value for max of add check in loop

    t0 = time.time()
    totalGenerations = 0

    j = len(jobs)
    m = len(jobs[0])
    l = j*m
    CR = 0.7
    F = random.random()*2
    genLength = j*m

    # initial generation
    schedules = [randomSchedule(j, m) for i in range(populationSize)]
    fitness = [cost(jobs, s) for s in schedules]

    # TODO rethink datastructure for population
    #   - using (cost, permutation) let us easily sort by cost
    #   - but cost changes in every step and we jsut need to recalculate at the end
    population = list(zip(fitness, schedules))


    for idx in range(numGenerations):
        # (1) selection
        #fittest = select(jobs, population)

        # (2) recombination

        for iPopulation in range(populationSize):
            #calculate new candidate solution
            y = population[iPopulation]
            #pick 3 different random points from population
            while True:
                agentIdxA, agentIdxB, agentIdxC = random.sample(range(0, numGenerations), 3)
                if((agentIdxA != idx ) and (agentIdxB != idx ) and (agentIdxC != idx )):
                    break
            #pick a random index [0-Dimensionality]
            R = random.randint(0,len(population[0][1]))

            #compute the agent's new position
            for genIdx in range(genLength):
                r = random.random()
                if (r<CR) or (genIdx == R):
                    y[1][genIdx] = random.randint(0,m-1)

            normalizedScheduler = normalizeSchedule(jobs,y[1])
            normalizedCost = cost(jobs, normalizedScheduler)
            if(normalizedCost < population[iPopulation][0]):
                population[iPopulation] = (normalizedCost, normalizedScheduler)
            # next_generation.append(
            #     recombine(jobs, random.choice(fittest)[1], random.choice(fittest)[1]))
        #
        # # dummy value for cost
        # population = fittest + [(0, s) for s in next_generation]
        #
        # # (3) mutation
        # for _, individual in population:
        #     mutate(jobs, individual)



        # reevaluate population
        # population = [(cost(jobs, i), i) for _, i in population]

        best_individuum = min(population)

        if best_individuum[0] < best:
            best = best_individuum[0]
            solutions.append(best_individuum)

        totalGenerations += 1

    # print("Generation", totalGenerations)

    # if maxTime and time.time() - t0 >= maxTime:
    #     raise OutOfTime("Time is over")
    #
    # t = time.time() - start
    # if t > 0:
    #     print("Best:", best, "({:.1f} Generations/s, {:.1f} s)".format(
    #             numGenerations/t, time.time() - t0))
    #
    # # Make outputs appear about every 3 seconds.
    # if t > 4:
    #     numGenerations //= 2
    # elif t < 1.5:
    #     numGenerations *= 2

        # except (KeyboardInterrupt, OutOfTime) as e:
        #     print()
        #     print("================================================================================")
        #     print("Best time:", best, "  (lower bound {})".format(lowerBound(jobs)))
        #     print("Best solution:")
        #     print(solutions[-1][1])
        #     print("Found in {:} generations in {:.1f}s".format(totalGenerations, time.time() - t0))
        #
    return solutions[-1]
