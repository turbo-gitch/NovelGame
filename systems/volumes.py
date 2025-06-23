import pygame

class VolumeManager:
    def __init__(self):
        self.volume = 0

    def increase_volume(self):
        self.volume = min(1.0, self.volume + 0.1)
        pygame.mixer.music.set_volume(self.volume)

    def decrease_volume(self):
        self.volume = max(0.0, self.volume - 0.1)
        pygame.mixer.music.set_volume(self.volume)