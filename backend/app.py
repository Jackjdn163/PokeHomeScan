from flask import Flask, jsonify, request
from PIL import UnidentifiedImageError

from matcher import process_image

app = Flask(__name__)


@app.route("/scan", methods=["POST"])
def scan():
    if "image" not in request.files:
        return jsonify({"error": "Missing image file field 'image'"}), 400

    file = request.files["image"]
    if not file or file.filename == "":
        return jsonify({"error": "No image selected"}), 400

    try:
        result = process_image(file)
    except UnidentifiedImageError:
        return jsonify({"error": "Uploaded file is not a valid image"}), 400

    return jsonify({"results": result, "count": len(result)})


if __name__ == "__main__":
    app.run(debug=True)
