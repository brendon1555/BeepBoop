clean:
	if [ -a dist ]; then rm -rf dist; fi;
	@echo "all clear! start re-buidling :)"

deploy:
	scp dist/*gz brendon@172.104.60.184:/home/brendon/BeepBoop/

dist:
	python setup.py clean
	python setup.py sdist