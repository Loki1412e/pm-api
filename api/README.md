# Password Manager API

Une API de gestionnaire de mots de passe sécurisée, containerisée avec FastAPI, SQLAlchemy (async) et PostgreSQL. Elle permet aux utilisateurs de gérer leurs identifiants avec chiffrement fort et authentification JWT.

## Fonctionnalités

- Création, connexion, modification et suppression d'utilisateur
- Gestion des identifiants (ajout, lecture, modification, suppression)
- Mots de passe chiffrés avec AES-GCM via un mot de passe maître
- Authentification JWT pour tous les endpoints sensibles
- Endpoint de vérification de santé (API et DB)
- Dockerisé pour un déploiement facile
- Prêt pour intégration avec Traefik

## Structure du projet

```
.
├── api/                # Application FastAPI
│   ├── main.py         # Point d'entrée
│   ├── core/           # Config, cryptographie, hash, logs, etc.
│   ├── dao/            # Accès base de données
│   ├── db/             # Session et base DB
│   ├── models/         # Modèles SQLAlchemy
│   ├── routes/         # Routes FastAPI
│   ├── schemas/        # Schémas Pydantic
│   ├── services/       # Logique métier
│   └── requirements.txt
├── docs/               # Documentation API (Postman)
├── postgres/           # Volume de données PostgreSQL
├── Dockerfile          # Build du container FastAPI
├── docker-compose.yml  # Orchestration multi-service
├── .env                # Variables d'environnement
└── .gitignore
```

## Démarrage rapide

1. **Cloner le dépôt**

   ```sh
   git clone git@github.com:Loki1412e/Password-Manager.git
   ```

2. **Configurer le fichier `.env`**  
   Exemple :
   ```
   POSTGRES_USER=youruser
   POSTGRES_PASSWORD=yourpassword
   POSTGRES_NAME=yourdb
   POSTGRES_PORT=5432
   JWT_SECRET_KEY=your_jwt_secret
   JWT_ALGO=HS256
   ```

3. **Préparer le volume PostgreSQL**  
   Créez le dossier `./postgres/data` avant de lancer le container.

4. **Construire et lancer les conteneurs**
   ```sh
   docker compose -f traefik-docker-compose.yml up -d  && docker compose up -d --build
   ```

   > **Notes :** J'utilise le container traefik pour plusieurs de mes projets, c'est pour cela qu'il est dans un docker-compose différent. Le réseau `traefik` doit être créé avant d'utiliser `docker-compose.yml`, c'est pour cela qu'il faut lancer `traefik-docker-compose.yml` dans un premier temps.

5. **Accéder à l’API**
   - Documentation : [https://localhost/pm/api/docs](https://localhost/pm/api/docs)
   - Healthcheck : `/pm/api/utils/healthcheck`

## Endpoints principaux

- **Utilisateur**
  - `PUT /user/create` — Inscription
  - `POST /user/login` — Connexion (username / password)
  - `GET /user/read` — Infos utilisateur (JWT)
  - `PATCH /user/update` — Modifier (JWT / password)
  - `DELETE /user/delete` — Supprimer (JWT / password)
  - `GET /user/count` — Compter les utilisateurs

- **Identifiants**
  - `PUT /credentials/create` — Ajouter (JWT)
  - `GET /credentials/list` — Lister (JWT)
  - `GET /credentials/read/{id}` — Lire (JWT / password)
  - `PATCH /credentials/update/{id}` — Modifier (JWT / password)
  - `DELETE /credentials/delete/{id}` — Supprimer (JWT / password)

- **Utils**
  - `GET /utils/healthcheck` — Statut API & DB

## Sécurité

- Mots de passe et mot de passe maître hachés et chiffrés (Scrypt, AES-GCM)
- Authentification JWT
- Accès aux identifiants réservé à leur propriétaire

## Développement

- Python 3.11
- FastAPI, SQLAlchemy (async), asyncpg, Alembic, Pydantic, Cryptography, PyJWT

---

**Liens utiles :**  
- [`api/main.py`](api/main.py) — Entrée FastAPI  
- [`api/core/cryptography.py`](api/core/cryptography.py) — Chiffrement  
- [`api/routes/user.py`](api/routes/user.py) — Routes utilisateur  
- [`api/routes/credential.py`](api/routes/credential.py) — Routes identifiants  
