#python -m mlgame -i ./games/racing_car/ml/ml_play_template.py -f 120 \
#--nd \
#./games/RacingCar/ --racetrack_length 1000

python -m mlgame \
-1 -f 60   \
-i ./ai_clients/RacingCar/start/ml_play.py \
-i ./ai_clients/RacingCar/start/ml_play.py \
-i ./ai_clients/RacingCar/start/ml_play.py \
-i ./ai_clients/RacingCar/start/ml_play.py \
./games/racing_car
