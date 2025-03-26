from flask import Flask, render_template
from board import board_bp
from pds import pds_bp

app = Flask(__name__)

app.register_blueprint(board_bp, url_prefix="/board")
app.register_blueprint(pds_bp, url_prefix="/pds")

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
