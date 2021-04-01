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

        self.setWindowTitle("Jeu des amazones")

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

        self.board_widget = BoardUI(Amazons(self.path,
                                            self.player1.combo.currentIndex(),
                                            self.player2.combo.currentIndex()),
                                    self)
        self.board_outer_layout.addWidget(self.board_widget)

        self.board_widget.timer.start()

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

    def resizeEvent(self, QResizeEvent):
        """Pour garder un plateau carré en redimentionnant la fenêtre."""
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
        self.grid_ui.set_disabled(True)
        self.grid_ui.cells.buttonClicked.connect(self.add_action)
        self.setLayout(self.grid_ui)

        self.current_player_idx = 1  # deuxième joueur, va être changé dans next_turn()

        delay = 2000
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_turn)
        self.timer.setSingleShot(True)
        self.timer.setInterval(delay)

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
                self.timer.start()
                action = self.current_player.play()
                self.update_from_action(action)
                # self.next_turn()

    def human_turn_begin(self):
        """Le tour du joueur humain commence."""
        self.action = []
        self.set_state(True)

    def human_turn_end(self):
        """Le tour du joueur humain se finit peut-être."""
        try:
            # action = self.current_player.play(f'{self.action[0].str_}>{self.action[1].str_}>{self.action[2].str_}')
            action = self.current_player.play(''.join(self.action))
            self.update_from_action(action)
            self.set_state(False)
            self.next_turn()
        except InvalidActionError:
            self.action = []

    def add_action(self, action):
        """Ajoute un coup à l'action du joueur humain courant.

        Args:
            action(Cell): cellule du coup
        """
        if len(self.action) == 0:
            self.action.append(action.coord_str)
        else:
            self.action.append(f'>{action.coord_str}')
        print(self.action)
        assert len(self.action) <= 3
        if len(self.action) == 3:
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
            self.grid_ui.cells.setExclusive(False)
            button = self.grid_ui.cells.checkedButton()
            button.setChecked(False)
            button.repaint()  # avoir un retour immédiat de la désactivation
            self.grid_ui.set_disabled(True)
        else:
            self.grid_ui.cells.setExclusive(True)
            self.grid_ui.set_disabled(False)

    def update_from_action(self, action):
        """Met à jour la gui du plateau.

        Args:
            action(Action): action qui vient d'être jouée
        """
        self.grid_ui[action.old_pos] = TOKENS[EMPTY]
        self.grid_ui[action.new_pos] = TOKENS[action.player]
        self.grid_ui[action.arrow_pos] = TOKENS[ARROW]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.exit(app.exec_())


