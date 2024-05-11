from werkzeug.security import generate_password_hash, check_password_hash
from dataclasses import dataclass
from flask_login import UserMixin


@dataclass
class User(UserMixin):
    id: int
    login: str
    password_hash: str = None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if check_password_hash(self.password_hash, password):
            return self
