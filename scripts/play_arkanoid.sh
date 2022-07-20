python -m mlgame \
-1 -f 60 --nd  \
-i "./ai_clients/arkanoid/space path/ml_play.py" \
--ws "wss://demo.piesocket.com/v3/arkanoid?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV" \
./games/arkanoid \
--difficulty NORMAL --level 1

#python -m mlgame \
#--ws "wss://demo.piesocket.com/v3/paia?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV&notify_self" \
#-f 60 -1 -i ./ai_clients/arkanoid/error_at_70f/ml_play.py \
#./games/arkanoid \
#--difficulty NORMAL --level 3

#python -m mlgame \
#--ws "wss://demo.piesocket.com/v3/paia?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV&notify_self" \
#-f 60 -1 -i ./ai_clients/arkanoid/error_at_syntax/ml_play.py \
#./games/arkanoid \
#--difficulty NORMAL --level 3

#python -m mlgame \
#--ws "wss://demo.piesocket.com/v3/paia?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV&notify_self" \
#-f 60 -1 -i ./ai_clients/arkanoid/error_at_import/ml_play.py \
#./games/arkanoid \
#--difficulty NORMAL --level 3
