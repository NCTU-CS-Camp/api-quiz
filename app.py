from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 允許所有來源呼叫；若只開放特定網域，可改成 CORS(app, origins="http://10.0.0.5:3000")
CORS(app)

@app.route("/")
def hello():
    return "Hello, intranet!"

@app.route("/echo", methods=["GET"])
def echo_get():
    # 例如 /echo?msg=hi
    msg = request.args.get("msg", "")
    return jsonify({"you_sent": msg})

@app.route("/echo", methods=["POST"])
def echo_post():
    # JSON body: {"msg": "hi"}
    data = request.get_json() or {}
    return jsonify({"you_sent": data.get("msg", "")})

if __name__ == "__main__":
    # host="0.0.0.0" 讓內網所有機器都能存取
    app.run(host="0.0.0.0", port=9000, debug=True)
