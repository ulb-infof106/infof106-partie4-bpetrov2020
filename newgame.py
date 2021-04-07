from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from amazons import Amazons
from const import *
from players import *
from grid_ui import Token
from pos2d import Pos2D
import copy

from MessageBoxes import *



class NewGame(QDialog):
    """Fenêtre de configuration d'une nouvelle partie.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(565, 796)
        # self.setGeometry(400,400,565, 1000)
        self.setWindowTitle("Configuration de la partie")
        self.layout = QVBoxLayout()

        self.players = PlayersTypes()
        self.layout.addLayout(self.players)

        self.custom_board = CustomBoard()
        self.layout.addLayout(self.custom_board)

        beg_game_button = QPushButton("Commencer la partie")
        beg_game_button.clicked.connect(self.begin_func)
        self.layout.addWidget(beg_game_button)

        self.setLayout(self.layout)
        self.custom_board.spinner.setValue(5)
        # self.exec_()

    def resizeEvent(self, QResizeEvent=None):
        width = self.custom_board.grid.horizontalHeader().sectionSize(0)
        self.custom_board.grid.verticalHeader().setDefaultSectionSize(width)


    def begin_func(self):
        # self.board.to_amazon()
        self.custom_board.to_attributes()
        self.board_size = self.custom_board.size
        self.pos_white = self.custom_board.pos_white
        self.pos_black = self.custom_board.pos_black
        self.pos_arrows = self.custom_board.pos_arrows
        if self.board_size == 1:
            OneSizeBoard(self)
            return
        if len(self.pos_white) == 0 or len(self.pos_black) == 0:
            NotEnoughTokens(self)
            return
        self.delay = self.players.delay_slider.value
        print(self.delay)
        self.player1 = self.players.player1.type_.currentIndex()
        self.player2 = self.players.player2.type_.currentIndex()

        self.close()


class PlayersTypes(QVBoxLayout):
    """Représente le formulaire de choix des types des joueurs."""

    def __init__(self):
        super().__init__()

        self.types_layout = QHBoxLayout()
        # self.types_layout.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,10)
        # self.setContentsMargins(11,11,11,22)
        # self.setSpacing(20)

        self.player1 = PlayerType("blanc")
        self.player1.type_.activated.connect(self.enable_slider)
        self.types_layout.addLayout(self.player1)
        self.player2 = PlayerType("noir")
        self.player2.type_.activated.connect(self.enable_slider)
        self.types_layout.addLayout(self.player2)
        self.addLayout(self.types_layout)

        self.delay_slider = DelaySlider()# TODO
        self.addLayout(self.delay_slider)
        self.insertSpacing(1, 8)

    def enable_slider(self):
        if self.player1.type_.currentIndex() or self.player2.type_.currentIndex():
            self.delay_slider.slider.setEnabled(True)
        else:
            self.delay_slider.slider.setEnabled(False)


class PlayerType(QFormLayout):
    """Représente le formulaire de choix d'un joueur.

    Args:
        couleur (str): couleur du joueur de ce formulaire
    """

    def __init__(self, couleur):
        super().__init__()

        self.setFormAlignment(Qt.AlignCenter)
        self.addRow(f"Joueur {couleur} :", self.type_())
        # self.addRow("Délais IA :", self.slider())

    def type_(self):
        """Création de la combobox qui choisit le type d'un joueur."""
        self.type_ = QComboBox()
        self.type_.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.type_.addItems(["Humain", "Ordinateur"])
        # self.type_.activated.connect(self.enable_slider)
        return self.type_

