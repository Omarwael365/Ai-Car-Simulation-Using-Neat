import math
import pygame

CAR_SIZE_X = 60                  # Width of the car sprite in pixels
CAR_SIZE_Y = 60                  # Height of the car sprite in pixels
BORDER_COLOR = (255, 255, 255, 255)  # Color of the track border (used for collision detection)
WIDTH = 1920                     # Width of the game window
HEIGHT = 1080                    # Height of the game window

class Car:
    def __init__(self):
        # Load and scale car sprite
        self.sprite = pygame.image.load('assets/car.png').convert() 
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite  # Sprite that will be rotated based on car angle

        # Car position, angle, speed
        self.position = [830, 920]  # Initial position on the screen
        self.angle = 0               # Initial rotation angle in degrees
        self.speed = 0               # Current speed of the car
        self.speed_set = False       # Flag to check if initial speed has been set

        # Center coordinates for easier rotation and radar calculations
        self.center = [self.position[0] + CAR_SIZE_X / 2,
                        self.position[1] + CAR_SIZE_Y / 2]

        # Sensor (radar) data
        self.radars = []             # Stores radar endpoints and distances
        self.drawing_radars = []     # Stores radar points for drawing
        self.alive = True            # Is the car alive (not collided)

        # Performance tracking
        self.distance = 0            # Total distance traveled
        self.time = 0                # Time steps alive


    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw rotated car on screen
        self.draw_radar(screen)                          # Draw radar sensors

    def draw_radar(self, screen):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)  # Draw radar line
            pygame.draw.circle(screen, (0, 255, 0), position, 5)             # Draw radar endpoint


    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:  # Check all 4 corners of the car
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False  # Collision detected
                break

    def check_radar(self, degree, game_map):
        length = 0
        # Calculate x, y position along radar ray
        x = int(self.center[0])
        y = int(self.center[1])

        # Extend radar until it hits border or reaches 300 pixels
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length += 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        dist = int(math.sqrt((x - self.center[0])**2 + (y - self.center[1])**2))
        self.radars.append([(x, y), dist])  # Save radar endpoint and distance


    def update(self, game_map):
        # Initialize speed once
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Rotate car sprite based on current angle
        self.rotated_sprite = pygame.transform.rotate(self.sprite, self.angle)

        # Update X position using speed and angle
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)  # Prevent going out of bounds
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Update traveled distance and time
        self.distance += self.speed
        self.time += 1

        # Update Y position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], HEIGHT - 120)

        # Update center coordinates
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2,
                       int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate car corners for collision detection
        length = math.sqrt((CAR_SIZE_X/2)**2 + (CAR_SIZE_Y/2)**2)
        self.corners = [
            [self.center[0] + math.cos(math.radians(360 - (self.angle + a))) * length,
             self.center[1] + math.sin(math.radians(360 - (self.angle + a))) * length]
            for a in [30, 150, 210, 330]
        ]

        # Check collision
        self.check_collision(game_map)

        # Update radar sensors
        self.radars.clear()
        for d in range(-90, 120, 45):  # Radars at -90°, -45°, 0°, 45°, 90° relative to car
            self.check_radar(d, game_map)


    def get_data(self):
        # Returns radar distances divided by 30 for normalization
        # If less than 5 radars, pad with zeros
        return [(r[1] // 30) for r in self.radars] + [0] * (5 - len(self.radars))

    def is_alive(self):
        return self.alive  # Returns whether car is alive (not collided)

    def get_reward(self):
        return self.distance / (CAR_SIZE_X / 2)  # Reward based on distance traveled
