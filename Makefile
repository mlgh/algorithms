install: .PHONY
	pip install . --upgrade --force --no-binary :all:

test:
	py.test tests

.PHONY:
