"""Promove um usuário já cadastrado a administrador.

Uso: python make_admin.py email@exemplo.com
"""
import sys

from sqlalchemy.orm import sessionmaker

from models import User, db


def main(email: str) -> int:
    with sessionmaker(bind=db)() as session:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            print(f"Usuário '{email}' não encontrado. Cadastre-o antes em POST /auth/create_user.")
            return 1
        user.admin = True
        session.commit()
        print(f"Usuário '{email}' agora é administrador.")
        return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python make_admin.py email@exemplo.com")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
