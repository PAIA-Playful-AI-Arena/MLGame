import re
from functools import wraps

from mlgame.game.paia_game import GameResultState

K_ATTACHMENT = "attachment"
K_STATE = "state"
K_ASSET = "assets"

OBJ_TYPE_TXT = "text"
OBJ_TYPE_IMG = "image"
OBJ_TYPE_RECT = "rect"
OBJ_TYPE_POLY = "polygon"
OBJ_TYPE_LINE = "line"

K_FRAME_USED = "frame_used"
K_URL = "url"
K_IMG_ID = "image_id"
K_IMG = "images"
K_TEMPLATE = "template"
K_Game_Objs = "object_list"
K_SCENE = "scene"
K_SIZE = "size"
K_ANGLE = "angle"
K_COLOR = "color"
K_CORD = "coordinate"
K_NAME = 'name'
K_TYPE = 'type'
K_X = 'x'
K_Y = 'y'
K_WID = 'width'
K_HEIGHT = 'height'
K_POINT = 'points'
K_POLY = 'polys'
K_STYLE = 'style'


def assert_polygon_obj(polygon):
    assert_contains_keys(polygon, keys=[K_TYPE, K_NAME, K_POINT, K_COLOR])
    assert type(polygon[K_POINT]) == list
    assert len(polygon[K_POINT]) >= 3
    assert type(polygon[K_POINT][0]) == dict
    assert_contains_keys(polygon[K_POINT][0], [K_X, K_Y])
    # validate the color string
    assert_color_rgba_hex_string(polygon[K_COLOR])


def assert_rect_obj(rect):
    assert isinstance(rect[K_X], (int, float))
    assert isinstance(rect[K_Y], (int, float))
    assert isinstance(rect[K_WID], (int, float))
    assert isinstance(rect[K_HEIGHT], (int, float))

    # validate the color string
    assert_color_rgba_hex_string(rect[K_COLOR])


def assert_image_obj(img):
    assert_contains_keys(img, keys=[K_TYPE, K_X, K_Y, K_WID, K_HEIGHT, K_ANGLE, K_IMG_ID])
    assert isinstance(img[K_X], (int, float))
    assert isinstance(img[K_Y], (int, float))
    assert isinstance(img[K_WID], (int, float))
    assert isinstance(img[K_HEIGHT], (int, float))
    assert isinstance(img[K_ANGLE], (int, float))


def assert_line_obj(line):
    assert_contains_keys(line, keys=[K_TYPE, "x1", "y1", "x2", "y2", K_WID, K_COLOR])
    assert isinstance(line["x1"], (int, float))
    assert isinstance(line["y1"], (int, float))
    assert isinstance(line["x2"], (int, float))
    assert isinstance(line["y2"], (int, float))
    assert isinstance(line[K_WID], (int, float))
    assert_color_rgba_hex_string(line[K_COLOR])


def assert_scene_init_data(data: dict = None):
    """  驗證遊戲場景初始化的資料
    :return:None
    """
    assert type(data) == dict
    assert_contains_keys(data, [K_SCENE, K_ASSET])

    scene_obj = data[K_SCENE]
    assert type(scene_obj) == dict
    assert_contains_keys(scene_obj, [K_WID, K_HEIGHT, K_COLOR])

    images = data[K_ASSET]
    assert type(images) == list
    assert_contains_keys(images[0], [K_IMG_ID, K_URL, K_WID, K_HEIGHT])


def assert_contains_keys(obj: dict, keys: list):
    for k in keys:
        assert k in obj, str(obj.__class__) + " should contains " + str(keys)
    pass


def assert_color_rgba_hex_string(color_str: str = ""):
    assert re.match(r'^#(\d|[A-F]|[a-f]){6,8}$', color_str), "color should be in hex format ex #DDEEFF00"


def assert_text_obj(text_obj: dict):
    assert_contains_keys(text_obj, keys=["content", K_COLOR, K_X, K_Y, "font-style"])
    assert isinstance(text_obj[K_X], (int, float))
    assert isinstance(text_obj[K_Y], (int, float))
    assert type(text_obj["font-style"]) == str
    assert_color_rgba_hex_string(text_obj[K_COLOR])


def assert_game_progress_data(data: dict = None):
    """
    驗證遊戲過程的更新資料
    :param data:
    :return:
    """

    assert type(data) == dict
    assert_contains_keys(data,
                         ["frame", "background", "object_list", "toggle", "foreground", "user_info", "game_sys_info"])
    assert type(data[K_Game_Objs]) == list
    total_objs = []
    total_objs.extend(data[K_Game_Objs])
    total_objs.extend(data["background"])
    total_objs.extend(data["toggle"])
    total_objs.extend(data["foreground"])
    for obj in total_objs:
        if obj[K_TYPE] == OBJ_TYPE_POLY:
            assert_polygon_obj(obj)
        elif obj[K_TYPE] == OBJ_TYPE_IMG:
            assert_image_obj(obj)
        elif obj[K_TYPE] == OBJ_TYPE_RECT:
            assert_rect_obj(obj)
        elif obj[K_TYPE] == OBJ_TYPE_TXT:
            assert_text_obj(obj)
        elif obj[K_TYPE] == OBJ_TYPE_LINE:
            assert_line_obj(obj)
        pass


def assert_game_result_data(data: dict = None):
    """
        驗證遊戲過程的更新資料
        :param data:
        :return:
        """
    # data = get_dummy_progress_data()
    assert type(data) == dict
    assert_contains_keys(data, [K_FRAME_USED, K_STATE, K_ATTACHMENT])
    assert data[K_STATE] in GameResultState.__dict__.values()

    assert isinstance(data[K_ATTACHMENT], list)


def check_game_result(func):
    """
    這是用來檢驗 遊戲結果 的裝飾子，可以在開發期間使用，在正式執行環境再拿掉
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        assert_game_result_data(result)
        return result

    return wrapper


def check_scene_init_data(func):
    """
    這是用來檢驗 遊戲初始化資料 的裝飾子，可以在開發期間使用，在正式執行環境再拿掉
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        assert_scene_init_data(result)
        return result

    return wrapper


def check_game_progress(func):
    """
    這是用來檢驗 遊戲過程資料 的裝飾子，可以在開發期間使用，在正式執行環境再拿掉
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        assert_game_progress_data(result)
        return result

    return wrapper
