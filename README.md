# Modèle Django sur Docker + Nginx + MySQL + PhpMyAdmin


1. Clonez le dépôt sur votre machine locale ou votre serveur :

  ```bash
  git clone https://github.com/monsieur-ned/lifestylesante.git
  ```

2. Accédez au dossier du projet :

  ```bash
  cd lifestylesante
  ```

3. Lancez le projet avec la commande docker-compose suivante :

  ```bash
  docker-compose up --build
  ```

4. Après avoir exécuté les étapes ci-dessus, vous devriez voir le site Django fonctionner sur le port 9080. Rendez-vous sur le lien suivant pour vérifier. Si vous voyez la fusée Django sur la page, tout devrait fonctionner correctement.

  ```
  localhost: 9080 # <-- Django site
  localhost: 9090 # <-- PhpMyAdmin page
  localhost: 3306 # <-- MySQL server
  ```

5. À ce stade, tout devrait fonctionner comme prévu. J'espère que cela vous aidera pour le déploiement de votre site.
