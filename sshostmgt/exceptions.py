# errors

class NoSuchHost(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class NoSuchField(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class FormatError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
