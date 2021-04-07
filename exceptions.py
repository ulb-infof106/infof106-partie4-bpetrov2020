"""
Prénom: Boris
Nom: Petrov
Matricule: 000515795
"""

class InvalidFormatError(SyntaxError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class InvalidPositionError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class InvalidActionError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
