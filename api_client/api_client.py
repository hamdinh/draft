# api_client.py
import requests
from api_client_base.py import APIClientBase

from token_manager import TokenManager


class APIClient(APIClientBase):
    def __init__(self, config):
        self.config = config
        self.token_manager = TokenManager()

    def get_headers(self):
        token = self.token_manager.get_token(self.config)
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def handle_response(self, response):
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:  # Unauthorized, token might be invalid
                self.token_manager.fetch_token(self.config)
                raise Exception(
                    "Token expired and re-fetched, please retry the request."
                )
            else:
                raise Exception(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            raise Exception(f"Request error occurred: {req_err}")
        except Exception as err:
            raise Exception(f"An error occurred: {err}")

    def get(self, endpoint):
        url = f"{self.config.base_url}/{endpoint}"
        response = requests.get(url, headers=self.get_headers())
        return self.handle_response(response)

    def post(self, endpoint, data):
        url = f"{self.config.base_url}/{endpoint}"
        response = requests.post(url, json=data, headers=self.get_headers())
        return self.handle_response(response)

    def put(self, endpoint, data):
        url = f"{self.config.base_url}/{endpoint}"
        response = requests.put(url, json=data, headers=self.get_headers())
        return self.handle_response(response)

    def delete(self, endpoint):
        url = f"{self.config.base_url}/{endpoint}"
        response = requests.delete(url, headers=self.get_headers())
        return self.handle_response(response)
