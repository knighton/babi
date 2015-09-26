babi:
	python -m tests.babi

console:
	python -m scripts.console

env:
	virtualenv env --system-site-packages

wc:
	find . -type f -name "*.py" | grep -v ^\./env/ | grep -v ^\./data/ | xargs wc
