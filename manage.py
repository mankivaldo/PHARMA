#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv


def main():
    """Run administrative tasks."""
    # Charge les variables d'environnement depuis le fichier .env en utilisant l'encodage UTF-8.
    # C'est la méthode la plus robuste pour éviter les problèmes d'encodage.
    load_dotenv(encoding='utf-8')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Pharma.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
