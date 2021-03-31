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
from grid_ui import GridUI

from MessageBoxes import *


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()  # initialiser QMainWindow

        self.layout = QVBoxLayout()
        self.path = ''

        self.resize(700, 800)

        self.player1 = self.player_type("blanc")
        self.layout.addLayout(self.player1)
        self.player2 = self.player_type("noir")
        self.layout.addLayout(self.player2)

        self.load_button = QPushButton("Charger un fichier")
        self.load_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_button)

        self.board_widget = QWidget()  # widget factice du plateau
        self.board_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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

    def player_type(self, couleur):
        layout = QFormLayout()
        layout.setFormAlignment(Qt.AlignCenter)

        layout.combo = QComboBox()
        layout.combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.combo.addItems(["Humain", "Ordinateur"])

        layout.addRow(f"Joueur {couleur} :", layout.combo)
        return layout

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

        # self.board_widget = QWidget()
        # self.board_ui = BoardUI(Amazons(self.path, HUMAN, HUMAN), self)
        # self.board_widget.setLayout(self.board_ui)
        self.board_widget = BoardUI(Amazons(self.path,
                                            self.player1.combo.currentIndex(),
                                            self.player2.combo.currentIndex()),
                                    self)
        self.board_outer_layout.addWidget(self.board_widget)

        self.board_widget.next_turn()

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
        if geo.width() < geo.height():
            self.board_outer_layout.setContentsMargins(0, int(diff/2), 0, int(diff/2))
        elif geo.width() > geo.height():
            self.board_outer_layout.setContentsMargins(int(diff/2), 0, int(diff/2), 0)


class BoardUI(QWidget):

    def __init__(self, game, parent=None):
        super().__init__(parent)

        self.game = game
        self.grid_ui = GridUI(self.game.board)
        self.grid_ui.cells.buttonClicked.connect(self.add_action)
        self.setLayout(self.grid_ui)

        self.current_player_idx = 1  # deuxième joueur, va être changé dans next_turn()

        # self.N = self.game.board.N

    def next_turn(self):
        """Joue le prochain tour, humain ou ordinateur."""
        self.current_player_idx = 1-self.current_player_idx  # passer au joueur suivant
        if self.game.is_over():
            self.declare_winner()
        else:
            # joueur actuel joue
            self.current_player = self.game.players[self.current_player_idx]
            if isinstance(self.current_player, HumanPlayer):
                self.human_turn_begin()
            else:
                action = self.current_player.play()
                self.update_from_action(action)
                self.next_turn()

    def human_turn_begin(self):
        """Le tour du joueur humain commence."""
        self.action = ''
        self.set_state(True)

    def human_turn_end(self):
        """Le tour du joueur humain se finit peut-être."""
        try:
            # action = self.current_player.play(f'{self.action[0].str_}>{self.action[1].str_}>{self.action[2].str_}')
            action = self.current_player.play(self.action)
            self.update_from_action(action)
            self.set_state(False)
            self.next_turn()
        except InvalidActionError:
            self.action = ''

    def add_action(self, action):
        """Ajoute un coup à l'action du joueur humain courant.

        Args:
            action(Cell): cellule du coup
        """
        if len(self.action) == 0:
            self.action += action.coord_str
        else:
            self.action += f'>{action.coord_str}'
        assert len(self.action) <= 8
        # print(self.action)
        if len(self.action) == 8:
            self.human_turn_end()

    def declare_winner(self):
        WinnerMsg(self.game.show_winner(), self.parent())

    def set_state(self, state=True):
        """Active et désactive le plateau de jeu.

            Le plateau est activé lorsque c'est à un joueur humain de jouer,
        sinon, il est désactivé.

        Args:
            state(bool): True s'il faut activer
        """
        if not state:
            # self.cells.checkedButton().setChecked(False)
            self.grid_ui.cells.setExclusive(False)
            # print(self.grid_ui.cells.checkedButton().coord_str)
            button = self.grid_ui.cells.checkedButton()
            button.setChecked(False)
            button.repaint()
            self.grid_ui.disable_grid()  # setAttribute(Qt.WA_TransparentForMouseEvents, True)
            # for cell in self:
            #     cell.setChecked(False)
            #     cell.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        else:
            # self.parent().setAttribute(Qt.WA_TransparentForMouseEvents)
            self.grid_ui.cells.setExclusive(True)
            self.grid_ui.disable_grid()  # setAttribute(Qt.WA_TransparentForMouseEvents, False)
            # for cell in self:
            #     # print(cell.id_)
            #     # if cell.id_ in (0, 1):
            #     # print(type(cell))
            #     cell.setAttribute(Qt.WA_TransparentForMouseEvents, False)

    def update_from_action(self, action):
        """Met à jour la gui du plateau."""
        self.grid_ui[action.old_pos] = TOKENS[EMPTY]
        self.grid_ui[action.new_pos] = TOKENS[action.player]
        self.grid_ui[action.arrow_pos] = TOKENS[ARROW]
        # for cell in self:
        #     # print(cell)
        #     # print(self.board.grid[cell.coord])
        #     path = PATHS[self.game.board.grid[cell.coord]]
        #     # print(path)
        #     cell.set_token(path)

    # def __iter__(self):
    #     """Itération sur toutes les cases de la gui de la grille."""
    #     for i in range(self.N):
    #         for j in range(self.N):
    #             # print(self[Pos2D(i, j)])
    #             print(self[Pos2D(i, j)])
    #             yield self[Pos2D(i, j)]

    # def __getitem__(self, pos):
    #     """Renvoir l'item la position en paramètre.
    # 
    #     Args:
    #         pos(Pos2D): position demandée"""
    #     return self.itemAtPosition(-(pos.row-self.N+1), pos.col).widget()


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


