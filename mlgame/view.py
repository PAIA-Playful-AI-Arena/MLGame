import math

from os import path
import pygame

NAME = "name"
TYPE = "type"
ANGLE = "angle"
SIZE = "size"
COLOR = "color"
IMAGE = "image"
RECTANGLE = "rect"
POLYGON = "polygon"


def trnsfer_hex_to_rgb(hex):
    h = hex.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class PygameView():
    def __init__(self, game_info: dict):
        pygame.display.init()
        pygame.font.init()
        self.scene_init_data = game_info
        self.width = self.scene_init_data["scene"]["width"]
        self.height = self.scene_init_data["scene"]["height"]
        self.background_color = trnsfer_hex_to_rgb(self.scene_init_data["scene"][COLOR])
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.address = "GameView"
        self.image_dict = self.loading_image()
        self.font = {}
        # self.map_width = game_info["map_width"]
        # self.map_height = game_info["map_height"]
        self.pygame_point = [0, 0]
        # if "images" in game_info.keys():
        #     self.image_dict = self.loading_image(game_info["images"])
        self._toggle_on = True
        self._toggle_last_time = 0

    def loading_image(self):
        result = {}
        if "assets" in self.scene_init_data:
            for file in self.scene_init_data["assets"]:
                print(file)
                if file[TYPE] == IMAGE:
                    image = pygame.image.load(file["file_path"])
                    result[file["image_id"]] = image
        return result

    def draw(self, object_information):
        '''
        每個frame呼叫一次，把角色畫在螢幕上
        :param object_information:
        :return:
        '''
        self.draw_screen()
        self.limit_pygame_screen()
        for game_object in object_information["background"]:
            if game_object[TYPE] == IMAGE:
                self.draw_image(game_object["image_id"], game_object["x"] - self.pygame_point[0],
                                game_object["y"] - self.pygame_point[1],
                                game_object["width"], game_object["height"], game_object["angle"])

            elif game_object[TYPE] == RECTANGLE:
                self.draw_rect(game_object["x"] - self.pygame_point[0], game_object["y"] - self.pygame_point[1],
                               game_object["width"], game_object["height"],
                               trnsfer_hex_to_rgb(game_object[COLOR]))

            elif game_object[TYPE] == "text":
                self.draw_text(game_object["content"], game_object["font-style"],
                               game_object["x"] - self.pygame_point[0], game_object["y"] - self.pygame_point[1],
                               trnsfer_hex_to_rgb(game_object[COLOR]))
            else:
                pass
        for game_object in object_information["object_list"]:
            # let object could be shifted
            self.draw_game_obj_according_type(game_object)
        if self._toggle_on:
            # TODO object should not be shifted
            for game_object in object_information["toggle"]:
                self.draw_game_obj_according_type(game_object)
        for game_object in object_information["foreground"]:
            # object should not be shifted
            self.draw_game_obj_according_type(game_object)

    def draw_game_obj_according_type(self, game_object):
        if game_object[TYPE] == IMAGE:
            self.draw_image(game_object["image_id"], game_object["x"], game_object["y"],
                            game_object["width"], game_object["height"], game_object["angle"])

        elif game_object[TYPE] == RECTANGLE:
            self.draw_rect(game_object["x"], game_object["y"], game_object["width"], game_object["height"],
                           trnsfer_hex_to_rgb(game_object[COLOR]))

        elif game_object[TYPE] == POLYGON:
            self.draw_polygon(game_object["points"], trnsfer_hex_to_rgb(game_object[COLOR]))

        elif game_object[TYPE] == "text":
            self.draw_text(game_object["content"], game_object["font-style"],
                           game_object["x"], game_object["y"], trnsfer_hex_to_rgb(game_object[COLOR]))
        elif game_object[TYPE] == "line":
            self.draw_line(game_object["x1"], game_object["y1"], game_object["x2"], game_object["y2"],
                           game_object["width"], game_object[COLOR])

        else:
            pass

    def draw_screen(self):
        self.screen.fill(self.background_color)  # hex # need turn to RGB

    def draw_image(self, image_id, x, y, width, height, angle):
        image = pygame.transform.rotate(pygame.transform.scale(self.image_dict[image_id], (width, height)),
                                        (angle * 180 / math.pi) % 360)
        rect = image.get_rect()
        rect.x, rect.y = x + self.pygame_point[0], y + self.pygame_point[1]
        self.screen.blit(image, rect)

    def draw_rect(self, x, y, width, height, color):
        pygame.draw.rect(self.screen, color,
                         pygame.Rect(x + self.pygame_point[0], y + self.pygame_point[1], width, height))

    def draw_line(self, x1, y1, x2, y2, width, color):
        pygame.draw.line(self.screen, color, (x1 + self.pygame_point[0], y1 + self.pygame_point[1]),
                         (x2 + self.pygame_point[0], y2 + self.pygame_point[1]), width)

    def draw_polygon(self, points, color):
        vertices = []
        for p in points:
            vertices.append((p["x"] + self.pygame_point[0], p["y"] + self.pygame_point[1]))
        pygame.draw.polygon(self.screen, color, vertices)

    def flip(self):
        pygame.display.flip()

    def draw_text(self, text, font_style, x, y, color):
        if font_style in self.font.keys():
            font = self.font[font_style]
        else:
            list = font_style.split(" ", -1)
            size = int(list[0].replace("px", "", 1))
            font_type = list[1].lower()
            font = pygame.font.Font(pygame.font.match_font(font_type), size)
            print(font)
            self.font[font_style] = font
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.x, text_rect.y = (x + self.pygame_point[0], y + self.pygame_point[1])
        self.screen.blit(text_surface, text_rect)

    def limit_pygame_screen(self):

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_w]:
            self.pygame_point[1] += 10
        elif keystate[pygame.K_s]:
            self.pygame_point[1] -= 10
        elif keystate[pygame.K_a]:
            self.pygame_point[0] += 10
        elif keystate[pygame.K_d]:
            self.pygame_point[0] -= 10

        mods = pygame.key.get_mods()
        if keystate[pygame.K_h] and (pygame.time.get_ticks() - self._toggle_last_time) > 300:
            self._toggle_on = not self._toggle_on
            self._toggle_last_time = pygame.time.get_ticks()

        # if self.pygame_point[1] < 480 - self.map_height:
        #     self.pygame_point[1] = 480 - self.map_height
        # elif self.pygame_point[1] > 0:
        #     self.pygame_point[1] = 0
        # else:
        #     pass
        # if self.pygame_point[0] < 500 - self.map_width:
        #     self.pygame_point[0] = 500 - self.map_width
        # elif self.pygame_point[0] > 0:
        #     self.pygame_point[0] = 0
        # else:
        #     pass
