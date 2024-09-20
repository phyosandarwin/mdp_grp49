import random
import time

def get_random_message():
    messages = [
        "Hello from Raspberry Pi",
        "Random message 1",
        "Another random message",
        "Message from model.py",
        "This is a periodic random message"
    ]
    time.sleep(2)  # Simulate a periodic delay
    return random.choice(messages)
