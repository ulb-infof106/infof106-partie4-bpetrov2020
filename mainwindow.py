"""
Prénom: Boris
Nom: Petrov
Matricule: 000515795
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import time
import pygame

from amazons import Amazons
from pos2d import Pos2D
from const import *
from players import HumanPlayer
from exceptions import *
from grid_ui import GridUI
from newgame import *

from MessageBoxes import *


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""

    def __init__(self):
        super().__init__()  # initialiser QMainWindow

        self.newG = NewGame(self)  # wizard pour une nouvelle partie
        self.layout = QVBoxLayout()

        self.setWindowTitle("Jeu des amazones")

        self.resize(730, 820)
        self.setMinimumWidth(730)

        # ajout de différentes composantes
        self.add_menu_bar()
        self.add_tool_bar()
        self.add_board_placeholder()
        self.add_custom_status_bar()

        self.widget = QWidget()  # widget factice
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.show()

        pygame.init()  # ajouter un peu de musique
        pygame.mixer.music.load('tmusic.ogg')
        pygame.mixer.music.play(-1)

    def add_menu_bar(self):
        """Ajoute la barre de menu."""
        menu_bar = self.menuBar()
        game_menu = menu_bar.addMenu('Jeu')

        self.new_game = QAction()
        self.new_game.setText("Nouvelle partie...")  # commencer une nouvelle partie
        self.new_game.setIcon(QIcon(QPixmap("new.svg")))
        self.new_game.triggered.connect(self.config_new_game)
        game_menu.addAction(self.new_game)

        self.save_game = QAction()  # sauvegarder la configuration actuelle
        self.save_game.setText("Sauvegarder la partie...")
        self.save_game.setIcon(QIcon(QPixmap("save.svg")))
        self.save_game.triggered.connect(self.save_game_)
        self.save_game.setEnabled(False)
        game_menu.addAction(self.save_game)

        self.quit_game = QAction()  # quitter la partie
        self.quit_game.setText("Quitter")
        self.quit_game.setIcon(QIcon(QPixmap("exit.svg")))
        self.quit_game.triggered.connect(self.close)
        game_menu.addAction(self.quit_game)

    def add_tool_bar(self):
        """Ajout de la barre d'outils."""
        self.tool_bar = QToolBar()

        self.pause_game = QAction()
        self.pause_game.setIcon(QIcon(QPixmap("pause.svg")))
        self.pause_game.triggered.connect(self.pause_game_)
        self.tool_bar.addAction(self.pause_game)

        self.layout.addWidget(self.tool_bar)
        self.tool_bar.hide()  # éviter de l'avoir au début

    def add_board_placeholder(self):
        """Placeholder pour le plateau qui va être ajouté par la suite."""
        self.greet_layout = QVBoxLayout()
        self.greet_layout.setAlignment(Qt.AlignCenter)
        self.greet_layout.setSpacing(20)
        self.greet_layout.setContentsMargins(60,60,60,60)

        greet_image_layout = QHBoxLayout()  # pour avoir une contrainte de grandeur et un alignement
        greet_image = QLabel()
        greet_image.setMaximumSize(300, 300)
        greet_image.setPixmap(QPixmap("greet_arrows.svg"))
        greet_image.setScaledContents(True)
        greet_image_layout.addWidget(greet_image)
        self.greet_layout.addLayout(greet_image_layout)

        greet_text = QLabel()
        greet_text.setAlignment(Qt.AlignCenter)
        greet_text.setStyleSheet("QLabel { font-size: 20px; font: bold}")
        greet_text.setText("Bienvenue dans le jeu des amazones !")
        self.greet_layout.addWidget(greet_text)

        greet_button_layout = QHBoxLayout()
        greet_button = QPushButton("Nouvelle partie")
        greet_button.clicked.connect(self.config_new_game)
        greet_button.setMaximumWidth(200)
        greet_button_layout.addWidget(greet_button)
        self.greet_layout.addLayout(greet_button_layout)

        self.board_widget = QWidget()  # widget factice du plateau
        self.board_widget.setLayout(self.greet_layout)
        self.board_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.board_outer_layout = QHBoxLayout()  # pour pouvoir centrer le plateau
        self.board_outer_layout.setAlignment(Qt.AlignCenter)

        self.board_outer_layout.addWidget(self.board_widget)
        self.layout.addLayout(self.board_outer_layout)

    def add_custom_status_bar(self):
        """Ajout d'une barre de statut."""
        self.status_bar = QWidget()
        status_bar_layout = QHBoxLayout()
        status_bar_layout.setContentsMargins(0,0,6,0)

        self.status_msg = QLabel("")  # message du joueur en train de jouer
        status_bar_layout.addWidget(self.status_msg)

        fill_widget = QWidget()  # pour que les widgets soient à gauch et à droite
        fill_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        status_bar_layout.addWidget(fill_widget)

        self.delay_slid = DelaySlider()  # modifier le délais d'ia en jeu
        self.delay_slid.slider.setMaximumWidth(200)
        self.delay_slid.slider.valueChanged.connect(self.change_delay)
        status_bar_layout.addLayout(self.delay_slid)

        self.status_bar.setLayout(status_bar_layout)
        self.layout.addWidget(self.status_bar)
        self.status_bar.hide()  # éviter de l'avoir au début

    def pause_game_(self):
        """Permet de mettre le jeu en pause.

            Lorsque le jeu est en pause, personne ne peut jouer.
        Ni IAs, ni humains.
        """
        if isinstance(self.board_widget, BoardUI):
            if self.board_widget.paused is False:
                self.pause_game.setIcon(QIcon(QPixmap("start.svg")))
                self.board_widget.paused = True
            else:
                self.pause_game.setIcon(QIcon(QPixmap("pause.svg")))
                self.board_widget.paused = False
                self.board_widget.timer.start()

    def config_new_game(self):
        """Configuration et commencement d'une partie."""
        self.newG.delay = None
        self.newG.exec_()
        if self.newG.delay is not None:  # test si fenêtre a été fermée -> pas de config
            self.status_bar.show()
            self.tool_bar.show()
            self.begin_game()

    def begin_game(self):
        """Démarre une partie."""

        if not self.board_outer_layout.isEmpty():  # si partie déjà en cours
            child = self.board_outer_layout.takeAt(0)
            child.widget().deleteLater()

        self.amazons = Amazons()
        self.amazons.set_board(self.newG.board_size,
                               self.newG.pos_black,
                               self.newG.pos_white,
                               self.newG.pos_arrows,
                               self.newG.player1,
                               self.newG.player2)

        self.board_widget = BoardUI(self.amazons)
        self.board_outer_layout.addWidget(self.board_widget)

        if self.newG.player1 or self.newG.player2:  # si au moin un joueur est IA
            self.delay_slid.slider.setEnabled(True)
        self.delay_slid.slider.setValue(self.newG.delay)

        self.save_game.setEnabled(True)

        self.board_widget.timer.start()  # commencer la partie

    def save_game_(self):
        """Permet de sauvegarder la configuration de la partie.

            Ce n'est pas une sauvegarde avec les types des joueurs, etc.
        Juste les positions des blancs, des noirs et des flèches, un fichier
        de configuration typique.
        """
        save_filename = QFileDialog.getSaveFileName(self,
                                                    "Ouvrir un fichier",
                                                    "",
                                                    "Fichier texte(.txt)")[0]
        if save_filename != "":  # si annulé
            if save_filename[-4:] != ".txt":  # si déjà extension
                save_filename += ".txt"

            save_file = open(f"{save_filename}", "w", encoding="utf-8")
            save_file.write(f'{self.amazons.board.N}\n')  # taille
            tokens = ([], [], [], [])
            for row in self.board_widget.grid_ui:
                for col in row:
                    if col.id_ != 2:
                        tokens[col.id_].append(col.coord_str)

            save_file.write(f"{','.join(tokens[1])}\n")  # positions noirs
            save_file.write(f"{','.join(tokens[0])}\n")  # positions blancs
            save_file.write(f"{','.join(tokens[3])}")    # positions flèches
            save_file.close()

    def change_delay(self, new_val):
        """Changer le délais de l'ia"""
        self.board_widget.delay = new_val

    def resizeEvent(self, QResizeEvent):
        """Pour garder un plateau carré en redimentionnant la fenêtre."""
        geo = self.board_outer_layout.geometry()
        if geo.width() < geo.height():
            self.board_widget.setMaximumHeight(geo.width())
            self.board_widget.setMaximumWidth(geo.width())
        elif geo.width() > geo.height():
            self.board_widget.setMaximumWidth(geo.height())
            self.board_widget.setMaximumHeight(geo.height())

    def closeEvent(self, QCloseEvent=None):
        """Implémentation d'un 'sauvegarder avant de quitter'."""
        state = True
        if isinstance(self.board_widget, BoardUI):  # pas besoin si pas de partie
            state = QuitMessage(self).exec_()
        if state == QMessageBox.Cancel:
            QCloseEvent.ignore()
        else:
            if state == QMessageBox.Save:
                self.save_game_()
            QCloseEvent.accept()


