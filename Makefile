# ------------------------------------------------------------------------------
# Evaluation.

babi:
	time python -m tests.babi_html > data/babi_html.out

english:
	time python -m tests.test_english > data/test_english.out

mind:
	time python -m tests.test_babi_like > data/test_babi_like.out

# ------------------------------------------------------------------------------
# Setup.

setup:
	virtualenv env --system-site-packages
	. env/bin/activate
	pip install -r requirements.txt
	python -m spacy.en.download

# ------------------------------------------------------------------------------
# Views.

console:
	python -m scripts.console

wc:
	find . -type f -name "*.py" | grep -v ^\./env/ | grep -v ^\./data/ | xargs wc
