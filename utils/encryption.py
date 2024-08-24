import base64
from cryptography.fernet import Fernet
import configparser

class Encryption:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.load_config()
        self.key = self.config['encryption']['key'].encode()

    def load_config(self):
        try:
            self.config.read(self.config_file)
            if 'encryption' not in self.config or 'key' not in self.config['encryption']:
                raise KeyError
        except KeyError:
            key = Fernet.generate_key()
            self.config['encryption'] = {'key': key.decode()}
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)

    def encrypt(self, message: str) -> str:
        fernet = Fernet(self.key)
        return fernet.encrypt(message.encode()).decode()

    def decrypt(self, encrypted_message: str) -> str:
        fernet = Fernet(self.key)
        return fernet.decrypt(encrypted_message.encode()).decode()
