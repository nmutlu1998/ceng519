import pickle
import pandas as pd
import math
from collections import Counter

MAX_TOTAL_LENGTH = 253
MAX_LABEL_LENGTH = 63


class Detector:
    def __init__(self):
        with open('./models/random_forest_model.pkl', 'rb') as file:
            self.model = pickle.load(file)

    def calculate_entropy(self, s):
        if not s:
            return 0
        prob = [freq / len(s) for freq in Counter(s).values()]
        return -sum(p * math.log2(p) for p in prob)

    def uppercase_ratio(self, s):
        return sum(1 for c in s if c.isupper()) / len(s)

    def digit_ratio(self, s):
        return sum(1 for c in s if c.isdigit()) / len(s)

    def total_label_ratio(self, s):
        return len(s) / MAX_TOTAL_LENGTH

    def per_label_ratio(self, s):
        labels = s.split(".")
        return max(len(label) for label in labels) / MAX_LABEL_LENGTH

    def max_entropy(self, s):
        labels = s.split(".")
        entropies = [self.calculate_entropy(s)] + [self.calculate_entropy(label) for label in labels]
        return max(entropies)

    def predict(self, text):
        query = {
            'url_len': len(text),
            'uppercase_ratio': self.uppercase_ratio(text),
            'digit_ratio': self.digit_ratio(text),
            'total_label_ratio': self.total_label_ratio(text),
            'per_label_ratio': self.per_label_ratio(text),
            'entropy': self.max_entropy(text)
        }

        df = pd.DataFrame([query])
        return self.model.predict(df)[0]