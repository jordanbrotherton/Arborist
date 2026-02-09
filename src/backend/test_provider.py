import json
from typing import List
from .deployment import Deployment
from .atomic_provider import AtomicProvider


class TestProvider(AtomicProvider):
    def __init__(self, json_path):
        self.json_path = json_path

    def get_deployments(self) -> List[Deployment]:
        with open(self.json_path, 'r') as file:
            data = json.load(file)

        return [
            Deployment(
                id=item['id'],
                checksum=item['checksum'],
                version=item['version'],
                osname=item['osname'],
                booted=item.get('booted', False),
                staged=item.get('staged', False),
                pinned=item.get('pinned', False)
            ) for item in data['deployments']
        ]
