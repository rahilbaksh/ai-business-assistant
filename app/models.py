from pydantic import BaseModel
from typing import List, Dict


class Document:
    def __init__(self, content: str, source: str = ""):
        self.content = content
        self.source = source

class BusinessInsight:
    def __init__(self, title: str, description: str, confidence: float):
        self.title = title
        self.description = description
        self.confidence = confidence

class ActionPlan:
    def __init__(self, title: str, steps: List[str]):
        self.title = title
        self.steps = steps
