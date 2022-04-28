from enum import Enum ,auto
import pygame

KEYS = [
    pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i,
    pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r,
    pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z,
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
    pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
]


class StringEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __eq__(self, other):
        if isinstance(other, StringEnum):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)
