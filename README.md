# Site web du club running (inscriptions aux courses)

Ce projet fournit un **site web** pour gérer les inscriptions aux courses:

- création de compte coureur (prénom, nom, email, date de naissance),
- ajout de courses,
- inscription d'un coureur à une course existante,
- pages de synthèse par coureur et par course.

## Lancer simplement pour tester

```bash
./run.sh
```

Puis ouvrir `http://localhost:8000`.

Par défaut, `run.sh` stocke la base SQLite à cet emplacement Mac:

`/Users/ymusset/Library/CloudStorage/GoogleDrive-yo.musset@gmail.com/Mon Drive/1 Drive Perso/4 - Sites web/inscriptions courses/running_club.db`

## Envoyer la documentation dans votre dossier Drive local

```bash
./export_docs.sh
```

Ce script copie:

- `README.md`
- `docs/guide-utilisateur.md`

vers:

`/Users/ymusset/Library/CloudStorage/GoogleDrive-yo.musset@gmail.com/Mon Drive/1 Drive Perso/4 - Sites web/inscriptions courses`

Vous pouvez aussi changer la destination:

```bash
DOCS_TARGET_DIR="/votre/dossier" ./export_docs.sh
```

## Vérifier rapidement que tout marche

```bash
./smoke_test.sh
```

Ce script lance le serveur, teste les pages principales et un scénario complet (création coureur, course, inscription), puis s'arrête automatiquement.

## Navigation

- `/` : accueil,
- `/coureurs` : gestion des coureurs,
- `/courses` : gestion des courses,
- `/inscriptions` : inscriptions coureur/course,
- `/synthese` : vues synthétiques.

## Configuration du chemin de base de données

Vous pouvez surcharger le chemin avec la variable d'environnement:

```bash
RUNNING_CLUB_DB_PATH="/votre/chemin/running_club.db" python3 app.py
```
