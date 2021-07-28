migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

isort:
	isort .

black:
	black . --line-length=78

fine: isort black

lint:
	flake8

test:
	pytest