#python -m mlgame \
#-i ./games/maze_car/ml/ml_play_template.py \
#-i ./games/maze_car/ml/ml_play_template.py \
#-i ./games/maze_car/ml/ml_play_template.py \
#-i ./games/maze_car/ml/ml_play_template.py \
#-i ./games/maze_car/ml/ml_play_template.py \
#-i ./games/maze_car/ml/ml_play_template.py \
#--nd \
#-o "./outputs" \
#-f 60 -1 \
#./games/maze_car/ --game_type=MAZE --sound=off --time_to_play=450
#--ws="wss://demo.piesocket.com/v3/arkanoid?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV" \
#python -m mlgame \
#-i ./ai_clients/Maze_Car/model_1013/ml_play.py \
#-f 60 -1 \
#--ws="wss://demo.piesocket.com/v3/paia?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV" \
#./games/Maze_Car/ --game_type=MAZE --sound=off --time_to_play=450

python -m mlgame \
-1 -f 60   \
-i ./ai_clients/Maze_Car/model_3p/ml_play.py \
-i ./ai_clients/Maze_Car/model_3p/ml_play.py \
-i ./ai_clients/Maze_Car/model_3p/ml_play.py \
-i ./ai_clients/Maze_Car/model_3p/ml_play.py \
./games/maze_car --map 8
#--game_type PRACTICE

