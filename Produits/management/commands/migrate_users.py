from django.core.management.base import BaseCommand
from Produits.models import Utilisateur, CustomUser
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Migre les utilisateurs existants vers le nouveau modèle CustomUser'

    def handle(self, *args, **kwargs):
        self.stdout.write('Début de la migration des utilisateurs...')
        
        for ancien_user in Utilisateur.objects.all():
            try:
                # Vérifier si l'utilisateur existe déjà
                if not CustomUser.objects.filter(username=ancien_user.utilisateur).exists():
                    nouveau_user = CustomUser(
                        username=ancien_user.utilisateur,
                        email=ancien_user.email,
                        password=ancien_user.mot_de_passe,  # Le mot de passe est déjà hashé
                        is_active=True
                    )
                    nouveau_user.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'Utilisateur migré avec succès : {ancien_user.utilisateur}'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'L\'utilisateur existe déjà : {ancien_user.utilisateur}'
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Erreur lors de la migration de {ancien_user.utilisateur}: {str(e)}'
                ))
        
        self.stdout.write(self.style.SUCCESS('Migration terminée !'))
