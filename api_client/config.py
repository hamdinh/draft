# config.py
class Config:
    def __init__(self, base_url, token_url, client_id, client_secret):
        self.base_url = base_url
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret


PROD_CONFIG = Config(
    base_url="https://api.production.com",
    token_url="https://auth.production.com/token",
    client_id="prod_client_id",
    client_secret="prod_client_secret",
)

NON_PROD_CONFIG = Config(
    base_url="https://api.nonprod.com",
    token_url="https://auth.nonprod.com/token",
    client_id="non_prod_client_id",
    client_secret="non_prod_client_secret",
)
