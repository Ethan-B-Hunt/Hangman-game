import pygame  
import random  
import sys  
  
# Initialize Pygame  
pygame.init()  
  
# Game settings  
GRID_SIZE = 10  
CELL_SIZE = 50  
WIDTH = GRID_SIZE * CELL_SIZE * 2  
HEIGHT = GRID_SIZE * CELL_SIZE + 300  
  
# Colors  
WHITE = (255, 255, 255)  
BLUE = (0, 0, 255)  
GREEN = (0, 255, 0)  
RED = (255, 0, 0)  
GRAY = (169, 169, 169)  
BLACK = (0, 0, 0)  
LIGHT_BLUE = (173, 216, 230)  
LIGHT_GRAY = (211, 211, 211)  
DARK_BLUE = (0, 0, 139)  
NAVY_BLUE = (0, 0, 128)  
  
# Sound effects  
HIT_SOUND = 'sound-effects/cannonball-89596.mp3'  
MISS_SOUND = 'sound-effects/water-splash-199583.mp3'  
WIN_SOUND = 'sound-effects/victorymale-version-230553.mp3'  
LOSE_SOUND = 'sound-effects/fail-144746.mp3'  
CLICK_SOUND = 'sound-effects/mouse-click-sound-233951.mp3'  
SINK_SOUND = 'sound-effects/sinking.mp3'  
  
