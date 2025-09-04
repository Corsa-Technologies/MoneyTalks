from flask import Flask
from flask_cors import CORS
import models
from log_reg import log_reg_bp
from extratos import extratos_bp  # novo import

app = Flask(__name__)
CORS(app)

# Registrar blueprints
app.register_blueprint(log_reg_bp)
app.register_blueprint(extratos_bp)  # registrar o extratos

if __name__ == "__main__":
    models.init_db()
    app.run(debug=True, port=5000)
