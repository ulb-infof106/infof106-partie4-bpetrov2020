from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import time

from amazons import Amazons
from pos2d import Pos2D
from const import *
from players import HumanPlayer
from exceptions import *

from MessageBoxes import *


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()  # initialiser QMainWindow

        self.layout = QVBoxLayout()
        self.path = ''

        self.resize(700, 800)

        self.load_button = QPushButton("Charger un fichier")
        self.load_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_button)

        self.board_widget = QWidget()  # widget factice du plateau
        self.board_outer_layout = QHBoxLayout()  # pour pouvoir centrer le plateau
        self.board_outer_layout.setAlignment(Qt.AlignCenter)
        self.board_outer_layout.addWidget(self.board_widget)
        self.layout.addLayout(self.board_outer_layout)

        self.begin_button = QPushButton("Commencer la partie")
        self.begin_button.clicked.connect(self.begin_game)
        self.layout.addWidget(self.begin_button)

        self.widget = QWidget()  # widget factice
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.show()

    def load_file(self):
        self.path = QFileDialog.getOpenFileName(None,
                                                "Charger un fichier",
                                                "",
                                                "Fichier de configuration (.txt)")[0]

    def begin_game(self, path):
        """Démarre une partie de jeu."""
        if self.path == '':
            NoFileError(self)
            return

        self.begin_button.setText("Recommencer")
        self.begin_button.clicked.disconnect()  # ne pas avoir la connection précédente
        self.begin_button.clicked.connect(self.stop_game)

        if not self.board_outer_layout.isEmpty():  # si partie déjà en cours
            child = self.board_outer_layout.takeAt(0)
            self.board_outer_layout.removeWidget(child.widget())

        self.board_widget = QWidget()
        self.board_ui = BoardUI(Amazons(self.path, HUMAN, HUMAN), self)
        self.board_widget.setLayout(self.board_ui)
        self.board_outer_layout.addWidget(self.board_widget)

        self.board_ui.next_turn()

    def stop_game(self):
        out = StopGame(self).exec_()
        print(out)
        if out == 16384:  # valeur retournée pour un oui
            print("yes")
            self.board_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.begin_button.setText("Commencer la partie")
            self.begin_button.clicked.disconnect()
            self.begin_button.clicked.connect(self.begin_game)
        else:
            pass
            print("no")

    def resizeEvent(self, QResizeEvent=None):
        geo = self.board_outer_layout.geometry()
        diff = abs(geo.width()-geo.height())
        print(diff/2)
        # print(geo.width(), geo.height())
        if geo.width() < geo.height():
            # self.board_widget.setMaximumHeight(geo.width())
            # self.board_widget.setMaximumWidth(geo.width())
            self.board_outer_layout.setContentsMargins(0, diff/2, 0, diff/2)
        elif geo.width() > geo.height():
            # self.board_widget.setMaximumWidth(geo.height())
            # self.board_widget.setMaximumHeight(geo.height())
            self.board_outer_layout.setContentsMargins(diff/2, 0, diff/2, 0)

            