class BoardUI(QWidget):
    """Représente le widget d'un plateau de jeu.

    Args:
        game(Amazon): la partie en background
        parent(QWidget): le parent
    """

    def __init__(self, game, parent=None):
        super().__init__(parent)

        self.game = game
        self.grid_ui = GridUI(self.game.board)  # grille du jeu
        self.grid_ui.set_disabled(True)
        self.grid_ui.cells.buttonClicked.connect(self.add_action)
        self.setLayout(self.grid_ui)

        self.status_bar_msgs = ("Joueur blanc ({0}) est en cours de réflexion...",
                                "Joueur noir ({0}) est en cours de réflexion...")

        self.current_player_idx = 1  # deuxième joueur, va être changé dans next_turn()

        self.delay = 2
        self.paused = False  # détermine si la partie est en pause

        self.timer = QTimer()  # timer avant le prochain coup, pour pouvoir update le plateau
        self.timer.timeout.connect(self.next_turn)
        self.timer.setSingleShot(True)
        self.timer.setInterval(100)

    def next_turn(self):
        """Joue le prochain tour, humain ou ordinateur."""
        if self.paused:
            return
        elif self.game.is_over():
            self.declare_winner()
        else:
            self.current_player_idx = 1-self.current_player_idx  # passer au joueur suivant
            # joueur actuel joue
            self.current_player = self.game.players[self.current_player_idx]
            if isinstance(self.current_player, HumanPlayer):
                self.parent().parent().status_msg.setText(self.status_bar_msgs[self.current_player_idx].format("humain"))
                self.parent().parent().status_msg.repaint()  # avoir un retour immédiat
                self.human_turn_begin()
            else:
                self.parent().parent().status_msg.setText(self.status_bar_msgs[self.current_player_idx].format("ordinateur"))
                self.parent().parent().status_msg.repaint()  # avoir un retour immédiat
                action = self.current_player.play(delay=self.delay)
                self.update_from_action(action)
                self.timer.start()

    def human_turn_begin(self):
        """Le tour du joueur humain commence."""
        self.action = []
        self.set_state(True)

    def human_turn_end(self):
        """Le tour du joueur humain se finit peut-être."""
        try:
            action = self.current_player.play(''.join(self.action))
            self.update_from_action(action)
            self.set_state(False)
            self.next_turn()
        except InvalidActionError:  # si coup pas valide
            InvalidActionErrorMsg(self)
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
        # print(self.action)
        assert len(self.action) <= 3
        if len(self.action) == 3:
            self.human_turn_end()

    def declare_winner(self):
        """Déclare le gagant."""
        self.parent().parent().delay_slid.slider.setEnabled(False)

        winner_msg, winner_str = self.game.show_winner()

        self.parent().parent().status_msg.setText(f"La partie est finie. Joueur {winner_str} a gagné !")
        WinnerMsg(winner_msg, self.parent().parent())

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



