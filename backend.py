from flask import Flask, request, jsonify, session
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure WebAuthn server
rp = PublicKeyCredentialRpEntity("desktop-app", "Desktop App")
server = Fido2Server(rp)

users = {}

@app.route('/register_begin', methods=['POST'])
def register_begin():
    username = request.json["username"]
    user = PublicKeyCredentialUserEntity(id=username.encode(), name=username, display_name=username)
    users[username] = user

    options, state = server.register_begin(user, user_verification="preferred")
    session["fido2_state"] = state
    return jsonify(options)

@app.route('/register_complete', methods=['POST'])
def register_complete():
    credential = request.json["credential"]
    state = session.pop("fido2_state", None)

    auth_data = server.register_complete(
        state, 
        credential["clientDataJSON"],
        credential["attestationObject"]
    )

    users[credential["id"]] = auth_data.credential_data
    return jsonify({"status": "ok"})

@app.route('/authenticate_begin', methods=['POST'])
def authenticate_begin():
    username = request.json["username"]
    if username not in users:
        return jsonify({"error": "User not found"}), 404
    
    options, state = server.authenticate_begin([users[username]])
    session["fido2_auth_state"] = state
    return jsonify(options)

# TODO: Implement authenticate_complete
# TODO: Create a new file for app
