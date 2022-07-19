export MLG_VER="9.5.2.7-alpha"
docker build -t paia/mlgame:latest -t paia/mlgame:$MLG_VER  -t paiaimages.azurecr.io/mlgame:$MLG_VER \
	--build-arg MLG_VER .
docker image push paiaimages.azurecr.io/mlgame:$MLG_VER
