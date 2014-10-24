.PHONY: clean,all,docs,test,install

clean:
	rm -rf *.out *.xml htmlcov

install:
	virtualenv venv && \
		pip install -r requirements.txt

test: install
	source venv/bin/activate && \
		py.test --cov=sandman2 tests
