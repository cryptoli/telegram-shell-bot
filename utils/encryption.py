import base64
from cryptography.fernet import Fernet
import configparser

class Encryption:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.load_config()
        self.key = self.config['encryption']['key'].encode()
        self.validate_or_generate_key()

    def load_config(self):
        try:
            self.config.read(self.config_file)
            if 'encryption' not in self.config or 'key' not in self.config['encryption']:
                raise KeyError
        except KeyError:
            self.generate_and_save_key()

    def validate_or_generate_key(self):
        try:
            # 尝试创建 Fernet 对象以验证密钥是否有效
            Fernet(self.key)
        except Exception:
            print("无效的密钥，正在生成新的密钥...")
            self.generate_and_save_key()

    def generate_and_save_key(self):
        # 生成新密钥
        new_key = Fernet.generate_key()
        self.config['encryption'] = {'key': new_key.decode()}
        # 将新密钥保存到配置文件中
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        self.key = new_key
        print("新密钥已生成并保存到配置文件。")

    def encrypt(self, message: str) -> str:
        fernet = Fernet(self.key)
        return fernet.encrypt(message.encode()).decode()

    def decrypt(self, encrypted_message: str) -> str:
        fernet = Fernet(self.key)
        return fernet.decrypt(encrypted_message.encode()).decode()
