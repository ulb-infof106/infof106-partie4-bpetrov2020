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
from newgame import *

from MessageBoxes import *


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()  # initialiser QMainWindow

        self.layout = QVBoxLayout()
        self.path = ''

        self.setWindowTitle("Jeu des amazones")

        self.resize(700, 800)

        self.add_menu_bar()

        # self.player1 = self.player_type("blanc")
        # self.layout.addLayout(self.player1)
        # self.player2 = self.player_type("noir")
        # self.layout.addLayout(self.player2)

        # self.load_button = QPushButton("Charger un fichier")
        # self.load_button.clicked.connect(self.load_file)
        # self.layout.addWidget(self.load_button)

        self.board_widget = QWidget()  # widget factice du plateau
        self.board_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.board_outer_layout = QHBoxLayout()  # pour pouvoir centrer le plateau
        self.board_outer_layout.setAlignment(Qt.AlignCenter)
        self.board_outer_layout.addWidget(self.board_widget)
        self.layout.addLayout(self.board_outer_layout)

        # self.begin_button = QPushButton("Commencer la partie")
        # self.begin_button.clicked.connect(self.begin_game)
        # self.layout.addWidget(self.begin_button)

        # self.custom_status = QHBoxLayout()
        # self.custom_status.addWidget(QLabel("En train de jouer"))
        # self.fill_widget = QWidget()
        # self.fill_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # self.custom_status.addWidget(self.fill_widget)
        # self.layout.addLayout(self.custom_status)

        self.add_custom_status_bar()

        self.widget = QWidget()  # widget factice
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.show()

    def add_menu_bar(self):
        menu_bar = self.menuBar()

        game_menu = menu_bar.addMenu('Jeu')

        self.new_game = QAction()
        self.new_game.setText("Nouvelle partie...")
        self.new_game.triggered.connect(self.config_new_game)
        game_menu.addAction(self.new_game)

    def add_custom_status_bar(self):
        """Ajout d'une barre de statut."""
        status_bar = QHBoxLayout()
        status_bar.setContentsMargins(0,0,6,0)

        self.status_msg = QLabel("")  # message du joueur en train de jouer
        status_bar.addWidget(self.status_msg)

        fill_widget = QWidget()  # pour que les widgets soient à gauch et à droite
        fill_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        status_bar.addWidget(fill_widget)

        self.delay_slid = DelaySlider()  # modifier le délais d'ia en jeu
        self.delay_slid.slider.setMaximumWidth(200)
        status_bar.addLayout(self.delay_slid)

        self.layout.addLayout(status_bar)

    def config_new_game(self):
        """Configuration et commencement d'une partie."""
        print("ok")
        self.newG = NewGame(self)
        self.newG.exec_()
        try:
            self.newG.delay  # test fenêtre a été fermée -> pas de config
            self.begin_game()
            print("game begins")
        except AttributeError:
            print("game doesnt begin")
            pass

    # def player_type(self, couleur):
    #     layout = QFormLayout()
    #     layout.setFormAlignment(Qt.AlignCenter)
    # 
    #     layout.combo = QComboBox()
    #     layout.combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    #     layout.combo.addItems(["Humain", "Ordinateur"])
    # 
    #     layout.addRow(f"Joueur {couleur} :", layout.combo)
    #     return layout

    # def load_file(self):
    #     self.path = QFileDialog.getOpenFileName(None,
    #                                             "Charger un fichier",
    #                                             "",
    #                                             "Fichier de configuration (.txt)")[0]

    def begin_game(self, path=None):
        """Démarre une partie de jeu."""
        
        # if self.path == '':
        #     NoFileError(self)
        #     return
        # 
        # self.begin_button.setText("Recommencer")
        # self.begin_button.clicked.disconnect()  # ne pas avoir la connection précédente
        # self.begin_button.clicked.connect(self.stop_game)
        # 
        if not self.board_outer_layout.isEmpty():  # si partie déjà en cours
            child = self.board_outer_layout.takeAt(0)
            self.board_outer_layout.removeWidget(child.widget())

        self.amazons = Amazons()
        self.amazons.set_board(self.newG.board_size,
                               self.newG.pos_black,
                               self.newG.pos_white,
                               self.newG.pos_arrows,
                               self.newG.players.player1.type_.currentIndex(),
                               self.newG.players.player2.type_.currentIndex())
        # self.board_widget = BoardUI(Amazons(,
        #                                     self.player1.combo.currentIndex(),
        #                                     self.player2.combo.currentIndex()),
        #                             self)
        self.board_widget = BoardUI(self.amazons)
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

        self.status_bar_msg = ("Joueur blanc ({0}) est en cours de rélfexion...",
                               "Joueur noir ({0}) est en cours de rélfexion...")

        self.current_player_idx = 1  # deuxième joueur, va être changé dans next_turn()

        delay = 1000
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
                self.parent().parent().status_msg.setText(self.status_bar_msg[self.current_player_idx].format("humain"))
                self.human_turn_begin()
            else:
                self.parent().parent().status_msg.setText(self.status_bar_msg[self.current_player_idx].format("ordinateur"))
                action = self.current_player.play()
                self.update_from_action(action)
                self.timer.start()
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


