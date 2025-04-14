import os
import sys
import django

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Pharma.settings')
django.setup()

from django.contrib.auth.models import User
from Produits.models import UserProfile

def create_admin_profile():
    try:
        # Récupérer le superutilisateur
        admin = User.objects.get(username='Valdo')
        print(f"Superutilisateur trouvé: {admin.username}")
        
        # Vérifier si le profil existe
        if not hasattr(admin, 'profile'):
            # Créer le profil
            UserProfile.objects.create(
                user=admin,
                type_utilisateur='ADMIN',
                telephone='',
                adresse='',
                est_actif=True
            )
            print("Profil admin créé avec succès")
        else:
            print("Le profil admin existe déjà")
            
    except User.DoesNotExist:
        print("Le superutilisateur 'Valdo' n'existe pas")
    except Exception as e:
        print(f"Une erreur s'est produite: {str(e)}")

if __name__ == "__main__":
    create_admin_profile() 