import argparse
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


DEFAULT_SECRET_NAMES = ("FERNET_KEY", "GITHUB_FERNET_KEY", "REPO_FERNET_KEY")


def load_fernet(secret_name: str | None = None) -> Fernet:
    names = (secret_name,) if secret_name else DEFAULT_SECRET_NAMES

    for name in names:
        value = os.environ.get(name)
        if value:
            try:
                return Fernet(value.encode("utf-8"))
            except Exception as exc:  # pragma: no cover - defensive
                raise SystemExit(f"Erreur: la cle dans {name} est invalide ({exc}).")

    tested = ", ".join(names)
    raise SystemExit(
        "Erreur: aucune cle Fernet trouvee dans les variables d'environnement.\n"
        f"Variables testees: {tested}\n"
        "Exemple pour creer une cle:\n"
        "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    )


def encrypt_file(fernet: Fernet, input_path: Path, output_path: Path) -> None:
    data = input_path.read_bytes()
    token = fernet.encrypt(data)
    output_path.write_bytes(token)


def decrypt_file(fernet: Fernet, input_path: Path, output_path: Path) -> None:
    token = input_path.read_bytes()
    try:
        data = fernet.decrypt(token)
    except InvalidToken as exc:
        raise SystemExit(
            "Erreur: decryption impossible (mauvaise cle ou fichier modifie)."
        ) from exc
    output_path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Atelier 1 - chiffrement/dechiffrement de fichiers avec Fernet et cle "
            "fournie via secret GitHub (variable d'environnement)."
        )
    )
    parser.add_argument("mode", choices=("encrypt", "decrypt"))
    parser.add_argument("input", help="Fichier d'entree")
    parser.add_argument("output", help="Fichier de sortie")
    parser.add_argument(
        "--secret-name",
        default=None,
        help="Nom de la variable d'environnement qui contient la cle Fernet",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Erreur: fichier introuvable: {input_path}")

    output_path = Path(args.output)
    fernet = load_fernet(args.secret_name)

    if args.mode == "encrypt":
        encrypt_file(fernet, input_path, output_path)
        print(f"OK: fichier chiffre -> {output_path}")
    else:
        decrypt_file(fernet, input_path, output_path)
        print(f"OK: fichier dechiffre -> {output_path}")


if __name__ == "__main__":
    main()
