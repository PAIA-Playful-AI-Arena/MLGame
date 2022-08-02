coverage run -m pytest mlgame/tests/ -v \
#-n auto\
coverage report -m
coverage html
coverage lcov