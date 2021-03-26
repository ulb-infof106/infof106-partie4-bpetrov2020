from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QSlider,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QSizePolicy,
    QAbstractItemView,
    QHeaderView
    )
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

from amazons import Amazons
from const import *


# def extract_positions(line):
#     """
#     Récupère la liste de positions dans line
# 
#     Args:
#         line (str): string sous la forme '<pos1>,<pos2>,<pos3>,...,<posn>'
# 
#     Returns:
#         list: liste d'instances de Pos2D
# 
#     Raises:
#         InvalidFormatError: si la ligne est vide
#     """
#     if line == '':
#         raise InvalidFormatError('Liste de positions vide')
#     else:
#         return line.strip().split(',')
# 
# 
# def read_file(path):
#     """
#     Récupère les informations stockées dans le fichier donné
# 
#     Args:
#         path (str): chemin vers un fichier de format de plateau
# 
#     Returns:
#         tuple: (size, pos_black, pos_white, pos_arrows)
# 
#     Raises:
#         InvalidFormatError: si le format du fichier est invalide
#     """
#     with open(path, 'r') as f:
#         try:
#             size = int(f.readline().strip())
#         except ValueError:  # Si la première ligne n'est pas un entier
#             raise InvalidFormatError('La taille du plateau n\'est pas donnée')
#         pos_black = extract_positions(f.readline())
#         pos_white = extract_positions(f.readline())
#         # on récupère la liste des positions des flèches
#         try:
#             pos_arrows = extract_positions(f.readline())
#         except InvalidFormatError:
#             pos_arrows = []
#         if f.readline() != '':  # S'il reste du texte dans le fichier
#             raise InvalidFormatError('Format invalide: informations après les flèches')
#     return size, pos_black, pos_white, pos_arrows


class NewGame(QDialog):
    """Fenêtre de configuration d'une nouvelle partie.
    """

    def __init__(self):
        super().__init__()

        self.resize(565, 796)
        self.setWindowTitle("Configuration de la partie")
        self.layout = QVBoxLayout()

        players = PlayersType()
        self.layout.addLayout(players)
        board = CustomBoard()
        self.layout.addLayout(board)
        # self.layout.addWidget(BeginGame)
        geom = QPushButton("Geom")
        geom.clicked.connect(self.sample)
        self.layout.addWidget(geom)
        

        self.setLayout(self.layout)
        # self.exec_()

    def sample(self):
        print(self.height(), self.width())

    def begin_button(self):
        beg_game_button = QPushButton()
        beg_game_button.clicked.connect(begin_func)

    def begin_func(self):
        self.n = self.board.spinner.getValue()
        self.pos_blanc


class PlayersType(QHBoxLayout):
    """Représente le formulaire de choix des types des joueurs."""

    def __init__(self):
        super().__init__()

        self.addLayout(Player("blanc"))
        self.addLayout(Player("noir"))
        self.insertSpacing(1, 10)


class Player(QFormLayout):
    """Représente le formulaire de choix d'un joueur.

    Args:
        couleur (str): couleur du joueur de ce formulaire
    """

    def __init__(self, couleur):
        super().__init__()

        self.setFormAlignment(Qt.AlignCenter)

        self.addRow(f"Joueur {couleur} :", self.player())
        self.addRow("Délais IA :", self.slider())

    def enable_slider(self, ia):
        """Activer et désactiver le slider selon le choix du joueur.
        Le slider n'est actif que si le joueur est une IA.

        Args:
            ia (int): index élément sélectionné -> 1 si IA 0 si humain
        """
        if ia:
            self.slider.setEnabled(True)  # slider est en deuxième pos
        else:
            self.slider.setEnabled(False)

    def player(self):
        """Création de la combobox qui choisit le type d'un joueur."""
        player = QComboBox()
        player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        player.addItems(["Humain", "Ordinateur"])
        player.activated.connect(self.enable_slider)
        return player

    def slider(self):
        """Création du slider de délais de l'IA. Plus élevé = plus dur."""
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.setTickPosition(QSlider.TicksBelow)

        self.slider.setRange(1, 10)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(1)
        return self.slider


