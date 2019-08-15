exp:
	./load_exp.py -d -f ~/work/b2/data/test_passive_samplers/experiments/mapped_converted_VOC.csv -v ~/work/b2/b2_drought/vocabulary/experiment_controlled_vocabulary.csv -t ~/work/b2/b2_drought/vocabulary/experiment_typology.csv -T VOCs -p -o samples.json

load:
	mongoimport --jsonArray -d b2 -c load_test samples.json

reqs:
	python3 -m pip install -r requirements.txt

orm:
	sqlacodegen postgresql:///b2 > b2/model.py
