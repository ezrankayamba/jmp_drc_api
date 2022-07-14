from cryptography.fernet import Fernet

key = "7MrI4oXBM-d6Zgn6xN0h0iGycxAPeJOIwfCkDSH4JmU="


def new_key():
    return Fernet.generate_key()


def encrypt(message):
    fernet = Fernet(key)
    return fernet.encrypt(message.encode()).decode('utf-8')


def decrypt(enc_message):
    fernet = Fernet(key)
    return fernet.decrypt(enc_message.encode()).decode()
