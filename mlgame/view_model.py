import random


class Scene():
    def __init__(self, width: int, height: int, color: str = "#000000"):
        """
        This is a value object
        :param width:
        :param height:
        :param color:
        :param image:
        """
        self.width = width
        self.height = height
        self.color = color


def create_asset_init_data(asset_file_name: str, width: int, height: int, github_raw_url: str):
    return {
        "type": "image",
        "image_id": asset_file_name,
        "width": width,
        "height": height,
        "url": github_raw_url
    }


def create_scene_view_data(width: int, height: int, color: str = "#000000"):
    return {
        "width": width,
        "height": height,
        "color": color
    }


def create_image_view_data(image_id, x, y, width, height, angle=0):
    """
    這是一個用來繪製圖片的資料格式，
    "type"表示不同的類型
    "x" "y" 表示物體左上角的座標
    "width" "height"表示其大小
    "image_id"表示其圖片的識別號，需在
    "angle"表示其順時針旋轉的角度
    """
    return {"type": "image",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "image_id": image_id,
            "angle": angle}


def create_rect_view_data(name: str, x: int, y: int, width: int, height: int, color: str, angle: int = 0):
    """
    這是一個用來繪製矩形的資料格式，
    "type"表示不同的類型
    "name"用來描述這個物件
    "x""y"表示其位置，位置表示物體左上角的座標
    "size"表示其大小
    "image"表示其圖片
    "angle"表示其順時針旋轉的角度
    "color"以字串表示
    :return:
    """
    return {"type": "rect",
            "name": name,
            "x": x,
            "y": y,
            "angle": angle,
            "width": width,
            "height": height,
            "color": color
            }


def create_line_view_model(name: str, x1: int, y1: int, x2: int, y2: int, color: str, width: int = 2):
    """
    這是一個用來繪製矩形的資料格式，
    "type"表示不同的類型
    "x""y"表示其位置，位置表示物體左上角的座標
    "size"表示其大小
    "image"表示其圖片
    "angle"表示其順時針旋轉的角度
    "color"以字串表示
    :return:
    """
    return {"type": "line",
            "name": name,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "width": width,
            "color": color
            }


def create_polygon_view_model(name: str, points: list, color: str):
    """
    這是一個用來繪製多邊形的資料格式，
    points欄位至少三個 # [{"x":1,"y":2},{},{}]
    :return:dict
    """
    # TODO 檢查points 數量
    vertices = []
    for p in points:
        vertices.append({"x": p[0], "y": p[1]})
    return {"type": "polygon",
            "name": name,
            "color": color,
            "points": vertices
            }


def create_text_view_model(content: str, x: int, y: int, color: str, font_style="24px Arial"):
    return {
        "type": "text",
        "content": content,
        "color": color,
        "x": x,
        "y": y,
        "font-style": font_style
    }
