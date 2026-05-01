from flask import Flask, request, jsonify
from matcher import process_image

app = Flask(__name__)

@app.route("/scan", methods=["POST"])
def scan():
    file = request.files["image"]
    result = process_image(file)
    return jsonify({"pokemon": result})

if __name__ == "__main__":
    app.run(debug=True)
