babi:
	python -m tests.babi

env:
	virtualenv env --system-site-packages

wc:
	find . -type f -name "*.py" | grep -v ^\./env/ | grep -v ^\./data/ | xargs wc
