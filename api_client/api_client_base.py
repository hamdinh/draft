# api_client_base.py
from abc import ABC, abstractmethod


class APIClientBase(ABC):
    @abstractmethod
    def get(self, endpoint):
        pass

    @abstractmethod
    def post(self, endpoint, data):
        pass

    @abstractmethod
    def put(self, endpoint, data):
        pass

    @abstractmethod
    def delete(self, endpoint):
        pass
