# sentiment_model.py

import pickle
from pathlib import Path
from typing import Tuple, Optional
from config import MODEL_FILE, VECTORIZER_FILE

SENTIMENT_MAP = {
    1: "Positive",
    0: "Neutral",
    -1: "Negative"
}


class SentimentModelService:
    """Loads and predicts ML sentiment model."""

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self._is_loaded = False

    def load(self):
        """Loads model + vectorizer once."""
        if self._is_loaded:
            return

        with open(MODEL_FILE, "rb") as f:
            self.model = pickle.load(f)

        with open(VECTORIZER_FILE, "rb") as f:
            self.vectorizer = pickle.load(f)

        self._is_loaded = True

    def predict(self, text: str) -> Tuple[int, str]:
        """Returns (score, label)."""
        if not self._is_loaded:
            raise RuntimeError("Model not loaded")

        vector = self.vectorizer.transform([text])
        pred = int(self.model.predict(vector)[0])
        return pred, SENTIMENT_MAP[pred]


# ----------------------------
# Create SINGLE GLOBAL INSTANCE
# ----------------------------
sentiment_service = SentimentModelService()
sentiment_service.load()
