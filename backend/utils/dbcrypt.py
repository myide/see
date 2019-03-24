# -*- coding: utf-8 -*-
from cryptography.fernet import Fernet

class prpcrypt:

    key = 'P30cMRRBa9kF3YNYpeKNmlUquLsX6ssOuBdy4yZe8wU='

    @classmethod
    def encrypt(cls, password):
        fn = Fernet(cls.key)
        password_encode = password.encode()
        token = fn.encrypt(password_encode)
        return token.decode()

    @classmethod
    def decrypt(cls, password):
        fn = Fernet(cls.key)
        password_encode = password.encode()
        token = fn.decrypt(password_encode)
        return token.decode()
