import pygame
import sys
import random
import time
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (34, 139, 34)
GRAY = (40, 40, 40)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
TEAL = (0, 128, 128)

# Fonts
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Modern Snake Game")
clock = pygame.time.Clock()

# Load sounds
try:
    eat_sound = mixer.Sound("eat.wav")
    crash_sound = mixer.Sound("crash.wav")
except:
    # If sounds are not available, create dummy sound objects
    class DummySound:
        def play(self):
            pass
    eat_sound = DummySound()
    crash_sound = DummySound()

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.length = 3
        self.positions = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = random.choice([
            (0, -GRID_SIZE),  # Up
            (0, GRID_SIZE),   # Down
            (-GRID_SIZE, 0),  # Left
            (GRID_SIZE, 0)    # Right
        ])
        self.color = GREEN
        self.head_color = DARK_GREEN
        self.score = 0
        self.grow_pending = 2  # Start with length 3
        self.alive = True
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        if not self.alive:
            return
            
        head = self.get_head_position()
        x, y = self.direction
        new_x = (head[0] + x) % WIDTH
        new_y = (head[1] + y) % HEIGHT
        new_position = (new_x, new_y)
        
        # Check for self collision
        if new_position in self.positions[1:]:
            self.alive = False
            crash_sound.play()
            return
            
        # Update positions
        self.positions.insert(0, new_position)
        
        # Handle growth
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()
    
    def render(self, surface):
        # Draw body segments
        for i, p in enumerate(self.positions):
            if i == 0:
                # Draw head
                pygame.draw.rect(surface, self.head_color, 
                                 (p[0], p[1], GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, DARK_GREEN, 
                                 (p[0], p[1], GRID_SIZE, GRID_SIZE), 1)
                
                # Draw eyes
                direction = self.direction
                eye_size = GRID_SIZE // 5
                eye_offset = GRID_SIZE // 3
                
                # Determine eye positions based on direction
                if direction == (0, -GRID_SIZE):  # Up
                    left_eye = (p[0] + eye_offset, p[1] + eye_offset)
                    right_eye = (p[0] + GRID_SIZE - eye_offset - eye_size, p[1] + eye_offset)
                elif direction == (0, GRID_SIZE):  # Down
                    left_eye = (p[0] + eye_offset, p[1] + GRID_SIZE - eye_offset - eye_size)
                    right_eye = (p[0] + GRID_SIZE - eye_offset - eye_size, p[1] + GRID_SIZE - eye_offset - eye_size)
                elif direction == (-GRID_SIZE, 0):  # Left
                    left_eye = (p[0] + eye_offset, p[1] + eye_offset)
                    right_eye = (p[0] + eye_offset, p[1] + GRID_SIZE - eye_offset - eye_size)
                else:  # Right
                    left_eye = (p[0] + GRID_SIZE - eye_offset - eye_size, p[1] + eye_offset)
                    right_eye = (p[0] + GRID_SIZE - eye_offset - eye_size, p[1] + GRID_SIZE - eye_offset - eye_size)
                
                pygame.draw.rect(surface, WHITE, (*left_eye, eye_size, eye_size))
                pygame.draw.rect(surface, WHITE, (*right_eye, eye_size, eye_size))
            else:
                # Make the snake body segmented with alternate colors for visual appeal
                segment_color = DARK_GREEN if i % 2 == 0 else GREEN
                pygame.draw.rect(surface, segment_color, 
                                 (p[0], p[1], GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, DARK_GREEN, 
                                 (p[0], p[1], GRID_SIZE, GRID_SIZE), 1)
    
    def turn(self, point):
        # Prevent turning directly back on yourself
        if (point[0] * -1, point[1] * -1) == self.direction:
            return
        self.direction = point
    
    def grow(self):
        self.grow_pending += 1
        self.score += 10
        eat_sound.play()
        
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
        
    def randomize_position(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )
        
    def render(self, surface):
        # Draw a more appealing food item
        x, y = self.position
        center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
        radius = GRID_SIZE // 2
        
        # Draw the apple shape
        pygame.draw.circle(surface, RED, center, radius)
        
        # Add a small green stem
        stem_rect = (x + GRID_SIZE // 2 - 1, y, 2, GRID_SIZE // 4)
        pygame.draw.rect(surface, DARK_GREEN, stem_rect)
        
        # Add a highlight to make it look 3D
        highlight_radius = radius // 2
        highlight_pos = (center[0] - radius // 3, center[1] - radius // 3)
        pygame.draw.circle(surface, (255, 150, 150), highlight_pos, highlight_radius // 2)

def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, GRAY, rect, 1)

def draw_background(surface):
    # Draw a nice dark background with subtle pattern
    surface.fill(BLACK)
    
    # Draw subtle grid pattern
    for y in range(0, HEIGHT, GRID_SIZE * 2):
        for x in range(0, WIDTH, GRID_SIZE * 2):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, (20, 20, 20), rect)

def draw_score(surface, score, high_score):
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    high_score_text = font_medium.render(f"High Score: {high_score}", True, WHITE)
    surface.blit(score_text, (10, 10))
    surface.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

def draw_game_over(surface, score, high_score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black overlay
    surface.blit(overlay, (0, 0))
    
    # Game Over text
    game_over_text = font_large.render("GAME OVER", True, WHITE)
    surface.blit(game_over_text, 
                (WIDTH // 2 - game_over_text.get_width() // 2, 
                 HEIGHT // 2 - game_over_text.get_height() // 2 - 50))
    
    # Score text
    final_score_text = font_medium.render(f"Your Score: {score}", True, WHITE)
    surface.blit(final_score_text, 
                (WIDTH // 2 - final_score_text.get_width() // 2, 
                 HEIGHT // 2 - final_score_text.get_height() // 2 + 20))
    
    # High score text
    high_score_text = font_medium.render(f"High Score: {high_score}", True, WHITE)
    surface.blit(high_score_text, 
                (WIDTH // 2 - high_score_text.get_width() // 2, 
                 HEIGHT // 2 - high_score_text.get_height() // 2 + 60))
    
    # Retry instructions
    retry_text = font_small.render("Press SPACE to play again or ESC to quit", True, WHITE)
    surface.blit(retry_text, 
                (WIDTH // 2 - retry_text.get_width() // 2, 
                 HEIGHT // 2 - retry_text.get_height() // 2 + 120))

def draw_start_screen(surface):
    # Fill with black background
    surface.fill(BLACK)
    
    # Draw a snake-like pattern in the background
    for i in range(0, WIDTH + HEIGHT, GRID_SIZE * 2):
        points = []
        for j in range(-HEIGHT, WIDTH, GRID_SIZE):
            points.append((j, i - j))
        
        if points:
            pygame.draw.lines(surface, DARK_GREEN, False, points, 3)
    
    # Title
    title_text = font_large.render("SNAKE GAME", True, GREEN)
    surface.blit(title_text, 
                (WIDTH // 2 - title_text.get_width() // 2, 
                 HEIGHT // 3 - title_text.get_height() // 2))
    
    # Instructions
    instructions = [
        "Use ARROW KEYS to control the snake",
        "Eat the red apples to grow",
        "Avoid hitting yourself",
        "Press SPACE to start",
        "Press ESC to quit"
    ]
    
    y_offset = HEIGHT // 2
    for instruction in instructions:
        instruction_text = font_small.render(instruction, True, WHITE)
        surface.blit(instruction_text, 
                    (WIDTH // 2 - instruction_text.get_width() // 2, 
                     y_offset))
        y_offset += 30

def main():
    snake = Snake()
    food = Food()
    high_score = 0
    game_state = "START"  # START, PLAYING, GAME_OVER
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif game_state == "START" and event.key == pygame.K_SPACE:
                    game_state = "PLAYING"
                    snake.reset()
                    food.randomize_position()
                elif game_state == "GAME_OVER" and event.key == pygame.K_SPACE:
                    game_state = "PLAYING"
                    snake.reset()
                    food.randomize_position()
                elif game_state == "PLAYING":
                    if event.key == pygame.K_UP:
                        snake.turn((0, -GRID_SIZE))
                    elif event.key == pygame.K_DOWN:
                        snake.turn((0, GRID_SIZE))
                    elif event.key == pygame.K_LEFT:
                        snake.turn((-GRID_SIZE, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.turn((GRID_SIZE, 0))
        
        if game_state == "START":
            draw_start_screen(screen)
        elif game_state == "PLAYING":
            # Update snake
            snake.update()
            
            # Check if snake is still alive
            if not snake.alive:
                game_state = "GAME_OVER"
                if snake.score > high_score:
                    high_score = snake.score
                continue
            
            # Check if snake ate food
            if snake.get_head_position() == food.position:
                snake.grow()
                food.randomize_position()
                # Make sure food doesn't appear on snake
                while food.position in snake.positions:
                    food.randomize_position()
            
            # Draw game
            draw_background(screen)
            draw_grid(screen)
            snake.render(screen)
            food.render(screen)
            draw_score(screen, snake.score, high_score)
        elif game_state == "GAME_OVER":
            # Keep drawing the game state but overlay game over screen
            draw_background(screen)
            draw_grid(screen)
            snake.render(screen)
            food.render(screen)
            draw_score(screen, snake.score, high_score)
            draw_game_over(screen, snake.score, high_score)
        
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()