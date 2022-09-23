# PyGameView

此物件使用Pygame技術繪製畫面，也自定義數種資料結構，用來繪製圖樣。
## 座標系統
延用pygame座標系統，視窗的左上角為(0,0)，X軸往右為正，Y軸往下為正。

[//]: # (TODO 座標軸範例圖片)

## 初始化素材之資料結構
- 繼承 `PaiaGame` 後覆寫 `get_scene_init_data` 內的資料

### Scene
1. 使用 `mlgame.view.view_model` 內的 `create_scene_view_data` 函式，建立場景初始化資料
    ```python
    def create_scene_view_data(width: int, height: int, color: str = "#000000", bias_x=0, bias_y=0):
        return {
            "width": width,
            "height": height,
            "color": color,
            "bias_x": bias_x,
            "bias_y": bias_y
        }
    ```
2. 建立 `mlgame.view.view_model` 內的 `Scene` 類別，再透過 `self.scene.__dict__` 將類別屬性化為字典，建立場景初始化資料
    ```python
    class Scene:
        def __init__(self, width: int, height: int, color: str = "#000000", bias_x=0, bias_y=0):
            """
            This is a value object
            :param width:
            :param height:
            :param color:
            """
            self.width = width
            self.height = height
            self.color = color
            self.bias_x = bias_x
            self.bias_y = bias_y
    ```
### Image
使用 `mlgame.view.view_model` 內的 `create_asset_init_data` 函式，建立圖片初始化資料
```python
def create_asset_init_data(image_id: str, width: int, height: int, file_path: str, github_raw_url: str):
    # assert file_path is valid
    return {
        "type": "image",
        "image_id": image_id,
        "width": width,
        "height": height,
        "file_path": file_path,
        "url": github_raw_url
    }
```


## 繪製畫面之資料結構
繪製畫面過程，依照物件種類與各自帶的座標、長寬、顏色來繪製圖樣。

### Line
- 資料範例
  - 此資料用來渲染從`(x1,y1)`到`(x2,y2)`的直線，此資料可用函式`create_line_view_data()`產生
      ```json
      {
        "type": "line",
        "name": "border_of_brick",
        "x1": 100,
        "y1": 150,
        "x2": 200,
        "y2": 250,
        "width": 3,
        "color": "#FFFAAA"
      }
      ```

### Rect
- 資料範例
  - 此資料用來渲染從`(x,y)`到寬`width`長`height`的實心矩形，此資料可用函式`create_rect_view_data()`產生
      ```json
      {
        "type": "rect",
        "name": "wall",
        "x": 0,
        "y": 0,
        "angle": 0,
        "width": 50,
        "height": 50,
        "color": "#ffffff"
      }
      ```
    
### Polygon
- 資料範例
  - 此資料用來渲染從`points[0]` 到`points[1]` 到`points[2]` 的實心多邊形，此資料可用函式`create_polygon_view_data()`產生
      ```json
      {
        "type": "polygon",
        "name": "window",
        "color": "#ff0000",
        "points": [{"x": 500, "y": 300}, {"x": 600, "y": 300}, {"x": 600, "y": 400}]
      }
      ```
    
### Image
- 資料範例
  - 此資料用來在座標 `(x, y)` 渲染 `image_id` 為 `1P`，設大小為 `（width, height）` 的圖片，此資料可用函式`create_image_view_data()`產生
      ```json
      {
        "type": "image",
        "x": 200,
        "y": 200,
        "width": 50,
        "height": 50,
        "image_id": "1P",
        "angle": 0
      }
      ```
    
### Text
- 資料範例
  - 此資料用來在座標 `(x, y)` 渲染 `image_id` 為 `1P`，設大小為 `（width, height）` 的圖片，此資料可用函式`create_text_view_data()`產生
      ```json
      {
        "type": "text",
        "content": "score",
        "color": "#FFA500",
        "x": 500,
        "y": 0,
        "font-style": "30px Arial BOLD"
      }
      ```
    
## 特殊功能

### 平移、縮放、隱藏

[//]: # (function name and data structure)
