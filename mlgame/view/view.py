import abc
import math
import time
from functools import lru_cache
import pygame

KEYS = [
    pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i,
    pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r,
    pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z,
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
    pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
]

LINE = "line"
TEXT = "text"
NAME = "name"
TYPE = "type"
ANGLE = "angle"
SIZE = "size"
COLOR = "color"
IMAGE = "image"
RECTANGLE = "rect"
POLYGON = "polygon"


@lru_cache
def transfer_hex_to_rgb(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


@lru_cache
def transfer_hex_to_rgba(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))


@lru_cache
def scale_bias_of_coordinate(obj_length, scale):
    return obj_length / 2 * (1 - scale)


@lru_cache
def rotate_img(scaled_img, radian_angle):
    return pygame.transform.rotate(
        scaled_img,
        (radian_angle * 180 / math.pi) % 360
    )


@lru_cache
def scale_img(img, origin_width, origin_height, scale_ratio):
    return pygame.transform.scale(
        img, (int(origin_width * scale_ratio), int(origin_height * scale_ratio))
    )


class PygameViewInterface(abc.ABC):
    def __init__(self, game_info: dict):
        self.scene_init_data = game_info

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def draw(self, object_information):
        pass

    @abc.abstractmethod
    def get_keyboard_info(self) -> list:
        return []


class DummyPygameView(PygameViewInterface):
    def __init__(self, game_info: dict):
        super().__init__(game_info)

    def reset(self):
        pass

    def draw(self, object_information):
        pass

    def get_keyboard_info(self) -> list:
        return []


