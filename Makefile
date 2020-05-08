.PHONY: installenv installnodeenv buildnodemodules cleannodemodules initsystem help

PATH  := $(PWD)/../venv/bin:$(PWD)/../nodeenv/bin:$(PATH)
SHELL := env PATH=$(PATH) /bin/bash

help: ##how to use
	@echo "installenv installnodeenv buildnodemodules cleannodemodules initsystem help"


installenv: ##install python env and other tools
	@echo "Install Python3 env !"
	@virtualenv -p /usr/bin/python3.6 ../venv
	@pip install -r requirements.txt -i https://pypi.douban.com/simple
	@pip install nodeenv -i https://pypi.douban.com/simple


installnodeenv: ##install node env
	@echo "Install NodeEnv and nodemodules!"
	@nodeenv ../nodeenv --node=10.15.3 --prebuilt --mirror=npm.taobao.org
	@npm install -g yarn --registry https://registry.npm.taobao.org
	@cd ./templates/mystorageapp/ && yarn install --registry  https://registry.npm.taobao.org
	#@cd ./media/libs/ && yarn install --registry  https://registry.npm.taobao.org


buildnodemodules:
	@echo "build the node modules"
	@cd ./templates/mystorageapp/  && yarn run build


cleannodemodules:
	@echo "clean the node modules"
	@rm -Rf ./templates/mystorageapp/node_modules


initsystem:
	@echo "Init the system using docker/install/init_web.sh !"
	@bash docker/install/init_web.sh
