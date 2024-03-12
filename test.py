import pygame
import sys
from core.Sprite import Sprite
from core.Medias import Audio
import ffmpeg

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Pygame Window")

test = Sprite(
    filepath='./toy/media/sprite/季云动态轮廓.png',
    eyepath='./toy/media/sprite/季云动态眼*.png',
    mouthpath='./toy/media/sprite/季云动态嘴*.png',
    pos=(300,300),
    blink_mean=3,
    blink_std=1,
    tick=3
)
audio = Audio('./toy/media/sprite/test1.wav')
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Clock for controlling the frame rate
clock = pygame.time.Clock()
FPS = 30

display_tick = test.get_tick(duration=500,audio=audio,delay=0,framerate=FPS)

output_engine = (
    ffmpeg
    .input(
        'pipe:',
        format  = 'rawvideo',
        r       = 30,
        pix_fmt = 'rgb24',
        s       = '{0}x{1}'.format(1920,1080)
        ) # 视频来源
    .output(
        ffmpeg.input('./toy/media/sprite/test1.wav').audio,
        './toy/media/sprite/test_out.mp4',
        pix_fmt = 'yuv420p',
        r       = 30,
        crf     = 24,
        loglevel= 'quiet',
        ) # 输出
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

channel = pygame.mixer.Channel(1)
# Main loop
running = True
for i,tick in enumerate(display_tick):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # Fill the screen with white color
    screen.fill(WHITE)
    # Draw something on the screen
    test.display(surface=screen,frame=tick)
    # Update the display
    pygame.display.update()
    obyte = pygame.image.tostring(screen,'RGB')
    output_engine.stdin.write(obyte)
    # Cap the frame rate
    clock.tick(FPS)

output_engine.stdin.close()

# Quit Pygame
pygame.quit()
sys.exit()