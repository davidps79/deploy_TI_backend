from typing import Dict

from experta import KnowledgeEngine
from abc import ABC, abstractmethod


class Expert(KnowledgeEngine):
    @abstractmethod
    def input_data(self, input_json):
        pass

    @abstractmethod
    def get_recommendations(self) -> Dict[str, str]:
        pass
