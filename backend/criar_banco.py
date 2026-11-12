from app import app
from models import db, Dono, Pet

with app.app_context():
    db.drop_all()
    db.create_all()

    dono1 = Dono(nome="Ana Silva", telefone="(45) 99999-1111")
    dono2 = Dono(nome="Carlos Souza", telefone="(45) 98888-2222")

    db.session.add_all([dono1, dono2])
    db.session.commit()

    pets = [
        Pet(nome="Rex", especie="Cachorro", idade=3, dono_id=dono1.id),
        Pet(nome="Mimi", especie="Gato", idade=2, dono_id=dono1.id),
        Pet(nome="Thor", especie="Cachorro", idade=5, dono_id=dono2.id),
    ]

    db.session.add_all(pets)
    db.session.commit()

    print("Banco criado e populado com sucesso!")