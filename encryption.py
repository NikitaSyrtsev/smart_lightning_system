from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv('config.env')

# Получение ключа шифрования
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
cipher = Fernet(ENCRYPTION_KEY)

# Функция для шифрования данных
def encrypt_data(data):
    return cipher.encrypt(data.encode())

# Функция для расшифровки данных
def decrypt_data(encrypted_data):
    return cipher.decrypt(encrypted_data).decode()

