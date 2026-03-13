import json
import os

SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "subscriptions.json")

def load_subscriptions():
    if not os.path.exists(SUBSCRIPTIONS_FILE):
        return {}
    try:
        with open(SUBSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_subscription(chat_id, city):
    subscriptions = load_subscriptions()
    subscriptions[str(chat_id)] = city
    with open(SUBSCRIPTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(subscriptions, f, ensure_ascii=False, indent=2)

def remove_subscription(chat_id):
    subscriptions = load_subscriptions()
    if str(chat_id) in subscriptions:
        del subscriptions[str(chat_id)]
        with open(SUBSCRIPTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(subscriptions, f, ensure_ascii=False, indent=2)
        return True
    return False

def get_subscription(chat_id):
    subscriptions = load_subscriptions()
    return subscriptions.get(str(chat_id))

