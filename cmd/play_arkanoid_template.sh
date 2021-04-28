python -m cProfile -o pi.pstats MLGame.py --transition-channel=redis-k2t9v5gafkduando.japaneast.azurecontainer.io:6379:mlgame_test -f 30 -1 -i ml_play_template.py arkanoid NORMAL 1
#python -m cProfile -o pi.pstats MLGame.py -f 30 -1 -i ml_play_template.py arkanoid NORMAL 1
python -m gprof2dot -f pstats pi.pstats | dot -T png -o pi_profile.png
