python -m mlgame \
--ws="wss://demo.piesocket.com/v3/arkanoid?api_key=VCXCEuvhGcBDP7XhiJJUDvR1e1D3eiVjgZ9VRiaV&notify_self" \
-1 -f 60  \
-i "./ai_clients/arkanoid/space path/ml_play.py" \
./games/arkanoid \
--difficulty NORMAL --level 1
#--ws="wss://dev-backend.paia-arena.com/ws/game_server/room/cff26f11-6bfc-4a07-9a6a-561ff84ba245?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjU4MjM0MjQ1LCJqdGkiOiIxM2I4NTFkZjg0ZDM0NjIzYjlmYmExYzQ4NzM4ZDM4OSIsInVzZXJfaWQiOjJ9.IcF2K-D7Q3MgXrZQhzN5DrQeDIgi45znBc3gKGp5Zbc" \

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
