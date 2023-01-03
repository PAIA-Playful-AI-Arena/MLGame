#python -m mlgame \
#-f 50 -i ./ai_clients/pingpong/start/ml_play.py -i ./ai_clients/pingpong/start/ml_play.py \
#./games/pingpong \
#--difficulty NORMAL --game_over_score 3

#python -m mlgame \
#-f 50 -i ./ai_clients/pingpong/rule/ml_play.py -i ./ai_clients/pingpong/rule/ml_play.py \
#--ws "wss://demo.piesocket.com/v3/paia?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV" \
#./games/pingpong \
#--difficulty NORMAL --game_over_score 3

#python -m mlgame \
#-f 120 -i ./ai_clients/pingpong/error_at_1p_50f/ml_play.py -i ./ai_clients/pingpong/error_at_2p_import/ml_play.py \
#--ws "wss://demo.piesocket.com/v3/paia?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV" \
#./games/pingpong \
#--difficulty NORMAL --game_over_score 3

#python -m mlgame \
#-f 30 -i ./ai_clients/pingpong/lv_4/ml_play.py -i ./ai_clients/pingpong/lv_4/ml_play.py \
#--ws "ws://localhost:8000/ws/game_server/room/035ed94d-0fcd-4462-bcc9-eb90ea3a9a73?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzAzNzI5NDA0LCJqdGkiOiI1YzA5MGIxMzY4NDU0YTFmYjNjNTM3ODQ5MTQwYTJlZiIsInVzZXJfaWQiOjEwMn0.-5G2h_ypAkBycSQq4qdz51s5FosV5x7nIjT7ZYHLqiA" \
#./games/pingpong \
#--difficulty EASY --game_over_score 3 \
#--init_vel 10
python -m mlgame \
-f 30 -i ./ai_clients/pingpong/lv_4/ml_play.py -i ./ai_clients/pingpong/lv_4/ml_play.py \
./games/pingpong \
--difficulty EASY --game_over_score 3 \
# --init_vel 10