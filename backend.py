import base64
from flask import Flask, request, jsonify, session
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialDescriptor, PublicKeyCredentialUserEntity
from fido2.webauthn import AttestationObject, AuthenticatorData, CollectedClientData
#from fido2.ctap2 import AttestedCredentialData
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Dummy user and credential storage
users = {}
credentials = {}

# Relying Party (RP) information
rp = {
    "id": "localhost",
    "name": "Passkey App"
}

# Fido2 server
server = Fido2Server(rp)

# Helper functions for base64url encoding/decoding
def base64url_to_bytes(base64url_string):
    return base64.urlsafe_b64decode(base64url_string + "==")

def bytes_to_base64url(byte_string):
    return base64.urlsafe_b64encode(byte_string).rstrip(b'=').decode('utf-8')

@app.route('/')
def index():
    return jsonify({"status": "Server is running"})

@app.route('/register', methods=['GET'])
def register():
    # Create a dummy user for registration
    user_id = str(uuid.uuid4()).encode()  # Generate a unique user ID
    user_name = "example_user"
    display_name = "Example User"
    user = PublicKeyCredentialUserEntity(id=user_id, name=user_name, display_name=display_name)
    users[user_id] = user

    # Generate WebAuthn registration challenge
    options, state = server.register_begin(user, user_verification="preferred")
    session['state'] = bytes_to_base64url(state)

    # Return the challenge to the client
    return jsonify(options)

@app.route('/complete_registration', methods=['POST'])
def complete_registration():
    data = request.json
    state = base64url_to_bytes(session['state'])

    try:
        # Complete the registration process
        attestation_object = AttestationObject(base64url_to_bytes(data['attestationObject']))
        client_data = CollectedClientData(base64url_to_bytes(data['clientDataJSON']))
        auth_data = server.register_complete(state, client_data, attestation_object)

        # Store the credential for the user
        user_id = list(users.keys())[0]  # Assuming a single user for simplicity
        credentials[user_id] = auth_data.credential

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/login', methods=['GET'])
def login():
    # Generate WebAuthn authentication challenge
    user_id = list(users.keys())[0]  # Assuming a single user for simplicity
    user_credentials = [PublicKeyCredentialDescriptor(cred_id=credentials[user_id].credential_id)]
    options, state = server.authenticate_begin(user_credentials, user_verification="preferred")
    session['state'] = bytes_to_base64url(state)

    # Return the challenge to the client
    return jsonify(options)

@app.route('/complete_login', methods=['POST'])
def complete_login():
    data = request.json
    state = base64url_to_bytes(session['state'])

    try:
        # Complete the login process
        credential_id = base64url_to_bytes(data['credentialId'])
        client_data = CollectedClientData(base64url_to_bytes(data['clientDataJSON']))
        auth_data = AuthenticatorData(base64url_to_bytes(data['authenticatorData']))
        signature = base64url_to_bytes(data['signature'])

        user_id = list(users.keys())[0]  # Assuming a single user for simplicity
        server.authenticate_complete(
            state,
            credentials[user_id].credential_public_key,
            auth_data,
            client_data,
            signature
        )

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)