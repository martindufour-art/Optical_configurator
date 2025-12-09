
PYTHON = python3
PIP = pip3
ENV = venv

# Création de l'environnement virtuel
venv:
	$(PYTHON) -m venv $(ENV)

# Installation des dépendances
install: venv
	$(ENV)/bin/$(PIP) install --upgrade pip
	$(ENV)/bin/$(PIP) install -r requirements.txt

# Lancer l'application
run:
	$(ENV)/bin/$(PYTHON) main.py


# Nettoyage fichiers temporaires
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.pytest_cache" -exec rm -r {} +
	rm -rf .mypy_cache

# Supprime complètement l'environnement virtuel
clean-env:
	rm -rf $(ENV)
