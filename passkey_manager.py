from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    PublicKeyCredentialDescriptor,
)
import secrets
import json
from typing import Dict, List, Optional
import logging

class PasskeyManager:
    def __init__(self, rp_id: str = "localhost", rp_name: str = "PyQt App"):
        self.rp_id = rp_id
        self.rp_name = rp_name
        self.origin = f"http://{rp_id}"
        self.logger = logging.getLogger(__name__)
        
        # Temporär lagring (ersätt med din databas)
        self.users: Dict[str, dict] = {}
        self.credentials: Dict[bytes, dict] = {}

    def register_begin(self, username: str, display_name: Optional[str] = None) -> dict:
        """Initiera passkey-registrering"""
        user_id = secrets.token_hex(16)
        display_name = display_name or username
        
        self.users[user_id] = {
            'id': user_id,
            'name': username,
            'display_name': display_name
        }
        
        options = generate_registration_options(
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=user_id,
            user_name=username,
            user_display_name=display_name,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.PREFERRED
            )
        )
        
        return {
            'options': dict(options),
            'user_id': user_id,
            'challenge': options.challenge
        }

    def register_complete(self, user_id: str, credential: dict, challenge: bytes) -> bool:
        """Slutför registrering"""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        try:
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=challenge,
                expected_rp_id=self.rp_id,
                expected_origin=self.origin,
            )
            
            self.credentials[verification.credential_id] = {
                'id': verification.credential_id,
                'public_key': verification.credential_public_key,
                'user_id': user_id
            }
            return True
        except Exception as e:
            self.logger.error(f"Registration failed: {e}")
            return False

    def authenticate_begin(self, username: str) -> dict:
        """Initiera inloggning"""
        user = next((u for u in self.users.values() if u['name'] == username), None)
        if not user:
            raise ValueError("User not found")
        
        user_credentials = [
            cred for cred in self.credentials.values() 
            if cred['user_id'] == user['id']
        ]
        
        options = generate_authentication_options(
            rp_id=self.rp_id,
            allow_credentials=[
                PublicKeyCredentialDescriptor(id=cred['id']) 
                for cred in user_credentials
            ],
            user_verification=UserVerificationRequirement.PREFERRED,
        )
        
        return {
            'options': options,
            'challenge': options.challenge
        }

    def authenticate_complete(self, credential: dict, challenge: bytes) -> dict:
        """Slutför inloggning"""
        try:
            credential_id = credential.get('rawId')
            if credential_id not in self.credentials:
                raise ValueError("Invalid credential")
            
            stored_credential = self.credentials[credential_id]
            
            verify_authentication_response(
                credential=credential,
                expected_challenge=challenge,
                expected_rp_id=self.rp_id,
                expected_origin=self.origin,
                credential_public_key=stored_credential['public_key'],
            )
            
            return self.users[stored_credential['user_id']]
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            raise