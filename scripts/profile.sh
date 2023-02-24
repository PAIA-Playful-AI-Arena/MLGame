export FILE=profile-2.pstats

python -m cProfile -s cumtime -o $FILE \
-m mlgame  -1 \
-i ./games/arkanoid/ml/ml_play_template.py ./games/arkanoid --level=15
python -m gprof2dot -f pstats $FILE | dot -T png -o ${FILE}.png