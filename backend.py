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

