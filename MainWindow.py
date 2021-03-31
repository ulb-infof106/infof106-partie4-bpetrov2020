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


class WinnerMsg(QMessageBox):

    def __init__(self, winning_text = '', parent=None):
        super().__init__(parent)
        self.setWindowTitle("La partie est finie !")
        self.setText(winning_text)
        self.exec_()


class BeginError(QMessageBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("La partie n'a pas pu commencer")
        self.setIcon(QMessageBox.Warning)

class NoFileError(BeginError):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Aucun fichier de configuration n'a été chargé.")
        # self.setDetailedText("Un fichier de configuration est nécessaire pour commencer la partie. Il doit contenir :\n\n"
        #                      "- une ligne spécifiant la taille du plateau de jeu;\n"
        #                      "- une ligne spécifiant les positions des reines blanches;\n"
        #                      "- une ligne spécifiant les positions des reines noires;\n"
        #                      "(- une ligne spécifiant les positions des flèches.)")
        self.exec_()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()  # initialiser QMainWindow

        self.layout = QVBoxLayout()
        self.path = ''

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
        print(self.path)

    def begin_game(self, path):
        """Démarre une partie de jeu."""
        if self.path == '':
            NoFileError(self)
            return
        # self.game = Amazons(self.path)

        if not self.board_outer_layout.isEmpty():
            child = self.board_outer_layout.takeAt(0)
            self.board_outer_layout.removeWidget(child.widget())

        self.board_widget = QWidget()
        self.board_ui = BoardUI(Amazons(self.path), self)
        self.board_widget.setLayout(self.board_ui)
        self.board_outer_layout.addWidget(self.board_widget)

        self.board_ui.next_turn()

    def resizeEvent(self, QResizeEvent):
        geo = self.board_outer_layout.geometry()
        print(geo.width(), geo.height())
        # print(self.boardUI.itemAtPosition(5,6).geometry().x())
        if geo.width() < geo.height():
            # geo.setHeight(geo.width())
            # self.boardUI.setGeometry(geo)
            self.board_outer_layout.itemAt(0).widget().setMaximumHeight(geo.width())
            self.board_outer_layout.itemAt(0).widget().setMaximumWidth(geo.width())
            # self.widget.setMaximumWidth(geo.width())
        elif geo.width() > geo.height():
        #     # geo.setWidth(geo.height())
        #     # geo.setX(self.width()/2)
        #     # self.boardUI.setGeometry(geo)
            self.board_outer_layout.itemAt(0).widget().setMaximumWidth(geo.height())
            self.board_outer_layout.itemAt(0).widget().setMaximumHeight(geo.height())
        #     # self.widget.setMaximumWidth(geo.height())
        #     # self.widget.setMaximumHeight(geo.height())
        # else:
        #     self.widget.setMaximumWidth(geo.height())
        #     self.widget.setMaximumHeight(geo.width())

            
class GridRow(QHBoxLayout):

    def __init__(self, parent=None):
        super().__init__(parent)

    def __getitem__(self, index):
        return self.itemAt(index).widget()

    def __iter__(self):
        for i in range(len(self)):
            yield self.itemAt(i).widget()

    def __len__(self):
        return self.count()


class BoardUI_(QBoxLayout):

    def __init__(self, parent=None):
        super().__init__(QBoxLayout.BottomToTop, parent)



class BoardUI(QGridLayout):

    def __init__(self, game, parent=None):
        super().__init__(parent)

        self.current_player_idx = 1

        self.game = game
        # self.board = self.game.board
        self.N = self.game.board.N

        self.setSpacing(0)
        self.setAlignment(Qt.AlignCenter)

        self.cells = QButtonGroup()
        self.cells.buttonClicked.connect(self.add_action)
        self.cells.setExclusive(True)

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
        WinnerMsg(self.game.show_winner())


    def human_turn_end(self):
        """Le tour du joueur humain se finit peut-être."""
        print(f'{self.action[0].str_}>{self.action[1].str_}>{self.action[2].str_}')
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
            for cell in self:
                cell.setDown(state)
                cell.setEnabled(state)
        else:
            for cell in self:
                print(cell.id_)
                # if cell.id_ in (0, 1):
                print(type(cell))
                cell.setEnabled(state)

    # def user_action(self):
    #     """Fontion qui renvoir le coup joué par un utilisateur humain."""
    #     self.action = []
    #     self.timer = QTimer()
    #     print()
    #     QTimer()
    #         QTime
    #         pass
    #     return f'{self.action[0].str_}>{self.action[1].str_}>{self.action[2].str_}'

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
        if not isinstance(pos, Pos2D):
            raise TypeError(f"{pos} n'est pas une instance de Pos2D.")
        return self.itemAtPosition(-(pos.row-self.N+1), pos.col).widget()


class Cell(QPushButton):
    """Case de la gui du plateau.

    Args:
        light(int): 0 pour une case claire, 1 pour une sombre
        row(int): rangée
        column(int): colonne

    Attributes:
    """

    def __init__(self, light=0, row=0, column=0):
        super().__init__()
        self.setMinimumWidth(30)
        self.setMinimumHeight(30)

        self.setEnabled(False)

        self.coord = Pos2D(row, column)
        self.id_ = 2  # empty

        self.setCheckable(True)
        self.setFlat(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.token_slot = QHBoxLayout(self)
        self.token = Token("")
        self.token_slot.addWidget(self.token)

        if light:
            self.setStyleSheet("QPushButton:flat {background-color:#d2cba8; border: none}\
                                QPushButton:checked{border:5px solid #827e68 }\
                                QPushButton:disabled{foreground-color:none}")
        else:
            self.setStyleSheet("QPushButton:flat {background-color:#463c26; border:none}\
                                QPushButton:checked{border:5px solid #827e68 }\
                                QPushButton:disabled{foreground-color:none}")

    def set_token(self, path):
        """
        Args:
            path(str): chemin vers l'image du pion qui est mis sur la case
        """
        if not isinstance(path, str):
            raise TypeError(f"{path} n'est pas un string.")
        self.id_ = PATHS.index(path)
        self.token.setPixmap(QPixmap(path))
        self.token.repaint()


class Token(QLabel):
    """Représente un pion.

    Args:
        filename(str): fichier image du pion
    """

    def __init__(self, path):
        super().__init__()

        self.setScaledContents(True)
        self.setPixmap(QPixmap(path))

        margin = 3
        self.setContentsMargins(margin, margin, margin, margin)

        self.setStyleSheet("QLabel:disabled{color: none;background-color:none;foreground-color:none}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.exit(app.exec_())
