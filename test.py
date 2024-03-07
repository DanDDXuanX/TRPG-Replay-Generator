import pygame
import sys
from core.Sprite import Sprite
from core.Medias import Audio

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Pygame Window")

test = Sprite(
    filepath='./toy/media/sprite/F.png',
    eyepath='./toy/media/sprite/E*.png',
    mouthpath='./toy/media/sprite/M*.png',
    pos=(300,300),
    blink_mean=3,
    blink_std=0.7,
    tick=2
)
audio = Audio('./test_output/测试音频.wav')
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Clock for controlling the frame rate
clock = pygame.time.Clock()
FPS = 30

display_tick = test.get_tick(duration=300,audio=audio,delay=20,framerate=FPS)

channel = pygame.mixer.Channel(1)
# Main loop
running = True
for i,tick in enumerate(display_tick):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if i == 20:
        audio.display(channel=channel,volume=100)
    # Fill the screen with white color
    screen.fill(WHITE)

    # Draw something on the screen
    test.display(surface=screen,frame=tick)

    # Update the display
    pygame.display.update()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()