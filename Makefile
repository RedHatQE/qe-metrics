pre-commit:
	pre-commit run --all-files

test:
	tox

commit: pre-commit test
