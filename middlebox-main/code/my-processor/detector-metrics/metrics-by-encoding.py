import base64
import codecs
import random
import string
from sklearn.metrics import precision_score, recall_score, f1_score
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.detector import Detector

ml_model = Detector()

import random

def generate_random_domain(subdomain_parts):
    popular_domains = [
        "google.com", "youtube.com", "facebook.com", "amazon.com", "wikipedia.org",
        "twitter.com", "instagram.com", "linkedin.com", "netflix.com", "microsoft.com",
        "apple.com", "whatsapp.com", "tiktok.com", "cloudflare.com", "reddit.com",
        "yahoo.com", "bing.com", "zoom.us", "dropbox.com", "paypal.com",
        "github.com", "stackoverflow.com", "quora.com", "office.com", "adobe.com",
        "mozilla.org", "cnn.com", "espn.com", "bbc.co.uk", "nytimes.com"
    ]

    domain = random.choice(popular_domains)
    return ".".join(subdomain_parts) + "." + domain



def generate_random_subdomain(encoding, encoded=False):
    words = ['mail', 'login', 'blog', 'cdn', 'www', 'img', 'video', 'auth', 'user', 'data']
    encodings = ['base64', 'hex', 'rot13']

    def random_token(length=6):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def encode_string_randomly(s):
        method = encoding
        if encoding == 'random':
            method = random.choice(encodings)
        return encode_string(s, method)

    subdomain_parts = []

    num_parts = random.randint(1, 4)

    for _ in range(num_parts):
        if encoded and random.random() < 0.8:
            raw = random_token(random.randint(6, 12))
            encoded_part = encode_string_randomly(raw)
            subdomain_parts.append(encoded_part)
        else:
            if random.random() < 0.5:
                subdomain_parts.append(random.choice(words))
            else:
                subdomain_parts.append(random_token(random.randint(4, 10)))

    return generate_random_domain(subdomain_parts)


def model_predict(domain):
    return ml_model.predict(domain)

# Encoding helpers
def encode_string(s, method):
    if method == 'base64':
        return base64.urlsafe_b64encode(s.encode()).decode()
    elif method == 'hex':
        return s.encode().hex()
    elif method == 'rot13':
        return codecs.encode(s, 'rot_13')
    else:
        return s

def generate_dataset(encoding, n=100):
    data = []
    for _ in range(n):
        is_encoded = random.choice([0, 1])
        subdomain = generate_random_subdomain(encoding, encoded=is_encoded)
        label = 1 if is_encoded else 0
        data.append((subdomain, label))
    return data


def evaluate_model(data, model_predict):
    y_true = []
    y_pred = []

    for domain, label in data:
        pred = model_predict(domain)
        y_true.append(label)
        y_pred.append(pred)

    tp = sum((yt == 1 and yp == 1) for yt, yp in zip(y_true, y_pred))
    tn = sum((yt == 0 and yp == 0) for yt, yp in zip(y_true, y_pred))
    fp = sum((yt == 0 and yp == 1) for yt, yp in zip(y_true, y_pred))
    fn = sum((yt == 1 and yp == 0) for yt, yp in zip(y_true, y_pred))

    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    print(f"TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall:    {recall:.2f}")
    print(f"F1-Score:  {f1:.2f}")

# Run it
if __name__ == "__main__":
    test_data = generate_dataset('random', 10000)
    print("=== Evaluation Results on Random Encoding ===")
    evaluate_model(test_data, model_predict)

    # evaluation on base64 encoded data
    test_data_base64 = generate_dataset('base64', 10000)
    print("=== Evaluation Results on Base64 Encoding ===")
    evaluate_model(test_data_base64, model_predict)

    # evaluation on hex encoded data
    test_data_hex = generate_dataset('hex', 10000)
    print("=== Evaluation Results on Hex Encoding ===")
    evaluate_model(test_data_hex, model_predict)

    # evaluation on rot13 encoded data
    test_data_rot = generate_dataset('rot13', 10000)
    print("=== Evaluation Results on rot13 Encoding ===")
    evaluate_model(test_data_rot, model_predict)



