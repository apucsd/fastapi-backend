.PHONY: dev start install clean

dev:
	uvicorn app.main:app --reload --host 0.0.0.0

start:
	uvicorn app.main:app --host 0.0.0.0

install:
	pip install -r requirements.txt

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete