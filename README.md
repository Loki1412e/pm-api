## Frontend

Cette API est consommée par l'extension navigateur officielle, dont le code se trouve ici :
➡️ **[pm-extension](https://github.com/Loki1412e/pm-extension)**

### **Première connexion**

**1. Interaction serveur**

* L’utilisateur crée son compte ou se logue avec `username` + `password`.
* Le serveur renvoie :

  * Un `JWT` pour l’authentification des requêtes futures.
  * Son coffre chiffré existant (vide la première fois, sinon un tableau de credentials chiffrés).

**2. En local**

* L’utilisateur saisit pour la première fois son `masterPassword`.
* On dérive une clé (`deriveKey`) depuis le `masterPassword` et un `salt` aléatoire.
* On crée un credential **de vérification** :

  * `domain = "password-manager"`
  * `ciphertext = encrypt(deriveKey, "valid")` (ou un payload simple type `"PMv1:<username>"`)
  * `iv` et `salt` générés.
* Ce credential permet de tester la validité future du masterPassword.
* On déchiffre tout le coffre reçu du serveur (s’il y en a) avec `deriveKey`.
* Les credentials sont stockés en local (ex: `chrome.storage.local`), chiffrés avec `deriveKey`.
* Si l’utilisateur sauvegarde de nouveaux passwords, ils sont chiffrés avec `deriveKey` et envoyés à l’API pour stockage.

---

### **Connexion suivante**

**1. Interaction serveur**

* L’utilisateur se logue avec `username` + `password`.
* Le serveur renvoie :

  * Un `JWT` valide.
  * Le coffre chiffré.

**2. En local**

* L’utilisateur saisit son `masterPassword`.
* On dérive la clé (`deriveKey`) à nouveau depuis ce masterPassword.
* On tente de déchiffrer le credential spécial `domain = "password-manager"` :

  * Si le déchiffrement est correct et que le payload correspond (`"PM:<username>"`), le masterPassword est valide.
  * Sinon, on affiche une alerte `"Mauvais master password"`.
* Si masterPassword correct :

  * On peut déchiffrer l’ensemble du coffre.
  * L’utilisateur peut autofill, créer, modifier ou supprimer des credentials.
  * Les nouvelles entrées sont chiffrées localement avec `deriveKey` et envoyées au serveur.

---

### **Points importants**

* **JWT** : utilisé uniquement pour authentifier les requêtes côté serveur. Il change régulièrement et n’est pas utilisé pour le chiffrement.
* **MasterPassword / deriveKey** : jamais envoyé au serveur. Sert uniquement à chiffrer/déchiffrer le coffre.
* **Credential de vérification** (`password-manager`) : permet de tester que le masterPassword est correct sans stocker de données sensibles en clair.