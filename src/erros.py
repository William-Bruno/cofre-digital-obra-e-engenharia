class Vazio(Exception):
    def __init__(self, msg:str):
        self.msg = msg

class Duplicado(Exception):
    def __init__(self, msg:str):
        self.msg