# PharmaSys - Système de Gestion de Pharmacie

Un système de gestion de pharmacie développé avec Django pour gérer les produits, les ventes, les clients et les utilisateurs.

## Fonctionnalités

- Gestion des produits (ajout, modification, suppression)
- Gestion des ventes
- Gestion des clients
- Gestion des utilisateurs
- Gestion des conditions de paiement
- Gestion des catégories de produits
- Tableau de bord
- Interface utilisateur moderne et responsive

## Prérequis

- Python 3.8+
- Django 4.0+
- pip

## Installation

1. Clonez le dépôt :

```bash
git clone https://github.com/votre-username/PHARMA.git
cd PHARMA
```

2. Créez un environnement virtuel :

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installez les dépendances :

```bash
pip install -r requirements.txt
```

4. Appliquez les migrations :

```bash
python manage.py migrate
```

5. Créez un superutilisateur :

```bash
python manage.py createsuperuser
```

6. Lancez le serveur de développement :

```bash
python manage.py runserver
```

## Structure du Projet

```
PHARMA/
├── Produits/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── Pharma/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── requirements.txt
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