class CustomBoard(QVBoxLayout):
    """Initialise la configuration du plateau de jeu."""

    def __init__(self):
        super().__init__()

        self.amazons = Amazons(10, [], [], [])

        self.addLayout(self.top_buttons())
        self.addWidget(self.board_widget())
        self.addLayout(self.bottom_buttons())

    def to_amazon(self, file_=None):
        # TODO
        if file_ is not None:
            self.amazons.read_new_file(file_)
        else:
            pos_arrows = []
            pos_black = []
            pos_white = []
            size = self.spinner.value()
            letters = "abcdefghijklmnopqrstuvwxyz"
            for j in range(size):
                for i in range(size):
                    cell = self.board.item(i, j)
                    # print(self.board.itemAt(i, j))
                    # print(cell)
                    if cell is not None:
                        print(cell.text())
                        if cell.text() == CHARS[0]:
                            pos_white.append(f'{letters[j]}{-(i-size)}')
                            # print(pos_white)
                        elif cell.text() == CHARS[1]:
                            pos_black.append(f'{letters[j]}{-(i-size)}')
                        elif cell.text() == CHARS[3]:
                            pos_arrows.append(f'{letters[j]}{-(i-size)}')

            print(pos_arrows, pos_white, pos_black)
            self.amazons.from_config(size,
                                     pos_black,
                                     pos_white,
                                     pos_arrows)
        
        pass

    def from_amazon(self):
        # TODO
        self.board.clear()

        size = self.amazons.board.N
        self.spinner.setValue(size)

        chars = [WHITE, BLACK, CHARS[3]]
        pions = self.amazons.board.queens
        pions.append(self.amazons.board.arrows[0])
        size
        for positions, char in zip(pions, chars):
            for pos in positions:
                # print(pos)
                # print(pos.x, pos.y, colors[n])
                fill = QTableWidgetItem(char)
                fill.setTextAlignment(Qt.AlignCenter)
                self.board.setItem(-(pos.y-size+1), pos.x, fill)
        pass

    def load_file(self):
        filename = QFileDialog.getOpenFileName(None,
                                               "Ouvrir un fichier",
                                               "",
                                               "Fichier amazones (.txt)")
        # print(self.board.itemAt(0,0).text())
        # self.to_amazon(filename[0])
        self.to_amazon()
        self.from_amazon()
        # size, pos_black, pos_white, pos_arrows = read_file(filename[0])

        # self.spinner.setValue(size)
        # print(pos_black, pos_white, pos_arrows)

    def load_file_button(self):
        button = QPushButton("Charger un fichier")
        button.clicked.connect(self.load_file)
        return button

    def reset_button(self):
        button = QPushButton("Réinitialiser le plateau")
        button.clicked.connect(self.board.clear)
        return button

    def bottom_buttons(self):
        buttons = QHBoxLayout()
        buttons.addWidget(self.reset_button())
        buttons.addWidget(self.load_file_button())
        return buttons

    def fill_selection(self):
        """Remplit la sélection du plateau du pion choisit."""
        token = None
        tokens = ('\u25CB', '\u25CF', "✕")
        for i in range(1, 4):
            if self.top_bar.itemAt(i).widget().isDown():
                token = tokens[i-1]
                break
        selection = self.board.selectedIndexes()
        for i in selection:
            fill = QTableWidgetItem(token)
            fill.setTextAlignment(Qt.AlignCenter)
            self.board.setItem(i.row(), i.column(), fill)

    def change_board_size(self, new_size):
        """Change la taille du plateau selon la valeur du spinner."""
        self.board.setRowCount(new_size)
        self.board.setColumnCount(new_size)

        # change également la hauteur des cellules pour qu'elles soient carrées
        width = self.board.horizontalHeader().sectionSize(0)
        self.board.verticalHeader().setDefaultSectionSize(width)

    def size_spinner(self):
        self.spinner = QSpinBox()
        self.spinner.setRange(1, 26)
        self.spinner.valueChanged.connect(self.change_board_size)
        self.spinner.setToolTip("Taille du plateau de jeu")
        self.spinner.setToolTipDuration(5000)
        return self.spinner

    def config_button(self, label):
        """Initialise un bouton de la barre d'outils supérieure du plateau."""
        button = QPushButton(label)
        button.pressed.connect(self.fill_selection)

        if label == "Flèches":
            button.setToolTip("Appuyez pour remplir la sélection de flèches")
            button.setShortcut(QKeySequence("X"))

        elif label == "Vide":
            button.setToolTip("Appuyez pour supprimer la sélection")
            button.setShortcut(QKeySequence("Del"))

        else:
            button.setToolTip(f"Appuyez pour remplir la "
                              f"sélection de pions {label.lower()}")
            if label == "Blancs":
                button.setShortcut("B")
            else:
                button.setShortcut("N")

        button.setToolTipDuration(5000)
        return button

    def top_buttons(self):
        """Crée les bouttons au-dessus du plateau."""
        self.top_bar = QHBoxLayout()
        self.top_bar.addWidget(self.size_spinner())
        self.top_bar.addWidget(self.config_button("Blancs"))
        self.top_bar.addWidget(self.config_button("Noirs"))
        self.top_bar.addWidget(self.config_button("Flèches"))
        self.top_bar.addWidget(self.config_button("Vide"))
        return self.top_bar

    def board_widget(self):
        """Crée le plateau de jeu configurable."""
        self.board = QTableWidget()
        self.board.horizontalHeader().hide()
        self.board.verticalHeader().hide()

        self.board.horizontalHeader().setMinimumSectionSize(20)
        self.board.verticalHeader().setMinimumSectionSize(20)

        self.board.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.board.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return self.board
