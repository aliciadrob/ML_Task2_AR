# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)
# This code has again been hoisted by the CGS Digital Innovation Department
# giving credit to the above authors for the benfit of our education in ML

import math
import random
import sys
import os
import neat
import pygame

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1600
HEIGHT = 880
CAR_SIZE_X = 50
CAR_SIZE_Y = 50
BORDER_COLOR = (255, 255, 255, 255)  # Color To Crash on Hit
current_generation = 0  # Generation counter

"""
The Car Class 

Throughout this section, you will need to explore each function
and provide extenive comments in the spaces denoted by the 
triple quotes(block quotes) """ """.
Your comments should describe each function and what it is doing, 
why it is necessary and where it is being used in the rest of the program.

"""


class Car:
    """1. func __init__:

    This function is the class constructor. This is a special function which is called upon when an
    object of the car class is instantiated. Attributes of the car class are defined here.
    Notably, alive, distance, time, radars and position

    """

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load(
            "car-green.png"
        ).convert()  # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # self.position = [690, 740] # Starting Position
        self.position = [830, 920]  # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False  # Flag For Default Speed Later on

        self.center = [
            self.position[0] + CAR_SIZE_X / 2,
            self.position[1] + CAR_SIZE_Y / 2,
        ]  # Calculate Center

        self.radars = []  # List For Sensors / Radars
        self.drawing_radars = []  # Radars To Be Drawn

        self.alive = True  # Boolean To Check If Car is Crashed

        self.distance = 0  # Distance Driven
        self.time = 0  # Time Passed

    """ 2. func draw:
        This function draws the car sprite, and draws the radar lines.
        screen.blit(self.rotated_sprite, self.position) calls the screen.blit function to draw the sprite and self.position signifies what position the car should be in.
        self.draw_radar(screen) calls the draw_radar function to draw radar lines for the car(s)
    """

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw Sprite
        self.draw_radar(screen)  # OPTIONAL FOR SENSORS

    """ 3. func draw_radar:
        This function is responsible for drawing radar lines, as a visual sensor for the cars
        for radar in self.radars: loops through the self.radars list, containing tuples with the radar's coordinates and the distance between the car and a detected object
        position = radar[0] extracts the coordinates of the radar, and set the position variable to these values
        pygame.draw.line uses the pygame library to draw a line representing the radar's detection range
        pygame.draw.circle uses the pygame library to draw a green circle where the radar detects an object
    """

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    """ 4. func check_collision:
        This function is responsible for determining whether the car has collided with another object
        self.alive = True is used to determine whether or not the car has crashed yet
        for point in self.corners: loops through the list of corner points of the car, or the four corners of the car
        if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR: checks if the pixel colours at the current corner matches the border colour, with game_map.get_at being used to retrieve the coordinates of the car on the map
        if any of the corners are in contact with pixels of the same colour as the border, self.alive = False meaning that the car has collided with an object
    """

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    """ 5. check_radar:
        This function is responsible for the radar sensors detecting obstacles and recording the radar data 
        length = 0 is used to monitor the distance from the centre of the car to the detected object
        x and y represent the coordinates where the radar line starts based on angles and car's coordinates
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300: loops continues whilst (x, y) doesn't equal the border colour and whilst the length of the radar is no more than 300 pixels
        dist = int( is a variable representing the distance from the center of the car to the detected object, calculated using pythagoras theroem, and this distance is appended to the self.radars list
    """

    def check_radar(self, degree, game_map):
        length = 0
        x = int(
            self.center[0]
            + math.cos(math.radians(360 - (self.angle + degree))) * length
        )
        y = int(
            self.center[1]
            + math.sin(math.radians(360 - (self.angle + degree))) * length
        )

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1
            x = int(
                self.center[0]
                + math.cos(math.radians(360 - (self.angle + degree))) * length
            )
            y = int(
                self.center[1]
                + math.sin(math.radians(360 - (self.angle + degree))) * length
            )

        # Calculate Distance To Border And Append To Radars List
        dist = int(
            math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2))
        )
        self.radars.append([(x, y), dist])

    """ 6. func update:
        if not self.speed_set: checks to see if the speed of the car has been set
            if self.speed_set = False, the car's speed is set to 20 and self.speed_set is set to equal "True"
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle) rotates the car based on its current rotation, as well as updating the sprite as to the car's positioning
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed updates the car's x position based off its current angle and speed, attempting to ensure the car moves in the correct trajectory
        self.position[0] = max(self.position[0], 20) sets a minimum x position of 20 pixels to ensure that the car doesn't drive off, or get close to the edge of the screen
        self.position[0] = min(self.position[0], WIDTH - 120) sets a buffer of 120 pixels on the right side of the game frame
        self.distance += self.speed updates the distance variable by adding the current speed, accuratly showing distance driven
        self.time += 1 represents the time passed, the time element is incremented based on the period of time passed since the start of the car simulation
        self.center recalculates the centre of the car (the positioning) from the updated position of the car
        length = 0.5 * CAR_SIZE_X length variable is set to half of the car's width
        left_top, right_top, left_bottom, right_bottom calculated based on updated the car's centre position and angle
        self.check_collision(game_map) used to check if the car has collided with an object yet, and updates the self.alive attribute based on this
        self.radars.clear() clears the self.radars list, ready for teh next update
    """

    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1

        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [
            int(self.position[0]) + CAR_SIZE_X / 2,
            int(self.position[1]) + CAR_SIZE_Y / 2,
        ]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X
        left_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length,
        ]
        right_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length,
        ]
        left_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length,
        ]
        right_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length,
        ]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    """ 7. func get_data(self):
        This function retrieves radar data, and normalises it into normalised data
        radars = self.radars assigns data from the radar sensors to the variable radar
        return_values all values are set to 0, ready to store processed radar data
        for i, radar in enumerate(radars): loops through the values in the radars list, and processes each radar value
        return_values[i] = int(radar[1] / 30) calculates standardised data for the radar snesor data, with radar[1] representing the distance measured by the radar
        return return_values returns the return_values list, with normailsed data based off radar data
    """

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    """ 8. func is_alive:
        This function checks if the car is still alive
        return self.alive returns whether or not the car is alive
    """

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    """ 9. func get_reward:
        This function returns a "reward" for a car's fitness in the simulation
        return self.distance / (CAR_SIZE_X / 2) in this self.distance is divided by half the car's width (CAR_SIZE_X / 2) to calculate the distance travelled in order to calculate the reward
    """

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    """ 10. func rotate_center:
        This function rotates the car around the centre point at a specific angle
        rectangle = image.get_rect() uses the get_rect() to retrieve information regarding the sprits image and positioning
        rotated_image = pygame.transform.rotate(image, angle) uses the pygame library to use the pygame.transform.rotate function and to rotate the image by a specific angle
        rotated_rectangle = rectangle.copy() creates a new copy of the rectangle variable
        rotated_rectangle.center = rotated_image.get_rect().center centre of the copied rectangle is set to match the centre of the rotated rectangle
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy() rectangle is updated to ensure that it remains the correct size with the correct centre
    """

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