class DelaySlider(QFormLayout):

    def __init__(self):
        super().__init__()

        self.setFormAlignment(Qt.AlignRight)
        self.addRow(f"Délais IA :", self.delay_slider())

    def delay_slider(self):
        """Création du slider de délais de l'IA. Plus élevé = plus dur."""
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimumWidth(200)
        self.slider.setEnabled(False)
        self.slider.setTickPosition(QSlider.TicksBelow)

        self.slider.setRange(1, 10)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(1)
        self.slider.setValue(2)
        return self.slider

    @property
    def value(self):
        return self.slider.value()


    # def enable_slider(self, ia):
    #     """Activer et désactiver le slider selon le choix du joueur.
    #     Le slider n'est actif que si le joueur est une IA.
    # 
    #     Args:
    #         ia (int): index élément sélectionné -> 1 si IA 0 si humain
    #     """
    #     if ia:
    #         self.slider.setEnabled(True)  # slider est en deuxième pos
    #     else:
    #         self.slider.setEnabled(False)


    # def slider(self):
    #     """Création du slider de délais de l'IA. Plus élevé = plus dur."""
    #     self.slider = QSlider(Qt.Horizontal)
    #     self.slider.setEnabled(False)
    #     self.slider.setTickPosition(QSlider.TicksBelow)
    # 
    #     self.slider.setRange(1, 10)
    #     self.slider.setSingleStep(1)
    #     self.slider.setTickInterval(1)
    #     return self.slider


class CustomBoard(QVBoxLayout):
    """Initialise la configuration du plateau de jeu."""

    def __init__(self):
        super().__init__()

        # self.amazons = Amazons()

        self.addLayout(self.top_buttons())
        self.grid = CustomGridUI()
        self.addWidget(self.grid)
        self.addLayout(self.bottom_buttons())

    def to_attributes(self, file_=None):
        # TODO
        self.pos_arrows = []
        self.pos_black = []
        self.pos_white = []
        self.size = self.spinner.value()
        for cell in self.grid:
            if cell.id_ == 0:
                self.pos_white.append(cell.coord_str)
            elif cell.id_ == 1:
                self.pos_black.append(cell.coord_str)
            elif cell.id_ == 3:
                self.pos_arrows.append(cell.coord_str)
        print(self.pos_white, self.pos_black, self.pos_arrows)
        # self.amazons.set_board(size pos_black, pos_white, pos_arrows)

    def from_amazon(self):
        """Met à jour la gui depuis l'instance d'Amazons."""

        # self.grid.clearBoard()

        size = self.amazons.board.N
        self.spinner.setValue(size)

        for row in range(size):
            for col in range(size):
                value = self.amazons.board.grid[Pos2D(row, col)]
                # print(row, col, value)
                self.grid[Pos2D(-(row-size+1), col)] = TOKENS[value]
                # print(-(row-size+1), col, "<<")
                

        # # chars = [WHITE, BLACK, CHARS[3]]
        # chars = self.board.tokens
        # pions = self.amazons.board.queens
        # pions.append(self.amazons.board.arrows[0])
        # size
        # for positions, char in zip(pions, chars):
        #     for pos in positions:
        #         # print(pos)
        #         # print(pos.x, pos.y, colors[n])
        #         fill = QTableWidgetItem(char)
        #         fill.setTextAlignment(Qt.AlignCenter)
        #         self.board.setItem(-(pos.y-size+1), pos.x, fill)
        # pass

    def load_file(self):
        filename = QFileDialog.getOpenFileName(self.parent().parent(),
                                               "Ouvrir un fichier",
                                               "",
                                               "Fichier texte (.txt)")[0]
        # print(self.board.itemAt(0,0).text())
        # self.to_amazon(filename[0])
        if filename == '':
            NoFileError(self.parent().parent())
            return
        try:
            self.amazons = Amazons(filename)
        # self.to_amazon(filename[0])
            self.from_amazon()
        except (InvalidFormatError, InvalidPositionError):
            InvalidFormatErrorMsg(self.parent().parent())
        # size, pos_black, pos_white, pos_arrows = read_file(filename[0])

        # self.spinner.setValue(size)
        # print(pos_black, pos_white, pos_arrows)

    def load_file_button(self):
        button = QPushButton("Charger un fichier")
        button.clicked.connect(self.load_file)
        return button

    def reset_button(self):
        button = QPushButton("Réinitialiser le plateau")
        button.clicked.connect(self.grid.clearBoard)
        return button

    def bottom_buttons(self):
        buttons = QHBoxLayout()
        buttons.addWidget(self.reset_button())
        buttons.addWidget(self.load_file_button())
        return buttons

    def fill_selection(self, id_fill):
        """Remplit la sélection du plateau du pion choisie."""
        # print(id_fill)
        token = TOKENS[id_fill]  # empty
        selection = self.grid.selectedIndexes()
        for i in selection:
            row = i.row()
            col = i.column()
            self.grid[Pos2D(row, col)] = token

    def change_board_size(self, new_size):
        """Change la taille du plateau selon la valeur du spinner."""
        self.grid.setRowCount(new_size)
        self.grid.setColumnCount(new_size)

        # change également la hauteur des cellules pour qu'elles soient carrées
        width = self.grid.horizontalHeader().sectionSize(0)
        self.grid.verticalHeader().setDefaultSectionSize(width)

        self.grid.size_changed(new_size)

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
        # button.pressed.connect(self.fill_selection)

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

        tokens_names = ("Blancs", "Noirs", "Vide", "Flèches")
        self.top_bar_group = QButtonGroup()
        self.top_bar_group.idPressed.connect(self.fill_selection)
        n = 0  # id des boutons
        for name in tokens_names:
            button = self.config_button(name)
            self.top_bar_group.addButton(button, n)
            self.top_bar.addWidget(button)
            n += 1
        return self.top_bar