class BattleshipGame:  
   def __init__(self):  
      self.player_grid = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
      self.computer_grid = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
      self.player_guesses = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
      self.computer_guesses = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
      self.boat_sizes = [1, 1, 3, 3, 4]  
      self.boat_positions = []  
      self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  
      pygame.display.set_caption("Battleship Game")  
      self.start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 40)  
      self.quit_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 40)  
      self.ships_placed = 0  
      self.game_started = False  
      self.score = 0  
      self.font = pygame.font.Font(None, 30)  
      self.title_font = pygame.font.Font(None, 60)  
      self.player_ships_left = len(self.boat_sizes)  
      self.computer_ships_left = len(self.boat_sizes)  
      self.dragging = False  
      self.dragged_boat = None  
      self.boat_orientation = 'H'  
      self.boat_rects = []  
      self.last_hit = None  
  
      # Load boat images  
      self.boat_images = {  
        1: pygame.image.load('boats/s_boat.png'),  
        3: pygame.image.load('boats/m_boat.png'),  
        4: pygame.image.load('boats/l_boat.png')  
      }  
  
  
      # Load sound effects  
      pygame.mixer.init()  
      try:  
        self.hit_sound = pygame.mixer.Sound(HIT_SOUND)  
        self.miss_sound = pygame.mixer.Sound(MISS_SOUND)  
        self.win_sound = pygame.mixer.Sound(WIN_SOUND)  
        self.lose_sound = pygame.mixer.Sound(LOSE_SOUND)  
        self.click_sound = pygame.mixer.Sound(CLICK_SOUND)  
        self.sink_sound = pygame.mixer.Sound(SINK_SOUND)  
      except FileNotFoundError:  
        print("One or more sound files not found. Continuing without sound effects.")  
  
   def draw_grid(self, x_offset, background_color):  
      pygame.draw.rect(self.screen, background_color, (x_offset, 200, GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))  
      for row in range(GRID_SIZE):  
        for col in range(GRID_SIZE):  
           pygame.draw.rect(self.screen, GRAY, (col * CELL_SIZE + x_offset, row * CELL_SIZE + 200, CELL_SIZE, CELL_SIZE), 1)  
  
   def draw_ships(self):  
      for row in range(GRID_SIZE):  
        for col in range(GRID_SIZE):  
           if self.player_grid[row][col] == 'S':  
              boat_size = self.get_boat_size(row, col)  
              if boat_size == 1:  
                self.screen.blit(self.boat_images[1], (col * CELL_SIZE, row * CELL_SIZE + 200))  
              elif boat_size == 3:  
                if self.boat_orientation == 'H':  
                   self.screen.blit(self.boat_images[3], (col * CELL_SIZE - CELL_SIZE, row * CELL_SIZE + 200))  
                else:  
                   self.screen.blit(pygame.transform.rotate(self.boat_images[3], 90), (col * CELL_SIZE, row * CELL_SIZE + 200 - CELL_SIZE))  
              elif boat_size == 4:  
                if self.boat_orientation == 'H':  
                   self.screen.blit(self.boat_images[4], (col * CELL_SIZE - CELL_SIZE * 1.5, row * CELL_SIZE + 200))  
                else:  
                   self.screen.blit(pygame.transform.rotate(self.boat_images[4], 90), (col * CELL_SIZE, row * CELL_SIZE + 200 - CELL_SIZE * 1.5))  
           elif self.computer_grid[row][col] == 'S' and self.computer_guesses[row][col] == 'X':  
              boat_size = self.get_boat_size(row, col)  
              if boat_size == 1:  
                self.screen.blit(self.boat_images[1], (col * CELL_SIZE + WIDTH // 2, row * CELL_SIZE + 200))  
              elif boat_size == 3:  
                if self.boat_orientation == 'H':  
                   self.screen.blit(self.boat_images[3], (col * CELL_SIZE - CELL_SIZE + WIDTH // 2, row * CELL_SIZE + 200))  
                else:  
                   self.screen.blit(pygame.transform.rotate(self.boat_images[3], 90), (col * CELL_SIZE + WIDTH // 2, row * CELL_SIZE + 200 - CELL_SIZE))  
              elif boat_size == 4:  
                if self.boat_orientation == 'H':  
                   self.screen.blit(self.boat_images[4], (col * CELL_SIZE - CELL_SIZE * 1.5 + WIDTH // 2, row * CELL_SIZE + 200))  
                else:  
                   self.screen.blit(pygame.transform.rotate(self.boat_images[4], 90), (col * CELL_SIZE + WIDTH // 2, row * CELL_SIZE + 200 - CELL_SIZE * 1.5))  
  
   def get_boat_size(self, row, col):  
      # Check if the current cell is part of a horizontal boat  
      if col > 0 and self.player_grid[row][col - 1] == 'S':  
        # Check if the current cell is the leftmost cell of the boat  
        if col == 1 or self.player_grid[row][col - 2] != 'S':  
           boat_size = 1  
           while col + boat_size < GRID_SIZE and self.player_grid[row][col + boat_size] == 'S':  
              boat_size += 1  
           return boat_size  
  
      # Check if the current cell is part of a vertical boat  
      if row > 0 and self.player_grid[row - 1][col] == 'S':  
        # Check if the current cell is the topmost cell of the boat  
        if row == 1 or self.player_grid[row - 2][col] != 'S':  
           boat_size = 1  
           while row + boat_size < GRID_SIZE and self.player_grid[row + boat_size][col] == 'S':  
              boat_size += 1  
           return boat_size  
  
      # If the current cell is not part of a horizontal or vertical boat, return 1  
      return 1  
  
   def draw_hits_and_misses(self):  
      for row in range(GRID_SIZE):  
        for col in range(GRID_SIZE):  
           if self.computer_guesses[row][col] == 'X':  
              pygame.draw.circle(self.screen, RED, (col * CELL_SIZE + CELL_SIZE // 2 + WIDTH // 2, row * CELL_SIZE + CELL_SIZE // 2 + 200), CELL_SIZE // 4)  
           elif self.computer_guesses[row][col] == 'O':  
              pygame.draw.circle(self.screen, BLACK, (col * CELL_SIZE + CELL_SIZE // 2 + WIDTH // 2, row * CELL_SIZE + CELL_SIZE // 2 + 200), CELL_SIZE // 4)  
           if self.player_guesses[row][col] == 'X':  
              pygame.draw.circle(self.screen, RED, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2 + 200), CELL_SIZE // 4)  
           elif self.player_guesses[row][col] == 'O':  
              pygame.draw.circle(self.screen, BLACK, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2 + 200), CELL_SIZE // 4)  
  
   def is_valid_placement(self, grid, row, col, ship_size, orientation):  
      if orientation == 'H':  
        if col + ship_size > GRID_SIZE:  
           return False  
        for i in range(ship_size):  
           if grid[row][col + i] != '~':  
              return False  
      elif orientation == 'V':  
        if row + ship_size > GRID_SIZE:  
           return False  
        for i in range(ship_size):  
           if grid[row + i][col] != '~':  
              return False  
      return True  
  
   def place_ship(self, grid, row, col, ship_size, orientation):  
      if orientation == 'H':  
        for i in range(ship_size):  
           grid[row][col + i] = 'S'  
      elif orientation == 'V':  
        for i in range(ship_size):  
           grid[row + i][col] = 'S'  
  
   def player_place_ship(self, ship_size):  
      ship_placed = False  
      boat_rect = pygame.Rect(50, 50, ship_size * CELL_SIZE, CELL_SIZE)  
      dragging = False  
      while not ship_placed:  
        for event in pygame.event.get():  
           if event.type == pygame.QUIT:  
              pygame.quit()  
              sys.exit()  
           if event.type == pygame.MOUSEBUTTONDOWN:  
              mouse_pos = pygame.mouse.get_pos()  
              if boat_rect.collidepoint(mouse_pos):  
                dragging = True  
              if self.start_button_rect.collidepoint(mouse_pos):  
                if self.ships_placed == len(self.boat_sizes):  
                   self.game_started = True  
                   return  
           if event.type == pygame.MOUSEBUTTONUP:  
              dragging = False  
              mouse_pos = pygame.mouse.get_pos()  
              col = (mouse_pos[0] - 0) // CELL_SIZE  
              row = (mouse_pos[1] - 200) // CELL_SIZE  
              if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:  
                if self.is_valid_placement(self.player_grid, row, col, ship_size, self.boat_orientation):  
                   self.place_ship(self.player_grid, row, col, ship_size, self.boat_orientation)  
                   ship_placed = True  
                   self.boat_positions.append((row, col, ship_size, self.boat_orientation))  
                   self.ships_placed += 1  
                   return  
           if event.type == pygame.MOUSEMOTION and dragging:  
              mouse_pos = pygame.mouse.get_pos()  
              boat_rect.x = mouse_pos[0]  
              boat_rect.y = mouse_pos[1]  
           if event.type == pygame.KEYDOWN:  
              if event.key == pygame.K_r:  
                self.boat_orientation = 'H' if self.boat_orientation == 'V' else 'V'  
        self.screen.fill(WHITE)  
        player_text = self.font.render("Player's Board", True, BLACK)  
        self.screen.blit(player_text, (WIDTH // 4 - player_text.get_width() // 2, 150))  
        computer_text = self.font.render("Computer's Board", True, BLACK)  
        self.screen.blit(computer_text, (WIDTH // 4 * 3 - computer_text.get_width() // 2, 150))  
        self.draw_grid(0, LIGHT_BLUE)  
        self.draw_grid(WIDTH // 2, LIGHT_GRAY)  
        self.draw_ships()  
        self.draw_hits_and_misses()  
        pygame.draw.rect(self.screen, BLUE, boat_rect)  
        ships_left_text = self.font.render(f"Ships left to place: {len(self.boat_sizes) - self.ships_placed}", True, BLACK)  
        self.screen.blit(ships_left_text, (WIDTH // 2 - ships_left_text.get_width() // 2, 100))  
        orientation_text = self.font.render(f"Orientation: {self.boat_orientation}", True, BLACK)  
        self.screen.blit(orientation_text, (WIDTH // 2 - orientation_text.get_width() // 2, 120))  
        if self.ships_placed < len(self.boat_sizes):  
           pygame.draw.rect(self.screen, GRAY, self.start_button_rect)  
           start_text = self.font.render("Start Game", True, BLACK)  
           self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT - 70))  
        else:  
           pygame.draw.rect(self.screen, LIGHT_BLUE, self.start_button_rect)  
           start_text = self.font.render("Start Game", True, BLACK)  
           self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT - 70))  
        pygame.display.flip()  
  
   def computer_place_ships(self):  
      for ship_size in self.boat_sizes:  
        while True:  
           row = random.randint(0, GRID_SIZE - 1)  
           col = random.randint(0, GRID_SIZE - 1)  
           orientation = random.choice(['H', 'V'])  
           if self.is_valid_placement(self.computer_grid, row, col, ship_size, orientation):  
              self.place_ship(self.computer_grid, row, col, ship_size, orientation)  
              break  
  
   def main_menu(self):  
      title_text = self.title_font.render("Battleship Game", True, WHITE)  
      start_text = self.font.render("Start", True, WHITE)  
      quit_text = self.font.render("Quit", True, WHITE)  
      self.screen.fill(NAVY_BLUE)  
      self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))  
      start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 40)  
      quit_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 40)  
      pygame.draw.rect(self.screen, LIGHT_BLUE, start_rect)  
      pygame.draw.rect(self.screen, LIGHT_BLUE, quit_rect)  
      self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 10))  
      self.screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 60))  
      pygame.display.flip()  
  
      waiting = True  
      while waiting:  
        for event in pygame.event.get():  
           if event.type == pygame.QUIT:  
              pygame.quit()  
              sys.exit()  
           if event.type == pygame.MOUSEBUTTONDOWN:  
              if start_rect.collidepoint(event.pos):  
                waiting = False  
                self.click_sound.play()  
              elif quit_rect.collidepoint(event.pos):  
                pygame.quit()  
                sys.exit()  
           if event.type == pygame.MOUSEMOTION:  
              if start_rect.collidepoint(event.pos):  
                pygame.draw.rect(self.screen, DARK_BLUE, start_rect)  
              else:  
                pygame.draw.rect(self.screen, LIGHT_BLUE, start_rect)  
              if quit_rect.collidepoint(event.pos):  
                pygame.draw.rect(self.screen, DARK_BLUE, quit_rect)  
              else:  
                pygame.draw.rect(self.screen, LIGHT_BLUE, quit_rect)  
              self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 10))  
              self.screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 60))  
              pygame.display.flip()  
  
   def check_winner(self):  
      player_wins = True  
      for row in range(GRID_SIZE):  
        for col in range(GRID_SIZE):  
           if self.computer_grid[row][col] == 'S' and self.computer_guesses[row][col] != 'X':  
              player_wins = False  
              break  
        if not player_wins:  
           break  
  
      computer_wins = True  
      for row in range(GRID_SIZE):  
        for col in range(GRID_SIZE):  
           if self.player_grid[row][col] == 'S' and self.player_guesses[row][col] != 'X':  
              computer_wins = False  
              break  
        if not computer_wins:  
           break  
  
      return player_wins, computer_wins  
  
   def computer_move(self):  
      if self.last_hit is not None:  
        row, col = self.last_hit  
        if self.player_grid[row][col] == 'S':  
           if row > 0 and self.player_guesses[row - 1][col] == '~':  
              self.player_guesses[row - 1][col] = 'X' if self.player_grid[row - 1][col] == 'S' else 'O'  
              if self.player_grid[row - 1][col] == 'S':  
                self.hit_sound.play()  
                self.last_hit = (row - 1, col)  
              else:  
                self.miss_sound.play()  
                self.last_hit = None  
              return  
           elif row < GRID_SIZE - 1 and self.player_guesses[row + 1][col] == '~':  
              self.player_guesses[row + 1][col] = 'X' if self.player_grid[row + 1][col] == 'S' else 'O'  
              if self.player_grid[row + 1][col] == 'S':  
                self.hit_sound.play()  
                self.last_hit = (row + 1, col)  
              else:  
                self.miss_sound.play()  
                self.last_hit = None  
              return  
           elif col > 0 and self.player_guesses[row][col - 1] == '~':  
              self.player_guesses[row][col - 1] = 'X' if self.player_grid[row][col - 1] == 'S' else 'O'  
              if self.player_grid[row][col - 1] == 'S':  
                self.hit_sound.play()  
                self.last_hit = (row, col - 1)  
              else:  
                self.miss_sound.play()  
                self.last_hit = None  
              return  
           elif col < GRID_SIZE - 1 and self.player_guesses[row][col + 1] == '~':  
              self.player_guesses[row][col + 1] = 'X' if self.player_grid[row][col + 1] == 'S' else 'O'  
              if self.player_grid[row][col + 1] == 'S':  
                self.hit_sound.play()  
                self.last_hit = (row, col + 1)  
              else:  
                self.miss_sound.play()  
                self.last_hit = None  
              return  
      while True:  
        row = random.randint(0, GRID_SIZE - 1)  
        col = random.randint(0, GRID_SIZE - 1)  
        if self.player_guesses[row][col] == '~':  
           self.player_guesses[row][col] = 'X' if self.player_grid[row][col] == 'S' else 'O'  
           if self.player_grid[row][col] == 'S':  
              self.hit_sound.play()  
              self.last_hit = (row, col)  
           else:  
              self.miss_sound.play()  
           break  
  
   def is_ship_destroyed(self, grid, row, col):  
      ship_destroyed = True  
      if grid[row][col] == 'S':  
        if row > 0 and grid[row - 1][col] == 'S':  
           ship_destroyed = False  
        if row < GRID_SIZE - 1 and grid[row + 1][col] == 'S':  
           ship_destroyed = False  
        if col > 0 and grid[row][col - 1] == 'S':  
           ship_destroyed = False  
        if col < GRID_SIZE - 1 and grid[row][col + 1] == 'S':  
           ship_destroyed = False  
      return ship_destroyed  
  
   def update_ships_left(self):  
      self.player_ships_left = 0  
      self.computer_ships_left = 0  
      for row in range(GRID_SIZE):  
        for col in range(GRID_SIZE):  
           if self.player_grid[row][col] == 'S' and self.player_guesses[row][col] != 'X':  
              self.player_ships_left += 1  
           if self.computer_grid[row][col] == 'S' and self.computer_guesses[row][col] != 'X':  
              self.computer_ships_left += 1  
  
   def game_over_menu(self, winner):  
      if winner == "Computer":  
        self.lose_sound.play()  
      else:  
        self.win_sound.play()  
      game_over_text = self.font.render(f"{winner} Wins!", True, BLACK)  
      play_again_text = self.font.render("Play Again", True, BLACK)  
      main_menu_text = self.font.render("Main Menu", True, BLACK)  
      exit_text = self.font.render("Exit", True, BLACK)  
  
      play_again_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 40)  
      main_menu_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 40)  
      exit_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 40)  
  
      waiting = True  
      while waiting:  
        for event in pygame.event.get():  
           if event.type == pygame.QUIT:  
              pygame.quit()  
              sys.exit()  
           if event.type == pygame.MOUSEBUTTONDOWN:  
              if play_again_rect.collidepoint(event.pos):  
                self.player_grid = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
                self.computer_grid = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
                self.player_guesses = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
                self.computer_guesses = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
                self.boat_positions = []  
                self.ships_placed = 0  
                self.game_started = False  
                self.score = 0  
                self.player_ships_left = len(self.boat_sizes)  
                self.computer_ships_left = len(self.boat_sizes)  
                waiting = False  
                self.click_sound.play()  
                self.game_loop()  
              elif main_menu_rect.collidepoint(event.pos):  
                self.player_grid = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
                self.computer_grid = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
                self.player_guesses = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
                self.computer_guesses = [['~'] * GRID_SIZE for _ in range(GRID_SIZE)]  
                self.boat_positions = []  
                self.ships_placed = 0  
                self.game_started = False  
                self.score = 0  
                self.player_ships_left = len(self.boat_sizes)  
                self.computer_ships_left = len(self.boat_sizes)  
                waiting = False  
                self.click_sound.play()  
                self.main_menu()  
                self.game_loop()  
              elif exit_rect.collidepoint(event.pos):  
                pygame.quit()  
                sys.exit()  
  
        self.screen.fill(WHITE)  
        player_text = self.font.render("Player's Board", True, BLACK)  
        self.screen.blit(player_text, (WIDTH // 4 - player_text.get_width() // 2, 150))  
        computer_text = self.font.render("Computer's Board", True, BLACK)  
        self.screen.blit(computer_text, (WIDTH // 4 * 3 - computer_text.get_width() // 2, 150))  
        self.draw_grid(0, LIGHT_BLUE)  
        self.draw_grid(WIDTH // 2, LIGHT_GRAY)  
        self.draw_ships()  
        self.draw_hits_and_misses()  
        self.update_ships_left()  
        player_ships_left_text = self.font.render(f"Player Ships Left: {self.player_ships_left}", True, BLACK)  
        self.screen.blit(player_ships_left_text, (10, 10))  
        computer_ships_left_text = self.font.render(f"Computer Ships Left: {self.computer_ships_left}", True, BLACK)  
        self.screen.blit(computer_ships_left_text, (WIDTH - computer_ships_left_text.get_width() - 10, 10))  
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))  
        if play_again_rect.collidepoint(pygame.mouse.get_pos()):  
           pygame.draw.rect(self.screen, DARK_BLUE, play_again_rect)  
        else:  
           pygame.draw.rect(self.screen, LIGHT_BLUE, play_again_rect)  
        self.screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 2 - 40))  
        if main_menu_rect.collidepoint(pygame.mouse.get_pos()):  
           pygame.draw.rect(self.screen, DARK_BLUE, main_menu_rect)  
        else:  
           pygame.draw.rect(self.screen, LIGHT_BLUE, main_menu_rect)  
        self.screen.blit(main_menu_text, (WIDTH // 2 - main_menu_text.get_width() // 2, HEIGHT // 2 + 10))  
        if exit_rect.collidepoint(pygame.mouse.get_pos()):  
           pygame.draw.rect(self.screen, DARK_BLUE, exit_rect)  
        else:  
           pygame.draw.rect(self.screen, LIGHT_BLUE, exit_rect)  
        self.screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 60))  
        pygame.display.flip()  
  
   def game_loop(self):  
      self.main_menu()  
  
      self.screen.fill(WHITE)  
      pygame.display.flip()  
  
      for ship_size in self.boat_sizes:  
        self.player_place_ship(ship_size)  
  
      self.computer_place_ships()  
  
      self.game_started = True  
  
      while self.game_started:  
        self.screen.fill(WHITE)  
        player_text = self.font.render("Player's Board", True, BLACK)  
        self.screen.blit(player_text, (WIDTH // 4 - player_text.get_width() // 2, 150))  
        computer_text = self.font.render("Computer's Board", True, BLACK)  
        self.screen.blit(computer_text, (WIDTH // 4 * 3 - computer_text.get_width() // 2, 150))  
        self.draw_grid(0, LIGHT_BLUE)  
        self.draw_grid(WIDTH // 2, LIGHT_GRAY)  
        self.draw_ships()  
        self.draw_hits_and_misses()  
        self.update_ships_left()  
        player_ships_left_text = self.font.render(f"Player Ships Left: {self.player_ships_left}", True, BLACK)  
        self.screen.blit(player_ships_left_text, (10, 10))  
        computer_ships_left_text = self.font.render(f"Computer Ships Left: {self.computer_ships_left}", True, BLACK)  
        self.screen.blit(computer_ships_left_text, (WIDTH - computer_ships_left_text.get_width() - 10, 10))  
  
        player_wins, computer_wins = self.check_winner()  
        if player_wins:  
           self.game_started = False  
           self.win_sound.play()  
           self.game_over_menu("Player")  
        elif computer_wins:  
           self.game_started = False  
           self.lose_sound.play()  
           self.game_over_menu("Computer")  
  
        pygame.display.flip()  
  
        if self.game_started:  
           player_clicked = False  
           while not player_clicked:  
              for event in pygame.event.get():  
                if event.type == pygame.QUIT:  
                   pygame.quit()  
                   sys.exit()  
                if event.type == pygame.MOUSEBUTTONDOWN:  
                   mouse_pos = pygame.mouse.get_pos()  
                   if mouse_pos[0] >= WIDTH // 2:  
                      col = (mouse_pos[0] - WIDTH // 2) // CELL_SIZE  
                      row = (mouse_pos[1] - 200) // CELL_SIZE  
                      if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and self.computer_guesses[row][col] == '~':  
                        if self.computer_grid[row][col] == 'S':  
                           self.computer_guesses[row][col] = 'X'  
                           self.hit_sound.play()  
                           if self.is_ship_destroyed(self.computer_grid, row, col):  
                              self.sink_sound.play()  
                              self.computer_ships_left -= 1  
                        else:  
                           self.computer_guesses[row][col] = 'O'  
                           self.miss_sound.play()  
                        player_clicked = True  
  
           self.screen.fill(WHITE)  
           player_text = self.font.render("Player's Board", True, BLACK)  
           self.screen.blit(player_text, (WIDTH // 4 - player_text.get_width() // 2, 150))  
           computer_text = self.font.render("Computer's Board", True, BLACK)  
           self.screen.blit(computer_text, (WIDTH // 4 * 3 - computer_text.get_width() // 2, 150))  
           self.draw_grid(0, LIGHT_BLUE)  
           self.draw_grid(WIDTH // 2, LIGHT_GRAY)  
           self.draw_ships()  
           self.draw_hits_and_misses()  
           self.update_ships_left()  
           player_ships_left_text = self.font.render(f"Player Ships Left: {self.player_ships_left}", True, BLACK)  
           self.screen.blit(player_ships_left_text, (10, 10))  
           computer_ships_left_text = self.font.render(f"Computer Ships Left: {self.computer_ships_left}", True, BLACK)  
           self.screen.blit(computer_ships_left_text, (WIDTH - computer_ships_left_text.get_width() - 10, 10))  
           pygame.display.flip()  
  
           self.computer_move()  
           for row in range(GRID_SIZE):  
              for col in range(GRID_SIZE):  
                if self.player_guesses[row][col] == 'X' and self.is_ship_destroyed(self.player_grid, row, col):  
                   self.sink_sound.play()  
                   self.player_ships_left -= 1  
           pygame.time.delay(500)  
  
if __name__ == "__main__":  
   game = BattleshipGame()  
   game.game_loop()