class PygameView(PygameViewInterface):
    def __init__(self, game_info: dict):
        super().__init__(game_info)
        pygame.display.init()
        pygame.font.init()

        self.width = self.scene_init_data["scene"]["width"]
        self.height = self.scene_init_data["scene"]["height"]
        self.background_color = transfer_hex_to_rgb(self.scene_init_data["scene"][COLOR])
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.address = "GameView"
        self.image_dict = self.loading_image()
        self.font = {}
        # self.map_width = game_info["map_width"]
        # self.map_height = game_info["map_height"]
        self.origin_bias_point = [self.scene_init_data["scene"]["bias_x"], self.scene_init_data["scene"]["bias_y"]]
        self.bias_point_var = [0, 0]
        self.bias_point = self.origin_bias_point.copy()

        self.scale = 1
        # if "images" in game_info.keys():
        #     self.image_dict = self.loading_image(game_info["images"])
        self._toggle_on = True
        self._toggle_last_time = 0

    def reset(self):
        self.bias_point_var = [0, 0]
        self.bias_point = self.origin_bias_point.copy()

        self.scale = 1
        self._toggle_on = True
        self._toggle_last_time = 0

    def loading_image(self):
        result = {}
        if "assets" in self.scene_init_data:
            for file in self.scene_init_data["assets"]:
                # print(file)
                if file[TYPE] == IMAGE:
                    image = pygame.image.load(file["file_path"]).convert_alpha()
                    result[file["image_id"]] = image
        return result

    def draw(self, object_information):
        '''
        每個frame呼叫一次，把角色畫在螢幕上
        :param object_information:
        :return:
        '''
        self.screen.fill(self.background_color)
        self.adjust_pygame_screen()
        if "view_center_coordinate" in object_information["game_sys_info"]:
            self.origin_bias_point = [object_information["game_sys_info"]["view_center_coordinate"][0],
                                      object_information["game_sys_info"]["view_center_coordinate"][1]]
            self.bias_point[0] = self.origin_bias_point[0] + self.bias_point_var[0]
            self.bias_point[1] = self.origin_bias_point[1] + self.bias_point_var[1]
        for game_object in object_information["background"]:
            self.draw_game_obj_according_type_with_bias(game_object, self.bias_point[0], self.bias_point[1], self.scale)
        for game_object in object_information["object_list"]:
            # let object could be shifted
            self.draw_game_obj_according_type_with_bias(game_object, self.bias_point[0], self.bias_point[1], self.scale)
        if self._toggle_on:
            for game_object in object_information["toggle_with_bias"]:
                # let object could be shifted
                self.draw_game_obj_according_type_with_bias(game_object, self.bias_point[0], self.bias_point[1],
                                                            self.scale)
            for game_object in object_information["toggle"]:
                self.draw_game_obj_according_type(game_object)
        for game_object in object_information["foreground"]:
            # object should not be shifted
            self.draw_game_obj_according_type(game_object)
        pygame.display.flip()

    def draw_game_obj_according_type(self, game_object, scale=1):
        if game_object[TYPE] == IMAGE:
            self.draw_image(game_object["image_id"], game_object["x"], game_object["y"],
                            game_object["width"], game_object["height"], game_object["angle"], scale)

        elif game_object[TYPE] == RECTANGLE:
            self.draw_rect(game_object["x"], game_object["y"], game_object["width"], game_object["height"],
                           transfer_hex_to_rgb(game_object[COLOR]), scale)

        elif game_object[TYPE] == POLYGON:
            self.draw_polygon(game_object["points"], transfer_hex_to_rgb(game_object[COLOR]), scale)

        elif game_object[TYPE] == TEXT:
            self.draw_text(game_object["content"], game_object["font-style"],
                           game_object["x"], game_object["y"], transfer_hex_to_rgb(game_object[COLOR]), scale)
        elif game_object[TYPE] == LINE:
            self.draw_line(game_object["x1"], game_object["y1"], game_object["x2"], game_object["y2"],
                           game_object["width"], game_object[COLOR], scale)
        else:
            pass

    def draw_game_obj_according_type_with_bias(self, game_object, bias_x, bias_y, scale=1):
        if game_object[TYPE] == IMAGE:
            self.draw_image(game_object["image_id"], game_object["x"] + bias_x, game_object["y"] + bias_y,
                            game_object["width"], game_object["height"], game_object["angle"], scale)

        elif game_object[TYPE] == RECTANGLE:
            self.draw_rect(game_object["x"] + bias_x, game_object["y"] + bias_y, game_object["width"],
                           game_object["height"],
                           transfer_hex_to_rgb(game_object[COLOR]), scale)

        elif game_object[TYPE] == POLYGON:
            self.draw_polygon(game_object["points"], transfer_hex_to_rgb(game_object[COLOR]), bias_x, bias_y, scale)

        elif game_object[TYPE] == TEXT:
            self.draw_text(game_object["content"], game_object["font-style"],
                           game_object["x"] + bias_x, game_object["y"] + bias_y,
                           transfer_hex_to_rgb(game_object[COLOR]),
                           scale)
        elif game_object[TYPE] == LINE:
            self.draw_line(game_object["x1"] + bias_x, game_object["y1"] + bias_y, game_object["x2"] + bias_x,
                           game_object["y2"] + bias_y,
                           game_object["width"], game_object[COLOR], scale)

        else:
            pass

        # hex # need turn to RGB

    def draw_image(self, image_id, x, y, width, height, radian_angle, scale=1):
        scaled_img = scale_img(self.image_dict[image_id], width, height, scale)
        rotated_img = rotate_img(scaled_img, radian_angle)
        # print(angle)
        rect = rotated_img.get_rect()
        rect.x = x * scale + scale_bias_of_coordinate(self.width, scale)
        rect.y = y * scale + scale_bias_of_coordinate(self.height, scale)
        self.screen.blit(rotated_img, rect)

    def draw_rect(self, x: int, y: int, width: int, height: int, color, scale=1):
        pygame.draw.rect(self.screen, color,
                         pygame.Rect(x * scale + scale_bias_of_coordinate(self.width, scale),
                                     y * scale + scale_bias_of_coordinate(self.height, scale),
                                     width * scale,
                                     height * scale))

    def draw_line(self, x1, y1, x2, y2, width, color, scale=1):
        # TODO revise
        offset_width = scale_bias_of_coordinate(self.width, scale)
        offset_height = scale_bias_of_coordinate(self.height, scale)
        pygame.draw.line(self.screen, color, (x1 * scale + offset_width, y1 * scale + offset_height),
                         (x2 * scale + offset_width, y2 * scale + offset_height), int(width * scale))
        # if scale != 1:
        #
        #     offset_width = scale_bias_of_coordinate(self.width, scale)
        #     offset_height = scale_bias_of_coordinate(self.height, scale)
        #     pygame.draw.line(self.screen, color, (x1 * scale + offset_width, y1 * scale + offset_height),
        #                      (x2 * scale + offset_width, y2 * scale + offset_height), int(width * scale))
        # else:
        #     pygame.draw.line(self.screen, color, (x1, y1), (x2 * scale, y2), int(width))

    def draw_polygon(self, points, color, bias_x=0, bias_y=0, scale=1):
        vertices = []
        for p in points:
            vertices.append(((p["x"] + bias_x) * scale + scale_bias_of_coordinate(self.width, scale),
                             (p["y"] + bias_y) * scale + scale_bias_of_coordinate(self.height, scale)))
        pygame.draw.polygon(self.screen, color, vertices)

    def draw_text(self, text, font_style, x, y, color, scale=1):
        if font_style in self.font.keys():
            font = self.font[font_style]
        else:
            font_style_list = font_style.split(" ", -1)
            size = int(font_style_list[0].replace("px", "", 1))
            font_type = font_style_list[1].lower()
            if "BOLD" in font_style_list:
                font = pygame.font.Font(pygame.font.match_font(font_type, bold=True), size * scale)
            else:
                font = pygame.font.Font(pygame.font.match_font(font_type), size * scale)
            self.font[font_style] = font
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.x, text_rect.y = (x * scale + scale_bias_of_coordinate(self.width, scale),
                                    y * scale + scale_bias_of_coordinate(self.height, scale))
        self.screen.blit(text_surface, text_rect)

    def adjust_pygame_screen(self):
        """
        zoom in zoom out and shift the window.
        """
        key_state = pygame.key.get_pressed()
        # 上下左右 放大縮小
        if key_state[pygame.K_i]:
            self.bias_point_var[1] += 10
            self.bias_point[1] = self.origin_bias_point[1] + self.bias_point_var[1]
        elif key_state[pygame.K_k]:
            self.bias_point_var[1] -= 10
            self.bias_point[1] = self.origin_bias_point[1] + self.bias_point_var[1]
        elif key_state[pygame.K_j]:
            self.bias_point_var[0] += 10
            self.bias_point[0] = self.origin_bias_point[0] + self.bias_point_var[0]
        elif key_state[pygame.K_l]:
            self.bias_point_var[0] -= 10
            self.bias_point[0] = self.origin_bias_point[0] + self.bias_point_var[0]

        if key_state[pygame.K_o]:
            self.scale += 0.01
        elif key_state[pygame.K_u]:
            self.scale -= 0.01
            if self.scale < 0.05:
                self.scale = 0.05
        # 隱藏鍵
        if key_state[pygame.K_h] and (time.time() - self._toggle_last_time) > 0.3:
            self._toggle_on = not self._toggle_on
            self._toggle_last_time = time.time()

    def get_keyboard_info(self) -> list:
        keyboard_info = []
        pressed_keys = pygame.key.get_pressed()
        if True in pressed_keys:
            for k in KEYS:
                if pressed_keys[k]:
                    keyboard_info.append(k)
        return keyboard_info