class BoardUI(QGridLayout):

    def __init__(self, game, parent=None):
        super().__init__(parent)

        self.current_player_idx = 1  # deuxième joueur, va être changé dans next_turn()

        self.game = game
        self.N = self.game.board.N

        self.setSpacing(0)
        self.setAlignment(Qt.AlignCenter)

        self.cells = QButtonGroup()
        self.cells.buttonClicked.connect(self.add_action)

        for i in range(self.N):
            for j in range(self.N):
                cell = Cell((i+j)%2, -(j-self.N+1), i)
                # cell.clicked.connect(self.add_action)
                self.cells.addButton(cell)
                self.addWidget(cell, j,i)

    def next_turn(self):
        """Joue le prochain tour, humain ou ordinateur."""
        self.update_ui()  # mettre à jour la gui
        self.current_player_idx = 1-self.current_player_idx  # passer au joueur suivant
        if self.game.is_over():
            self.declare_winner()
        else:
            # joueur actuel joue
            self.current_player = self.game.players[self.current_player_idx]
            if isinstance(self.current_player, HumanPlayer):
                self.human_turn_begin()
            else:
                self.current_player.play()
                self.next_turn()

    def add_action(self, action):
        self.action.append(action.coord)
        print(action.coord, self.action)
        if len(self.action) == 3:
            print("in")
            self.human_turn_end()

    def declare_winner(self):
        WinnerMsg(self.game.show_winner(), self.parent())


    def human_turn_end(self):
        """Le tour du joueur humain se finit peut-être."""
        self.current_player.play(f'{self.action[0].str_}>{self.action[1].str_}>{self.action[2].str_}')
        self.set_state(False)
        self.next_turn()

    def human_turn_begin(self):
        """Le tour du joueur humain commence."""
        self.action = []
        self.set_state(True)

    def set_state(self, state=True):
        """Active et désactive le plateau de jeu.

            Le plateau est activé lorsque c'est à un joueur humain de jouer,
        sinon, il est désactivé.

        Args:
            state(bool): True s'il faut activer
        """
        if not state:
            # self.cells.checkedButton().setChecked(False)
            self.cells.setExclusive(False)
            for cell in self:
                cell.setChecked(False)
                cell.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        else:
            # self.parent().setAttribute(Qt.WA_TransparentForMouseEvents)
            self.cells.setExclusive(True)
            for cell in self:
                # print(cell.id_)
                # if cell.id_ in (0, 1):
                # print(type(cell))
                cell.setAttribute(Qt.WA_TransparentForMouseEvents, False)

    def update_ui(self):
        """Met à jour la gui du plateau."""
        for cell in self:
            # print(cell)
            # print(self.board.grid[cell.coord])
            path = PATHS[self.game.board.grid[cell.coord]]
            # print(path)
            cell.set_token(path)

    def __iter__(self):
        """Itération sur toutes les cases de la gui de la grille."""
        for i in range(self.N):
            for j in range(self.N):
                # print(self[Pos2D(i, j)])
                yield self[Pos2D(i, j)]

    def __getitem__(self, pos):
        """Renvoir l'item la position en paramètre.

        Args:
            pos(Pos2D): position demandée"""
        return self.itemAtPosition(-(pos.row-self.N+1), pos.col).widget()


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
        self.setMinimumWidth(30)
        self.setMinimumHeight(30)

        self.coord = Pos2D(row, column)
        self.id_ = 2  # empty

        self.setCheckable(True)
        self.setFlat(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.token_slot = QHBoxLayout(self)  # là où se pose le pion
        self.token = Token("")
        self.token_slot.addWidget(self.token)

        if light:
            self.setStyleSheet("QPushButton:flat {background-color:#d2cba8; border: none}\
                                QPushButton:checked{border:5px solid #827e68 }")
        else:
            self.setStyleSheet("QPushButton:flat {background-color:#463c26; border:none}\
                                QPushButton:checked{border:5px solid #827e68 }")

    def set_token(self, path):
        """
        Args:
            path(str): chemin vers l'image du pion qui est mis sur la case
        """
        self.id_ = PATHS.index(path)
        self.token.setPixmap(QPixmap(path))
        self.token.repaint()  # avoir un retour immédiat de l'action


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.exit(app.exec_())


# class GridRow(QHBoxLayout):
# 
#     def __init__(self, parent=None):
#         super().__init__(parent)
# 
#     def __getitem__(self, index):
#         return self.itemAt(index).widget()
# 
#     def __iter__(self):
#         for i in range(len(self)):
#             yield self.itemAt(i).widget()
# 
#     def __len__(self):
#         return self.count()
# 
# 
# class BoardUI_(QBoxLayout):
# 
#     def __init__(self, parent=None):
#         super().__init__(QBoxLayout.BottomToTop, parent)
