import pygame
from pygame.sprite import Sprite

# Make a class to manage a ship
class Ship(Sprite):


    def __init__(self, ai_game):
        # Initialize the ship and set its starting position
        super().__init__()
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings
        # Load the ship image and get its rect
        self.image = pygame.image.load("images/ship.bmp")
        self.rect = self.image.get_rect()
        # Start each new ship as the bottom center of the screen
        self.x = float(self.rect.x)
        self.rect.midbottom = self.screen_rect.midbottom
        # Movement flags
        self.moving_right = False
        self.moving_left = False

    def update(self):
        # Update the ship's position based on the movement flags
        # Update ship's x-value, not the rect
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        # Update rect object from self.x
        self.rect.x = self.x
        

    # Draw the ship at its vurrent location
    def blitme(self):
        self.screen.blit(self.image, self.rect)


    def center_ship(self):
        # Center the ship on the screen
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

