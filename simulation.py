import sys        # System functions (e.g., exit the program)
import pygame     # For graphics, input handling, and game loop
import neat       # NeuroEvolution of Augmenting Topologies (NEAT AI)
from car import Car  # Import the Car class (handles car behavior, sensors, collisions)

WIDTH = 1920                  # Width of the game window
HEIGHT = 1080                 # Height of the game window
current_generation = 0        # Tracks the current NEAT generation

# --- Main simulation function ---
def run_simulation(genomes, config):
    global current_generation
    current_generation += 1  # Increment generation count

    # --- Initialize neural networks and cars ---
    nets = []   # Stores neural networks created from genomes
    cars = []   # Stores Car objects controlled by neural networks

    # Initialize Pygame and screen
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    # Load track image (used for rendering and collision detection)
    game_map = pygame.image.load('assets/map2.png').convert()

    # Create a neural network and Car object for each genome
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)  # Create feedforward network from genome
        nets.append(net)
        genome.fitness = 0      # Initialize fitness score for each genome
        cars.append(Car())      # Create a Car object controlled by this network

    # Clock to manage framerate
    clock = pygame.time.Clock()
    counter = 0  # Frame counter (used to limit simulation time)

    # Fonts for displaying information on screen
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)

    # --- Simulation loop ---
    while True:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)  # Exit program if window is closed

        # --- Neural network decisions ---
        for i, car in enumerate(cars):
            # Get radar data from the car (sensor distances)
            output = nets[i].activate(car.get_data())
            # Select the action with the highest output
            decision = output.index(max(output))

            # Map neural network output to car actions
            if decision == 0:
                car.angle += 10        # Turn right
            elif decision == 1:
                car.angle -= 10        # Turn left
            elif decision == 2 and car.speed >= 14:
                car.speed -= 2         # Slow down (if speed is above minimum)
            elif decision == 3:
                car.speed += 2         # Speed up

        # --- Update cars and fitness ---
        alive_count = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                alive_count += 1
                car.update(game_map)                    # Update car movement, radar, and collisions
                genomes[i][1].fitness += car.get_reward()  # Reward genome based on distance traveled

        # End simulation if all cars have crashed
        if alive_count == 0:
            break

        # End simulation if maximum time/frames reached
        counter += 1
        if counter >= 30 * 40:  # Example: 40 seconds at 30 FPS
            break

        # --- Drawing ---
        screen.blit(game_map, (0, 0))  # Draw track background

        for car in cars:
            if car.is_alive():
                car.draw(screen)  # Draw each alive car and its radars

        # Display generation number in blue
        text = generation_font.render(f"Generation: {current_generation}", True, (0, 0, 255))
        screen.blit(text, (900, 450))
        
        # Display number of cars still alive in blue
        text = alive_font.render(f"Still Alive: {alive_count}", True, (0, 0, 255))
        screen.blit(text, (900, 490))

        # Update display
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second