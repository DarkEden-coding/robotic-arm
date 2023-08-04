from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

requested_moves = None


@app.route("/move", methods=["POST", "OPTIONS"])
def move():
    global requested_moves

    if request.method == "OPTIONS":
        response = jsonify({"status": "success"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    data = request.json
    requested_moves = data
    print("Received data:", data)
    return "Move request received"

@app.route("/get_move", methods=["GET", "OPTIONS"])


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=False)
