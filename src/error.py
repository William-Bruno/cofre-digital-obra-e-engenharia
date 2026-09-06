class Missing(Exception):
    def __init__(self, msg:str = "Arquivo não encontrado"):
        self.msg = msg
        super().__init__(self.msg)

class Duplicate(Exception):
    def __init__(self, msg:str = "Arquivo duplicado"):
        self.msg = msg
        super().__init__(self.msg)

class FileConfigError(Exception):
    def __init__(self, msg:str = "Problema  nas configurações do arquivo"):
        self.msg = msg
        super().__init__(self, msg)

class FileTooLarge(Exception):
    def __init__(self, msg:str = "Arquivo enviado é muito grande"):
        self.sg = msg
        super().__init__(self,msg)

class InvalidFileName(Exception):
    def __init__(self, msg:str = "Arquivo não possui nome"):
        self.msg = msg
        super().__init__(self, msg)

class InvalidJSONError(Exception):
    def __init__(self, msg:str = "Arquivo JSON é invalido ou está corrompido"):
        self.msg = msg
        super().__init__(self, msg)

class ServerError(Exception):
    def __init__(self, msg:str = "Erro interno no servidor"):
        self.msg = msg
        super().__init__(self, msg)

