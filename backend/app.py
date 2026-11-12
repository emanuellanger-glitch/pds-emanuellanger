from flask import Flask, request, jsonify
from models import db, Dono, Pet

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///petshop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# Exercício 1: função de validação acumulando todos os erros
def validar_pet(dados):
    if not isinstance(dados, dict):
        return ["Corpo da requisição deve ser um JSON válido"]

    erros = []

    nome = dados.get("nome")
    if not isinstance(nome, str) or not nome.strip():
        erros.append("O campo 'nome' é obrigatório e não pode ser vazio")

    especie = dados.get("especie")
    if not isinstance(especie, str) or not especie.strip():
        erros.append("O campo 'especie' é obrigatório e não pode ser vazio")

    idade = dados.get("idade")
    if idade is None or isinstance(idade, bool) or not isinstance(idade, int):
        erros.append("O campo 'idade' é obrigatório e deve ser um número inteiro")
    elif idade < 0:
        erros.append("O campo 'idade' deve ser maior ou igual a zero")

    dono_id = dados.get("dono_id")
    if dono_id is None or isinstance(dono_id, bool) or not isinstance(dono_id, int):
        erros.append("O campo 'dono_id' é obrigatório e deve ser um número inteiro")
    else:
        dono = db.session.get(Dono, dono_id)
        if not dono:
            erros.append("O 'dono_id' informado não corresponde a um dono existente")

    return erros


# --- Rotas GET e DELETE intactas ---

@app.route("/donos/<int:id>/pets", methods=["GET"])
def listar_pets_do_dono(id):
    dono = db.session.get(Dono, id)
    if not dono:
        return jsonify({"erro": "Dono não encontrado"}), 404

    return jsonify([pet.to_dict() for pet in dono.pets]), 200


@app.route("/pets", methods=["GET"])
def listar_pets():
    dono_id = request.args.get("dono_id")

    if dono_id is not None:
        try:
            dono_id_int = int(dono_id)
        except ValueError:
            return jsonify({"erro": "O parâmetro dono_id deve ser um inteiro"}), 400

        pets = Pet.query.filter_by(dono_id=dono_id_int).all()
    else:
        pets = Pet.query.all()

    return jsonify([pet.to_dict() for pet in pets]), 200


@app.route("/pets/<int:id>", methods=["GET"])
def buscar_pet(id):
    pet = db.session.get(Pet, id)
    if not pet:
        return jsonify({"erro": "Pet não encontrado"}), 404

    return jsonify(pet.to_dict()), 200


# Exercício 2: POST usando validar_pet antes de qualquer db.session.add
@app.route("/pets", methods=["POST"])
def criar_pet():
    dados = request.get_json(silent=True)
    erros = validar_pet(dados)

    if erros:
        return jsonify({"erros": erros}), 400

    novo_pet = Pet(
        nome=dados["nome"].strip(),
        especie=dados["especie"].strip(),
        idade=dados["idade"],
        dono_id=dados["dono_id"],
    )
    db.session.add(novo_pet)
    db.session.commit()

    return jsonify(novo_pet.to_dict()), 201


# Exercício 2: PUT usando a mesma função validar_pet
@app.route("/pets/<int:id>", methods=["PUT"])
def atualizar_pet(id):
    pet = db.session.get(Pet, id)
    if not pet:
        return jsonify({"erro": "Pet não encontrado"}), 404

    dados = request.get_json(silent=True)
    erros = validar_pet(dados)

    if erros:
        return jsonify({"erros": erros}), 400

    pet.nome = dados["nome"].strip()
    pet.especie = dados["especie"].strip()
    pet.idade = dados["idade"]
    pet.dono_id = dados["dono_id"]

    db.session.commit()
    return jsonify(pet.to_dict()), 200


@app.route("/pets/<int:id>", methods=["DELETE"])
def deletar_pet(id):
    pet = db.session.get(Pet, id)
    if not pet:
        return jsonify({"erro": "Pet não encontrado"}), 404

    db.session.delete(pet)
    db.session.commit()
    return jsonify({"mensagem": "Pet removido com sucesso"}), 200


if __name__ == "__main__":
    app.run(debug=True)