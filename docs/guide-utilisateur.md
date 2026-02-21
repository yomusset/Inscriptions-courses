# Guide utilisateur — Site inscriptions courses

## Démarrage rapide

1. Ouvrir un terminal dans le projet.
2. Lancer:

```bash
./run.sh
```

3. Ouvrir <http://localhost:8000>.

## Pages du site

- `/` : accueil.
- `/coureurs` : créer et voir les coureurs.
- `/courses` : ajouter et voir les courses.
- `/inscriptions` : inscrire un coureur à une course.
- `/synthese` : vue récapitulative.

## Vérification automatique

```bash
./smoke_test.sh
```

Le script vérifie que le site répond et que le scénario principal fonctionne.
