# PyGameView

此物件使用Pygame技術繪製畫面，也自定義數種資料結構，用來繪製圖樣。
## 座標系統
延用pygame座標系統，視窗的左上角為(0,0)，X軸往右為正，Y軸往下為正。

[//]: # (TODO 座標軸範例圖片)

## 初始化素材之資料結構

### Scene

### Image
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
  - 此資料用來渲染從(x1,y1)到(x2,y2)的直線，此資料可用函式`create_line_view_data()`產生
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

### Polygon

### Image

### Text

## 特殊功能

### 平移、縮放、隱藏

[//]: # (function name and data structure)