class CustomGridUI(QTableWidget):
    """Représente l'interface graphique d'un plateau de jeu.
    """

    def __init__(self):
        super().__init__(1, 1)
        self.size = 1
        # self.setViewportMargins(20,20,20,20)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.horizontalHeader().setMinimumSectionSize(10)
        self.verticalHeader().setMinimumSectionSize(10)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setItem(0, 0, Background(0))
        self.setCellWidget(0, 0, CustomGridCell(0,0, 1))

    def __setitem__(self, index, value):
        assert isinstance(index, Pos2D)
        self.cellWidget(index.row, index.col).set_token(value)

    def __iter__(self):
        for row in range(self.size):
            for col in range(self.size):
                yield self.cellWidget(row, col)

    def clearBoard(self):
        for cell in self:
            cell.set_token(TOKENS[EMPTY])

    def size_changed(self, new_size):
        old_size = self.size
        self.size = new_size
        for row in range(old_size):
            for col in range(old_size):
                if self.cellWidget(row, col) is not None:
                    self.cellWidget(row, col).coord_str = f'{chr(col + 97)}{-(row-new_size+1)+1}'
        for row in range(old_size, new_size):
            for col in range(self.size):
                self.setItem(row, col, Background((col+row)%2))
                self.setCellWidget(row, col, CustomGridCell(col, row, new_size))
        for col in range(old_size, new_size):
            for row in range(old_size):
                self.setItem(row, col, Background((col+row)%2))
                self.setCellWidget(row, col, CustomGridCell(col, row, new_size))
                


class Background(QTableWidgetItem):

    def __init__(self, light=1):
        super().__init__()

        # color
        if light:
            self.setBackground(QBrush(QColor("#d2cba8")))
        else:
            self.setBackground(QBrush(QColor("#463c26")))


class CustomGridCell(QWidget):
    """Un pion sur le plateau custom."""

    def __init__(self, col, row, size, token=EMPTY):
        super().__init__()

        self.id_ = token
        self.token = Token(TOKENS[token])
        self.coord_str = f'{chr(col + 97)}{-(row-size+1)+1}'

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.margin = 4
        layout.setContentsMargins(self.margin, self.margin, self.margin, self.margin)

        layout.addWidget(self.token)
        self.setLayout(layout)

    def set_token(self, path):
        self.id_ = TOKENS.index(path)
        self.token.setPixmap(QPixmap(path))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    new = NewGame()
    new.exec_()
