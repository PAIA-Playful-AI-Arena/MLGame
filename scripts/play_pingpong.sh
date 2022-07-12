#python -m mlgame \
#-f 50 -i ./ai_clients/pingpong/start/ml_play.py -i ./ai_clients/pingpong/start/ml_play.py \
#./games/pingpong \
#--difficulty NORMAL --game_over_score 3

python -m mlgame \
-f 50 -i ./ai_clients/pingpong/rule/ml_play.py -i ./ai_clients/pingpong/rule/ml_play.py \
--ws "wss://demo.piesocket.com/v3/paia?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV" \
./games/pingpong \
--difficulty NORMAL --game_over_score 3

#python -m mlgame \
#-f 120 -i ./ai_clients/pingpong/error_at_1p_50f/ml_play.py -i ./ai_clients/pingpong/error_at_2p_import/ml_play.py \
#--ws "wss://demo.piesocket.com/v3/paia?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV" \
#./games/pingpong \
#--difficulty NORMAL --game_over_score 3
