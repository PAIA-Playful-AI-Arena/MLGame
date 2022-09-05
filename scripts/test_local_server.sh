python -m mlgame \
--ws="ws://127.0.0.1:8000/ws/game_server/room/8770a056-f083-47f8-a74a-21360bf7691a?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc4NTA3MjQ2LCJqdGkiOiJhMzFlMTliMTVjNDA0ODRhYWYzMDg0YTE5YjhmNjJjZiIsInVzZXJfaWQiOjF9.BYzkFvHOdmJHQcbkdvaIuKxic5kGQOXhEJLl0qE2OLA" \
-f 200 --nd -1 \
-i ./games/Maze_Car/ml/ml_play_template.py \
./games/Maze_Car \
--game_type MAZE --time_to_play 5400

#python -m mlgame \
#--ws="ws://127.0.0.1:8000/ws/game_server/room/8770a056-f083-47f8-a74a-21360bf7691a?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc4NTA3MjQ2LCJqdGkiOiJhMzFlMTliMTVjNDA0ODRhYWYzMDg0YTE5YjhmNjJjZiIsInVzZXJfaWQiOjF9.BYzkFvHOdmJHQcbkdvaIuKxic5kGQOXhEJLl0qE2OLA" \
#-f 200 --nd -1 \
#-i ./games/arkanoid/ml/ml_play_template.py \
#./games/arkanoid \
#--difficulty EASY --level 1

