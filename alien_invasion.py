# # # Creating a Pygame Window and Responding to User Input

import sys
from time import sleep
import pygame
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

# Create overall class to manage game assets and behavior
class AlienInvasion:

    # Initialize the game and create game resources
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        # Create an instance to store game statistics
        # and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        # Create instances for ships, bullets, and aliens.
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        # Generate a fleet of aliens
        self._create_fleet()
        # Create the Play button
        self.play_button = Button(self, "Play")
        # Set the background color
        self.bg_color = (230, 230, 230)

    def _create_fleet(self):
        ### Create a fleet of aliens.
        # Create an alien and find the number of aliens in a row
        # Spacing between each alien is equal to one alien width
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)


    def _create_alien(self, alien_number, row_number):
        # Create an alien and place it in the row
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

        
    def _check_fleet_edges(self):
        # Respond appropriately if any aliens have reached an edge
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        # Drop the entire fleet and change the fleet's direction
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    # Start the main loop for the game
    def run_game(self):
        # Watch for keyboard and mouse input;
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            
            self._update_screen()


    # _check_events() allows the program to isolate the management of different processes within the game
    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            # KEYDOWN and KEYUP recognizes when keys are pressed
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)


    def _check_play_button(self, mouse_pos):
        # Start a new game when the player clicks Play
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset the game settings
            self.settings.initialize_dynamic_settings()
            # Reset the game statistics
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()
            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            # Hide the mouse cursor
            pygame.mouse.set_visible(False)
    

    # Respond to keypresses
    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()


    # Respond to key releases
    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = False


    # Create a new bullet and add it to the bullets group
    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _update_bullets(self):
        # Update position of bullets and get rid of old bullets
        # Update bullet positions
        self.bullets.update()
        # Get rid of bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)       
        self._check_bullet_alien_collisions()


    def _check_bullet_alien_collisions(self):
        # Respond to bullet-alien collisions
        # Remove any bullets and aliens that have collided
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            # Increase level
            self.stats.level += 1
            self.sb.prep_level()


    def _update_aliens(self):
        # Check if the fleet is at an edge (in alien.py), then update positions of all aliens in the fleet
        self._check_fleet_edges()
        self.aliens.update()
        # Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()


    def _check_aliens_bottom(self):
        # Check if any aliens have reached the bottom of the screen
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit
                self._ship_hit
                break

    
    def _ship_hit(self):
        # Respond to the ship being hit by the alien
        if self.stats.ships_left > 0:
            # Decrement "ships_left," then update scoreboard
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()
            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            # Pause
            sleep(0.5)
        else:
            # If the ship has no lives left, the "game_active" process will swtich off,
            # and the mouse will become visible on the screen again
            self.stats.game_active = False
            pygame.mouse.set_visible(True)


    # Update images on the screen, and flip to the new screen
    def _update_screen(self):
        # Redraw the screen during each pass through the loop
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # Draw the score information
        self.sb.show_score()
        # Draw the Play button if the game is active
        if not self.stats.game_active:
            self.play_button.draw_button()
        # Make the most recently drawn screen visible
        pygame.display.flip()


# Make the most recently drawn ship visible
if __name__ == "__main__":
    # Make a game instance, and run the game
    ai = AlienInvasion()
    ai.run_game()
