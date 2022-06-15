import random

import pygame.sprite


class Ball(pygame.sprite.Sprite):
    def __init__(self, color="#FFEB3B"):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([50, 50])
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)

    def update(self, motion):
        # for motion in motions:
        if motion == "UP":
            self.rect.centery -= 10.5
        elif motion == "DOWN":
            self.rect.centery += 10.5
        elif motion == "LEFT":
            self.rect.centerx -= 10.5
        elif motion == "RIGHT":
            self.rect.centerx += 10.5

    @property
    def game_object_data(self):
        return {"type": "rect",
                "name": "ball",
                "x": self.rect.x,
                "y": self.rect.y,
                "angle": 0,
                "width": self.rect.width,
                "height": self.rect.height,
                "color": self.color
                }


class Food(pygame.sprite.Sprite):
    def __init__(self, group):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = pygame.Surface([8, 8])
        self.color = "#E91E63"
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(0, 800)
        self.rect.centery = random.randint(0, 600)
        self.angle = 0

    def update(self) -> None:
        self.angle += 10
        if self.angle > 360:
            self.angle -= 360

    @property
    def game_object_data(self):
        return {"type": "rect",
                "name": "ball",
                "x": self.rect.x,
                "y": self.rect.y,
                "angle": 0,
                "width": self.rect.width,
                "height": self.rect.height,
                "color": self.color
                }
