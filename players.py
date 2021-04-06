import random
import time
from abc import ABCMeta, abstractmethod
from const import *
from exceptions import *
from action import Action

class Player(metaclass=ABCMeta):
    """
    Classe abstraite représentant un joueur quelconque.

    Attributes:
        board (Board): le plateau de jeu sur lequel le joueur va effectuer ses actions
        player_id (int): l'id du joueur
    """
    def __init__(self, board, player_id):
        self.board = board
        self.player_id = player_id

    @abstractmethod
    def _play(self):
        pass

    def play(self, coup=None, delay=None):
        """
        Détermine l'action à effectuer et la joue sur le plateau
        """
        if delay is None:
            action = self._play(coup)
        else:
            action = self._play(coup, delay)
        self.board.act(action)
        return action

    @property
    def other_player_id(self):
        """
        int: l'id du joueur adverse
        """
        return PLAYER_2 if self.player_id == PLAYER_1 else PLAYER_1

class HumanPlayer(Player):
    """
    Spécialisation de Player représentant un joueur humain
    """
    def __init__(self, board, player_id):
        super().__init__(board, player_id)

    def _play(self, coup=None):
        """
        Récupère l'action désirée via stdin

        Returns:
            Action: l'action récupérée sur stdin
        """
        valid = False
        joueur = WHITE if self.player_id == 1 else BLACK

        if coup is None:
            while not valid:
                coup = input(MESSAGE_COUP.format('1' if self.player_id == PLAYER_1 else '2'))
                if coup.count('>') != 2:
                    print(ERREUR_COUP)
                    continue
                try:
                    action = Action(*coup.split('>'), self.player_id)
                    valid = self.board.is_valid_action(action)
                except InvalidActionError:
                    continue
        else:
            action = Action(*coup.split('>'), self.player_id)
            self.board.is_valid_action(action)
        return action

class AIPlayer(Player):
    """
    Spécialisation de la classe Player représentant un joueur utilisant un minimax
    """
    def __init__(self, board, player_id):
        super().__init__(board, player_id)

    def _play(self, coup=None, delay=2):
        """
        Détermine le meilleur coup à jouer

        Returns:
            Action: le meilleur coup déterminé via minimax
        """
        print("ID", self.player_id, "white 0, black 1")
        self.timer_beg = time.time()
        self.delay = delay
        self.return_single_delay = 0.004
        self.return_delay = 0
        depth = 1
        best_score = None
        while time.time() - self.timer_beg + self.return_single_delay < self.delay:
            ret, score = self.minimax(depth)
            if best_score is None and ret is not None:
                # print(ret, score)
                best_ret = ret
                best_score = score
            elif score >= best_score and ret is not None:
                # print(ret, score)
                best_ret = ret
                best_score = score
            depth += 1
        print(time.time()- self.timer_beg)
        assert time.time()- self.timer_beg < self.delay
        print(best_ret, best_score)
        # print(self.board.label_components())
        print(self.accessible_cells())
        return best_ret

    def accessible_cells(self):
        components, components_ids = self.board.label_components()
        score = 0
        for component in components:
            current, opponent = 0, 0
            for queen in self.board.queens[self.player_id]:
                if queen in component:
                    current += 1
            for queen in self.board.queens[self.other_player_id]:
                if queen in component:
                    opponent += 1
            if opponent < current:
                score += len(component) / (current+opponent) * (current-opponent)
            elif opponent > current:
                score -= len(component) / (current+opponent) * (opponent-current)
        return score
        # queens_ids = {}
        # player_id = self.player_id
        # score = 0
        # for _ in range(2):
        #     for queen in self.board.queens[player_id]:
        #         queen_id = components_ids[queen]
        #         if queen_id not in queens_ids:
        #             queens_ids[queen_id] = [(queen, player_id)]
        #         else:
        #             queens_ids[queen_id].append((queen, player_id))
        #     player_id = self.other_player_id
        # for id_ in queens_ids:
            
            

    def minimax(self, depth=2, maximizing=True):
        """
        Détermine le coup optimal à jouer selon l'algorithme minimax.

        Args:
            depth (int): la profondeur à explorer dans l'arbre des coups possibles
            maximizing (bool): True si on cherche à maximiser le score et False si on cherche à le maximiser

        Returns:
            Action: le meilleur coup trouvé dans la profondeur explorée
        """
        self.return_delay += self.return_single_delay
        if time.time() - self.timer_beg + self.return_delay >= self.delay:
             return (None, 0)
        if depth == 0:
            # print(self.board)
            # self.adjacent_moves()
            # time.sleep(5)
            print(self.board, self.objective_function())
            return (None, self.objective_function())
            # return (None, DRAW)
        if maximizing:
            best_score = -INF
            player = self.player_id
        else:
            best_score = +INF
            player = self.other_player_id
        best_actions = []
        assert self.board.has_moves(player)
        for action in self.board.possible_actions(player):
            self.board.act(action)
            winner = self.board.status.winner
            if winner is not None:
                score = WIN+depth  # Il vaut mieux gagner tôt (ou perdre tard) que de gagner tard (ou perdre tôt)
                if winner == self.other_player_id:
                    score *= -1
            else:
                score = self.minimax(depth-1, not maximizing)[1]
                self.return_delay -= self.return_single_delay
            self.board.undo()
            # Si on trouve un meilleur score
            if (score > best_score and maximizing) or (score < best_score and not maximizing):
                best_score = score
                best_actions = [action]
            elif score == best_score:
                best_actions.append(action)
            if time.time() - self.timer_beg + self.return_delay >= self.delay:
                break
        return random.choice(best_actions), best_score

    def objective_function(self):
        # if isolated:
        #     pass # TODO
        # else:
        #     pass # TODO
        score = self.accessible_cells()
        # if score 
        score += self.adjacent_moves()
        # if self.board.check_regions():
        #     score_curr = self.board.scores[self.player_id]
        #     score_other = self.board.scores[self.other_player_id]
        #     score += score_curr - score_other
        return score

    def adjacent_moves(self):
        """18n2 - 36n + 18 cases au maximum"""
        curr_score, other_score = 0, 0
        for queen in self.board.queens[self.player_id]:
            # for _ in self.board.possible_actions(self.player_id):
            for _ in self.board._possible_moves_from(queen):
                curr_score += 1
        for queen in self.board.queens[self.other_player_id]:
            # for _ in self.board.possible_actions(self.other_player_id):
            for _ in self.board._possible_moves_from(queen):
                other_score += 1
        # for queen in self.board.queens[self.player_id]:
        #     for dir_ in DIRECTIONS:
        #         # print(queen, queen+dir_)
        #         if self.board.is_valid_pos(queen+dir_)\
        #            and self.board.at(queen+dir_) == EMPTY:
        #             curr_score += 1
        #         # print(score)
        # 
        # for queen in self.board.queens[self.other_player_id]:
        #     for dir_ in DIRECTIONS:
        #         # print(queen, queen+dir_)
        #         if self.board.is_valid_pos(queen+dir_)\
        #            and self.board.at(queen+dir_) == EMPTY:
        #             other_score += 1
                # print(score)
        return curr_score - 2*other_score
        # time.sleep(3)
        # return current_player - other_player
        # print(current_player - other_player)
                
