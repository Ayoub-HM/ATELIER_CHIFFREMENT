import argparse
import base64
import os
from pathlib import Path

from nacl.exceptions import CryptoError
from nacl.secret import SecretBox
from nacl.utils import random as nacl_random


DEFAULT_KEY_NAMES = ("SECRETBOX_KEY_B64", "GITHUB_SECRETBOX_KEY_B64")


def generate_key() -> str:
    return base64.b64encode(nacl_random(SecretBox.KEY_SIZE)).decode("ascii")


def load_box(key_name: str | None = None) -> SecretBox:
    names = (key_name,) if key_name else DEFAULT_KEY_NAMES

    for name in names:
        value = os.environ.get(name)
        if not value:
            continue

        try:
            raw_key = base64.b64decode(value)
        except Exception as exc:
            raise SystemExit(f"Erreur: la valeur de {name} n'est pas du base64 valide.") from exc

        if len(raw_key) != SecretBox.KEY_SIZE:
            raise SystemExit(
                f"Erreur: la cle {name} doit faire {SecretBox.KEY_SIZE} octets apres decode base64."
            )
        return SecretBox(raw_key)

    tested = ", ".join(names)
    raise SystemExit(
        "Erreur: aucune cle SecretBox trouvee dans l'environnement.\n"
        f"Variables testees: {tested}\n"
        f"Genere une cle avec: python app/secretbox_crypto.py genkey"
    )


def encrypt_file(box: SecretBox, input_path: Path, output_path: Path) -> None:
    plaintext = input_path.read_bytes()
    nonce = nacl_random(SecretBox.NONCE_SIZE)
    encrypted = box.encrypt(plaintext, nonce)
    output_path.write_bytes(bytes(encrypted))


def decrypt_file(box: SecretBox, input_path: Path, output_path: Path) -> None:
    encrypted = input_path.read_bytes()
    try:
        plaintext = box.decrypt(encrypted)
    except CryptoError as exc:
        raise SystemExit(
            "Erreur: decryption impossible (mauvaise cle ou donnees modifiees)."
        ) from exc
    output_path.write_bytes(plaintext)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chiffrement/dechiffrement de fichiers avec PyNaCl SecretBox."
    )
    parser.add_argument("mode", choices=("genkey", "encrypt", "decrypt"))
    parser.add_argument("input", nargs="?", help="Fichier d'entree")
    parser.add_argument("output", nargs="?", help="Fichier de sortie")
    parser.add_argument(
        "--key-name",
        default=None,
        help="Nom de la variable d'environnement contenant la cle base64",
    )
    args = parser.parse_args()

    if args.mode == "genkey":
        print(generate_key())
        return

    if not args.input or not args.output:
        raise SystemExit("Erreur: input/output requis pour encrypt et decrypt.")

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Erreur: fichier introuvable: {input_path}")

    output_path = Path(args.output)
    box = load_box(args.key_name)

    if args.mode == "encrypt":
        encrypt_file(box, input_path, output_path)
        print(f"OK: fichier chiffre -> {output_path}")
    else:
        decrypt_file(box, input_path, output_path)
        print(f"OK: fichier dechiffre -> {output_path}")


if __name__ == "__main__":
    main()
