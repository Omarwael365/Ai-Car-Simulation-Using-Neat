import neat
from simulation import run_simulation

if __name__ == "__main__":
    config_path = "./config.txt" 
    config = neat.Config(
        neat.DefaultGenome,         # Defines the blueprint of a neural network (nodes, connections, activation, mutation rules)
        neat.DefaultReproduction,   # Handles how genomes reproduce (crossover, elitism, survival thresholds)
        neat.DefaultSpeciesSet,     # Groups similar genomes into species to maintain diversity and protect innovation
        neat.DefaultStagnation,     # Detects species that stop improving and handles their extinction
        config_path                 # Path to your config file (the one you showed earlier)
    )

    population = neat.Population(config) # Creates a population of neural networks.NEAT initializes: genomes, species, generation counters
    population.add_reporter(neat.StdOutReporter(True)) # Adds a console reporter that prints progress. (generation number, fitness, best genome, species count)
    stats = neat.StatisticsReporter() #Tracks evolution statistics: (average fitness, best fitness, species performance
    population.add_reporter(stats)

    population.run(run_simulation, 1000)

    # NEAT will run up to 1000 generations
    # For each generation, it will call run_simulation() function
    # run_simulation() evaluates each genome by letting cars drive in the Pygame simulation
    # NEAT receives the fitness values from you and evolves better networks

#myenv\Scripts\activate