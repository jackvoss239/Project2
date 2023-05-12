import pygame
import os
import time
import random
pygame.font.init()

# Set up the window
width, height = 750, 750
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Invaders")

# Load images
red_spaceship = pygame.image.load(os.path.join("assets", "red.png"))
green_spaceship = pygame.image.load(os.path.join("assets", "green.png"))
blue_spaceship = pygame.image.load(os.path.join("assets", "extra.png"))

yellow_spaceship = pygame.image.load(os.path.join("assets", "player.png"))

red_laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
green_laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
blue_laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
yellow_laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "black-background.png")), (width, height))


class Laser:
    def __init__(self, x, y, img):
        """
        Initialize a Laser object.

        Args:
            x (int): X-coordinate of the laser.
            y (int): Y-coordinate of the laser.
            img (pygame.Surface): Laser image.
        """
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        """
        Draw the laser on the window.

        Args:
            window (pygame.Surface): The game window surface.
        """
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        """
        Move the laser vertically.

        Args:
            vel (int): Velocity of the laser.
        """
        self.y += vel

    def off_screen(self, height):
        """
        Check if the laser is off the screen.

        Args:
            height (int): Height of the game window.

        Returns:
            bool: True if the laser is off the screen, False otherwise.
        """
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        """
        Check if the laser collides with another object.

        Args:
            obj: The object to check collision against.

        Returns:
            bool: True if the laser collides with the object, False otherwise.
        """
        return collide(self, obj)


class Ship:
    COOLDOWN = 60

    def __init__(self, x, y, health=100):
        """
        Initialize a Ship object.

        Args:
            x (int): X-coordinate of the ship.
            y (int): Y-coordinate of the ship.
            health (int, optional): Health of the ship. Defaults to 100.
        """
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        """
        Draw the ship and lasers on the window.

        Args:
            window (pygame.Surface): The game window surface.
        """
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        """
        Move the lasers and handle collisions.

        Args:
            vel (int): Velocity of the lasers.
            obj: The object to check collision against.
        """
        
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        """
        Handle the cooldown of the ship's lasers.
        """
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        """
        Create a laser object and add it to the ship's lasers list.
        """
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        """
        Get the width of the ship's image.

        Returns:
            int: Width of the ship's image.
        """
        return self.ship_img.get_width()

    def get_height(self):
        """
        Get the height of the ship's image.

        Returns:
            int: Height of the ship's image.
        """
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = yellow_spaceship
        self.laser_img = yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs, score):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            score += 5
        return score

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    color_map = {
            "red": (red_spaceship, red_laser),
            "green": (green_spaceship, green_laser),
            "blue": (blue_spaceship, blue_laser)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    """
    Check if two objects collide.

    Args:
        obj1: The first object.
        obj2: The second object.

    Returns:
        bool: True if obj1 collides with obj2, False otherwise.
    """
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 120
    score = 0
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("arial", 50)
    lost_font = pygame.font.SysFont("arial", 60)

    enemies = []
    wave_length = 3
    enemy_vel = 1
    laser_vel = 4

    vel = 5
    player = Player(300, 650)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        window.blit(BG, (0, 0))

        #Sets up labels for Lives and Score
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {score}", 1, (255,255,255))

        window.blit(lives_label, (10, 10))
        window.blit(score_label, (width - score_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(window)

        player.draw(window)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            window.blit(lost_label, (width/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        #Handles logic for players lives
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        #Logic for each time you kill a wave of enemies
        if len(enemies) == 0:
            level += 1
            wave_length += 3
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, width - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        #This allows for player movement and attacks
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - vel > 0:
            player.x -= vel
        if keys[pygame.K_d] and player.x + vel + player.get_width() < width:
            player.x += vel
        if keys[pygame.K_w] and player.y - vel > 0:
            player.y -= vel
        if keys[pygame.K_s] and player.y + vel + player.get_height() + 15 < height:
            player.y += vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        #Handles logic for enemies
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 240) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                score += 5
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)


        score = player.move_lasers(-laser_vel, enemies, score)

#function for main menu to run
def main_menu():
    title_font = pygame.font.SysFont("arial", 70)
    run = True
    while run:
        window.blit(BG, (0, 0))
        title_label = title_font.render("Click to start...", 1, (255,255,255))
        window.blit(title_label, (width/2 - title_label.get_width()/2, 350))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()

main_menu()


