none:
	@echo Not doing anything by default.

init:
	pip install -r requirements.txt

freeze:
	pip freeze --exclude wincertstore --exclude certifi > requirements.txt

test:
	pytest -s tests

.PHONY: none init freeze test