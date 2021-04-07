from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pos2d import *
from const import *


class GridUI(QBoxLayout):
    """GUI d'un plateau de jeu.

    Args:
        size(int): taille du plateau
        parent(QWidget): père du plateau
    """

    def __init__(self, board, parent=None):
        super().__init__(QBoxLayout.BottomToTop, parent)

        self.setContentsMargins(0,0,0,0)
        self.setSpacing(0)

        self.cells = QButtonGroup()
        # self.cells.buttonClicked.connect(self.parent().add_action)

        for i in range(board.N):
            row = GridRow()
            for j in range(board.N):
                cell = Cell((i+j)%2, i, j)
                cell.set_token(TOKENS[board.grid[Pos2D(i, j)]])
                self.cells.addButton(cell)
                row.addWidget(cell)
            self.addLayout(row)

    def __getitem__(self, index):
        return self.itemAt(index)

    def __setitem__(self, index, token):
        if isinstance(index, Pos2D):
            self[index.row][index.col] = token
        else:
            raise TypeError

    def __iter__(self):
        for i in range(len(self)):
            yield self.itemAt(i)

    def __len__(self):
        return self.count()

    def set_disabled(self, state=True):
        """Une grille désactivée n'accepte aucune entrée de l'utilisateur."""
        for row in self:
            for col in row:
                col.setAttribute(Qt.WA_TransparentForMouseEvents, state)


class GridRow(QHBoxLayout):
    """Une rangée du plateau de jeu."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0,0,0,0)

    def __getitem__(self, index):
        return self.itemAt(index).widget()

    def __setitem__(self, index, token):
        # print(token, self[index].coord)
        self[index].set_token(token)

    def __iter__(self):
        for i in range(len(self)):
            yield self.itemAt(i).widget()

    def __len__(self):
        return self.count()



class Cell(QPushButton):
    """Case de la gui du plateau.

    Args:
        light(int): 0 pour une case claire, 1 pour une sombre
        row(int): rangée
        column(int): colonne

    Attributes:
        coord(Pos2D): coordonées de la cellule
        id_(int): id du pion qui s'y trouve (ou qui ne s'y trouve pas) -> voir const.py
    """

    def __init__(self, light=0, row=0, column=0):
        super().__init__()
        self.setMinimumWidth(10)
        self.setMinimumHeight(10)

        # self.coord = Pos2D(row, column)
        self.coord_str = f'{chr(column+97)}{row+1}'
        self.id_ = 2  # empty
        self.light = light

        self.setCheckable(True)
        self.setFlat(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.token_slot = QHBoxLayout(self)  # là où se pose le pion
        self.token = Token(TOKENS[EMPTY])
        self.token_slot.addWidget(self.token)

        if light:
            self.setStyleSheet(":flat {background-color:#d2cba8; border: none}\
                                :checked{border:5px solid #827e68 }")
        else:
            self.setStyleSheet(":flat {background-color:#463c26; border:none}\
                                :checked{border:5px solid #827e68 }")

    def set_token(self, path):
        """
        Args:
            path(str): chemin vers l'image du pion qui est mis sur la case
        """
        self.id_ = TOKENS.index(path)
        self.token.setPixmap(QPixmap(path))
        self.token.repaint()  # avoir un retour immédiat de l'action

    def highlight(self, state=True):
        """Pour mettre en valeur les cases où l'on peut jouer.

        Args:
            state(bool): True s'il faut mettre en valeur la case
        """
        if state:
            if self.light != 0:
                self.setStyleSheet(":flat {background-color:#d2cba8; border: 5px solid #ffff64}\
                                    :checked{border:5px solid #827e68 }")
            else:
                self.setStyleSheet(":flat {background-color:#463c26; border: 5px solid #ffff00}\
                                    :checked{border:5px solid #827e68 }")
        else:
            if self.light:
                self.setStyleSheet(":flat {background-color:#d2cba8; border: none}\
                                    :checked{border:5px solid #827e68 }")
            else:
                self.setStyleSheet(":flat {background-color:#463c26; border: none}\
                                    :checked{border:5px solid #827e68 }")


class Token(QLabel):
    """Représente un pion.

    Args:
        filename(str): fichier image du pion
    """

    def __init__(self, path):
        super().__init__()

        self.setScaledContents(True)  # pour s'adapter à la taille de la case
        self.setPixmap(QPixmap(path))

        margin = 3
        self.setContentsMargins(margin, margin, margin, margin)
