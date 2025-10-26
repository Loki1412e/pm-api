## Important !

Le proxy/docker-compose.yml n'est pas fonctionnel en l'état. Il manque des fichiers de configurations liés à cloudflared.

## Créer un utilisateur pour traefik dashboard

Modifie le contenu de la variable `BCRYPT_HASH` dans  le fichier [`.env`](./.env)

```bash
# user:hash // htpasswd -nbB username password
echo BCRYPT_HASH=$(htpasswd -nbB username password | sed 's/\$/\$\$/g') > ~/docker/traefik/.env
```