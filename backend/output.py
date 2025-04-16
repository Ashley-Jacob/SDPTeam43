import pygame
import random
import time

pygame.init()

airhorn = pygame.mixer.Sound('C:/Users/rubas/OneDrive/Documents/Random/airhorn.mp3')
potsnpans = pygame.mixer.Sound('C:/Users/rubas/OneDrive/Documents/Random/potsnpans.mp3')
laser = pygame.mixer.Sound('C:/Users/rubas/OneDrive/Documents/Random/laser.mp3')

sounds = [airhorn, potsnpans, laser]

def output(lock, detection):
    while True:
        with lock:
            if not detection:
                wait()
            try:
                print("Sound Played")
                sound = random.choice(sounds)
                sound.play()

                time.sleep(random.uniform(.2, 1.2))
            except KeyboardInterrupt:
                break

    print("exited")


