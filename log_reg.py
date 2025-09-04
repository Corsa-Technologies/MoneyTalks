from flask import Blueprint, request, jsonify
from database import get_db

log_reg_bp = Blueprint("log_reg", __name__)

@log_reg_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username e password obrigatórios"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        user_id = cur.lastrowid
    except Exception as e:
        return jsonify({"error": f"falha no cadastro: {str(e)}"}), 400
    finally:
        conn.close()

    return jsonify({"message": "usuário cadastrado com sucesso", "user_id": user_id})


@log_reg_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if not row or row["password"] != password:
        return jsonify({"error": "usuário ou senha incorretos"}), 401

    return jsonify({"message": "login bem-sucedido", "user_id": row["id"]})
