# Atelier - Chiffrement/Dechiffrement (Python)

## 1) Lancer le projet
- Fork / clone du repo
- Ouvrir dans GitHub Codespaces (ou en local)

## 2) Installer les dependances
```bash
pip install -r requirements.txt
```

## 3) Partie A - Chiffrer/Dechiffrer un texte (Fernet)
```bash
python app/fernet_demo.py
```

Role de la cle Fernet:
- Cle symetrique secrete (32 octets, encodee base64-urlsafe).
- Sert a chiffrer et authentifier les donnees.
- Si la cle est mauvaise ou le message est modifie, la decryption echoue.

## 4) Partie B - Chiffrer/Dechiffrer un fichier (Fernet)
Creer un fichier de test:
```bash
echo "Message Top secret !" > secret.txt
```

Chiffrer:
```bash
python app/file_crypto.py encrypt secret.txt secret.enc
```

Dechiffrer:
```bash
python app/file_crypto.py decrypt secret.enc secret.dec.txt
cat secret.dec.txt
```

Reponses:
- Si on modifie un octet du fichier chiffre, la verification d'integrite echoue et la decryption leve `InvalidToken`.
- Il ne faut jamais commiter la cle dans Git: toute personne avec acces au repo (ou a son historique) peut dechiffrer les donnees.

## 5) Atelier 1 - Cle Fernet dans un secret GitHub
Un nouveau programme est fourni: `app/fernet_atelier1.py`.

Principes:
- La cle n'est pas hardcodee.
- La cle est lue dans une variable d'environnement (ex: `FERNET_KEY`) alimentee par un secret GitHub.

Generer une cle:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Exemple d'utilisation:
```bash
python app/fernet_atelier1.py encrypt secret.txt secret.a1.enc
python app/fernet_atelier1.py decrypt secret.a1.enc secret.a1.dec.txt
```

Option utile:
```bash
python app/fernet_atelier1.py encrypt secret.txt secret.a1.enc --secret-name FERNET_KEY
```

## 6) Atelier 2 - Solution PyNaCl SecretBox
Une implementation complete est fournie: `app/secretbox_crypto.py`.

Generer une cle SecretBox (base64):
```bash
python app/secretbox_crypto.py genkey
```

Placer la cle dans `SECRETBOX_KEY_B64`, puis:
```bash
python app/secretbox_crypto.py encrypt secret.txt secret.sb
python app/secretbox_crypto.py decrypt secret.sb secret.sb.dec.txt
cat secret.sb.dec.txt
```

Comportement securite:
- SecretBox chiffre + authentifie.
- Si le fichier est modifie ou si la cle est mauvaise, la decryption echoue.
