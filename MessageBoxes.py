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

class LoadFileError(QMessageBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Erreur au chargement du fichier")
        self.setIcon(QMessageBox.Warning)

class NoFileError(LoadFileError):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Aucun fichier de configuration n'a été chargé.")
        self.exec_()

class InvalidFormatErrorMsg(LoadFileError):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Une erreur est survenue lors de la lecture du fichier.")
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

class QuitMessage(QMessageBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quitter le jeu")
        self.setText("Voulez-vous sauvegarder votre partie avant de quitter ?")
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.Cancel | QMessageBox.Save | QMessageBox.Discard)
# class SaveError(QMessageBox):
# 
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Erreur à la sauvegarde du fichier")
#         self.setIcon(QMessageBox.Warning)
#         self.setText("Impossible de sauvegarder un partie qui n'a pas encore commencée...")
#         self.exec_()
