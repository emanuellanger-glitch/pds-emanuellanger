from flask import Flask, request, jsonify
from models import db, Dono, Pet

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///petshop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# Nova rota da Aula 03: listar pets de um dono específico usando dono.pets
@app.route("/donos/<int:id>/pets", methods=["GET"])
def listar_pets_do_dono(id):
    dono = db.session.get(Dono, id)
    if not dono:
        return jsonify({"erro": "Dono não encontrado"}), 404

    return jsonify([pet.to_dict() for pet in dono.pets]), 200


# --- Rotas da Aula 02 preservadas ---

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


@app.route("/pets", methods=["POST"])
def criar_pet():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição deve ser JSON válido"}), 400

    nome = dados.get("nome")
    especie = dados.get("especie")
    idade = dados.get("idade")
    dono_id = dados.get("dono_id")

    if (
        not nome
        or not str(nome).strip()
        or not especie
        or not str(especie).strip()
        or idade is None
        or dono_id is None
    ):
        return jsonify({"erro": "Campos obrigatórios: nome, especie, idade e dono_id"}), 400

    try:
        idade = int(idade)
        dono_id = int(dono_id)
    except (ValueError, TypeError):
        return jsonify({"erro": "idade e dono_id devem ser números inteiros"}), 400

    dono = db.session.get(Dono, dono_id)
    if not dono:
        return jsonify({"erro": "Dono não encontrado"}), 404

    novo_pet = Pet(
        nome=str(nome).strip(),
        especie=str(especie).strip(),
        idade=idade,
        dono_id=dono_id,
    )
    db.session.add(novo_pet)
    db.session.commit()

    return jsonify(novo_pet.to_dict()), 201


@app.route("/pets/<int:id>", methods=["PUT"])
def atualizar_pet(id):
    pet = db.session.get(Pet, id)
    if not pet:
        return jsonify({"erro": "Pet não encontrado"}), 404

    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Corpo da requisição deve ser JSON válido"}), 400

    if "nome" in dados:
        if not dados["nome"] or not str(dados["nome"]).strip():
            return jsonify({"erro": "O campo nome não pode ser vazio"}), 400
        pet.nome = str(dados["nome"]).strip()

    if "especie" in dados:
        if not dados["especie"] or not str(dados["especie"]).strip():
            return jsonify({"erro": "O campo especie não pode ser vazio"}), 400
        pet.especie = str(dados["especie"]).strip()

    if "idade" in dados:
        if dados["idade"] is None:
            return jsonify({"erro": "O campo idade não pode ser nulo"}), 400
        try:
            pet.idade = int(dados["idade"])
        except (ValueError, TypeError):
            return jsonify({"erro": "idade deve ser um número inteiro"}), 400

    if "dono_id" in dados:
        try:
            novo_dono_id = int(dados["dono_id"])
        except (ValueError, TypeError):
            return jsonify({"erro": "dono_id deve ser um número inteiro"}), 400

        dono = db.session.get(Dono, novo_dono_id)
        if not dono:
            return jsonify({"erro": "Dono não encontrado"}), 404
        pet.dono_id = novo_dono_id

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