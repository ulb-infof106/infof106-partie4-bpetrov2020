from PyQt5.QtWidgets import QMessageBox

class WinnerMsg(QMessageBox):

    def __init__(self, winning_text = '', parent=None):
        super().__init__(parent)
        self.setWindowTitle("La partie est finie !")
        self.setText(winning_text)
        self.exec_()


class StopGame(QMessageBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quitter la partie")
        self.setText("Vous êtes sur le point de quitter la partie. Continuer ?")
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)


class BeginError(QMessageBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("La partie n'a pas pu commencer")
        self.setIcon(QMessageBox.Warning)


class NoFileError(BeginError):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Aucun fichier de configuration n'a été chargé.")
        self.exec_()


class NotEnoughTokens(BeginError):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Il n'y a pas assez de pions sur le plateau pour commencer la partie.")
        self.exec_()


class OneSizeBoard(BeginError):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Mais comment voulez-vous jouer avec seulement une case !?")
        self.exec_()
