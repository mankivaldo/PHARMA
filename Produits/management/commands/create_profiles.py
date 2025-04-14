from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Produits.models import UserProfile

class Command(BaseCommand):
    help = 'Crée des profils pour les utilisateurs existants qui n\'en ont pas'

    def handle(self, *args, **options):
        # Récupérer tous les utilisateurs sans profil
        users_without_profile = User.objects.filter(profile__isnull=True)
        
        # Créer un profil pour chaque utilisateur
        for user in users_without_profile:
            UserProfile.objects.create(
                user=user,
                type_utilisateur='ADMIN' if user.is_superuser else 'USER',
                est_actif=True
            )
            self.stdout.write(self.style.SUCCESS(f'Profil créé pour l\'utilisateur {user.username}'))
        
        self.stdout.write(self.style.SUCCESS('Tous les profils ont été créés avec succès !')) 