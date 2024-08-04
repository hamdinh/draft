# token_manager.py
from datetime import datetime, timedelta
from threading import Lock

import requests


class TokenManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TokenManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "token"):  # Initialize only once
            self.token = None
            self.token_expires_at = None

    def fetch_token(self, config):
        response = requests.post(
            config.token_url,
            data={
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "grant_type": "client_credentials",
            },
        )
        response.raise_for_status()
        token_data = response.json()
        self.token = token_data.get("access_token")
        self.token_expires_at = datetime.now() + timedelta(
            hours=24
        )  # Assuming the token is valid for 24 hours

    def get_token(self, config):
        if self.token is None or datetime.now() >= self.token_expires_at:
            self.fetch_token(config)
        return self.token
