import subprocess
import os
import webbrowser
import time

# Chemin vers le dossier du projet
os.chdir(r'C:\App\PHARMA')

# Lance le serveur Django
subprocess.Popen([r'env\\Scripts\\python.exe', 'manage.py', 'runserver'])

# Attend quelques secondes que le serveur démarre
time.sleep(3)

# Ouvre le navigateur par défaut sur l'application
webbrowser.open('http://127.0.0.1:8000/')
