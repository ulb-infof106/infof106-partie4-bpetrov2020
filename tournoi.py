import random
from const import *
from exceptions import *
from action import Action
import time

class TournoiAIPlayer():
    """
    Spécialisation de la classe Player représentant un joueur utilisant un minimax
    """
    def __init__(self, board, player_id):
        self.board = board
        self.player_id = player_id

    @property
    def other_player_id(self):
        """
        int: l'id du joueur adverse
        """
        return PLAYER_2 if self.player_id == PLAYER_1 else PLAYER_1

    def play(self):
        """
        Détermine l'action à effectuer et la joue sur le plateau
        """
        action = self._play()
        self.board.act(action)

    def _play(self, delay=2):
        """
        Détermine le meilleur coup à jouer

        Returns:
            Action: le meilleur coup déterminé via minimax
        """
        # print("ID", self.player_id, "white 0, black 1")
        self.timer_beg = time.time()
        self.delay = delay
        self.return_single_delay = 0.0005*self.board.N
        self.return_delay = 0

        depth = 1
        best_score = None

        while time.time() - self.timer_beg + 0.0002 < self.delay:
            ret, score = self.minimax(depth)
            if best_score is None and ret is not None:
                best_ret = ret
                best_score = score
            elif score >= best_score and ret is not None:
                best_ret = ret
                best_score = score
            depth += 1

        print(time.time()- self.timer_beg)
        assert time.time()- self.timer_beg < self.delay
        print(best_ret, best_score)
        return best_ret

    def minimax(self, depth=2, maximizing=True):
        """
        Détermine le coup optimal à jouer selon l'algorithme minimax.

        Args:
            depth (int): la profondeur à explorer dans l'arbre des coups possibles
            maximizing (bool): True si on cherche à maximiser le score et False si on cherche à le maximiser

        Returns:
            Action: le meilleur coup trouvé dans la profondeur explorée
        """
        if time.time() - self.timer_beg + self.return_delay >= self.delay:
             return (None, 0)
        if depth == 0:
            return (None, self.objective_function())
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
                self.return_delay += self.return_single_delay
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
        score, current, other = 0, 0, 0
        alone = True
        components, components_ids = self.board.label_components()
        for component in components:
            player, count = self.board.count_queens(component)
            if player == self.player_id and count != 0:
                # print(player, count, self.board)
                current += (len(component)-count)/count
            elif player == self.other_player_id and count != 0:
                other += (len(component)-count)/count
            else:
                alone = False
                score += self.movements_component(component)
        if alone:
            if current > other:
                score += 1000
            elif current < other:
                score -= 1000
        if current == 0:
            score -= 1000
        elif other == 0:
            score += 1000
        return score + current - other

    def movements_component(self, component):
        score, current, other = 0, 0, 0
        current_queens = set(component) & set(self.board.queens[self.player_id])
        opponent_queens = set(component) & set(self.board.queens[self.other_player_id])
        for queen in current_queens:
            test = self.board._possible_moves_from(queen)
            if next(test, None) is not None:
                for move in self.board._possible_moves_from(queen):
                    for arrow_move in self.board._possible_moves_from(move, ignore=queen):
                        current += 1
            else:
                score -= 100
        for queen in opponent_queens:
            test = self.board._possible_moves_from(queen)
            if next(test, None) is not None:
                for move in self.board._possible_moves_from(queen):
                    for arrow_move in self.board._possible_moves_from(move, ignore=queen):
                        other += 1
            else:
                score += 100
        # print(self.board, current, other)
        # if current == 0:
        #     score -= 100
        # elif other == 0:
        #     score += 100
        return score + current - other