""" This Function:

1.  Empty Collections Initialization:
    nets: A list to hold neural networks corresponding to each genome.
    cars: A list to hold instances of the Car class that the neural networks control.
    
2.  Initializing PyGame and Display:
    The Pygame library is initialized, and a display window is created with the specified dimensions.

3.  Creating Neural Networks and Cars:
    For each genome passed into the run_simulation function:
    A neural network is created using the neat.nn.FeedForwardNetwork.create(g, config) method. The genome g and configuration config are used to create the network.
    The neural network is added to the nets list, and the genome's fitness is set to 0.
    A new instance of the Car class is created and added to the cars list.

4.  Clock and Font Settings:
    A PyGame clock is created to control the frame rate of the simulation.
    Different fonts are loaded for displaying information on the screen.

Updating the Generation Counter:

The current_generation global variable is incremented, indicating the current generation being simulated.
Main Simulation Loop:

The loop runs indefinitely, simulating the behavior of each car and updating the neural networks based on their actions.
Event Handling:

PyGame events are processed within the loop.
If the user closes the window or presses the escape key, the program exits.
Car Actions and Neural Network Activation:

For each car, the neural network is activated with the car's sensor data using nets[i].activate(car.get_data()).
The highest value in the output of the neural network determines the car's action: left, right, slow down, or speed up.
Updating Fitness and Car Movement:

For each alive car, the car's fitness is increased, and its position and movement are updated based on its action.
Checking Car Survival:

The number of cars that are still alive is counted.
If no cars are alive, the simulation loop is terminated.
Time Limit for Simulation:

A simple counter is used to roughly limit the duration of the simulation.
Drawing the Game Environment:

The game map is drawn on the screen.
For each alive car, its image is drawn on the screen.
Displaying Information:

Text information about the current generation, number of cars alive, and mean fitness is displayed on the screen.
Updating Display and Frame Rate:

The display is updated with the drawn elements.
The frame rate is controlled using the clock, ensuring a maximum of 60 frames per second.


"""


def run_simulation(genomes, config):
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # Initialize PyGame And The Display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    mean_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load("map3.png").convert()  # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Exit On Quit Event
        """
        Mod: added on keydown/esc to quit the game
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10  # Left
            elif choice == 1:
                car.angle -= 10  # Right
            elif choice == 2:
                if car.speed - 2 >= 12:
                    car.speed -= 2  # Slow Down
            else:
                car.speed += 2  # Speed Up

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40:  # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
        text = generation_font.render(
            "Generation: " + str(current_generation), True, (0, 0, 0)
        )
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        text = mean_font.render(
            "Mean Fitness: " + str(neat.StatisticsReporter().get_fitness_mean()),
            True,
            (0, 0, 0),
        )
        text_rect = text.get_rect()
        text_rect.center = (900, 530)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS


""" 1. This Section: The program main section
    The if __name__ == "__main__": block ensures that the code within it 
    only executes when the script is run directly (not when imported as a module).
    
    The config.txt file settings are loaded into the config variable using Config()
        neat.DefaultGenome
            Various options that control genome node activation, aggregation, bias, 
            compatibility, connection management, feed-forward architecture, response, 
            and weight settings.
            num_hidden, num_inputs, num_outputs: 
            Specifies the number of hidden, input, and output nodes, respectively.
            These parameters collectively define the structure and characteristics 
            of the neural networks represented by the genomes.
            
        neat.DefaultReproduction
            elitism: Specifies the number of elite genomes that are directly passed 
            to the next generation.
            survival_threshold: Sets the survival threshold, indicating the proportion 
            of genomes in each species that are considered for reproduction.
            
        neat.DefaultSpeciesSet
            compatibility_threshold: Specifies the compatibility threshold used for 
            determining species separation. Genomes with compatibility distance below 
            this threshold belong to the same species.
            
        neat.DefaultStagnation
            species_fitness_func: Defines the function to use when determining species 
            fitness. In this case, 'max' indicates that the maximum fitness of a 
            species is used.
            max_stagnation: Specifies the maximum number of generations a species 
            can remain stagnant before it's considered for stagnation and possible 
            extinction.
            species_elitism: Specifies the number of elite genomes from each species 
            that are preserved to the next generation.
            
        config_path
    
    
"""
if __name__ == "__main__":
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)
