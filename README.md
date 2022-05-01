# Déclarations - Projet Python

Ce projet a été réalisé dans le cadre du cours de développement applicatif du master 2 "Technologies numériques appliquées à l'histoire" à l'Ecole nationale des chartes. 
Il recense des procès-verbaux enregistrés pour vol à la Comédie-Française, Comédie-Italienne et Académie royale de musique (Opéra) à la fin du XVIIIe siècle.
Les documents sont conservés dans la série Y des Archives nationales qui contient les archives du Châtelet de Paris dont les papiers des commissaires de police.

## Description de l'application

Cette application est développée avec Flask et SQLAlchemy. Elle permet de naviguer dans les données enregistrées et, par un formulaire d'inscription, de les modifier, les supprimer ou en ajouter. Des index et des pages individuelles sont à disposition ainsi qu'une possibilité de recherche. Une carte permet de visualiser la localisation des théâtres.

## Installation

- Cloner le dépôt : `git clone https://github.com/margauxfre/Declarations-Projet_python.git`
- Se déplacer dans le dossier
- Vérifier sa version de Python ou installer Python3
- Installer un environnement virtuel et l'activer : `virtualenv -p python3 env` puis `source env/bin/activate`
- Lancer la commande : `pip install -r requirements.txt`
- Lancer la commande : `python run.py`
