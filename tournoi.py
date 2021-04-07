"""
Prénom: Boris
Nom: Petrov
Matricule: 000515795
"""

from players import Player
from action import Action
from const import *
import time
import random

class TournoiAIPlayer(Player):
    """IA qui jouera au tournoi.

    Améliorations:
        L'amélioration principale est dans le fonction objective_function.
        Dans cette dernière, 
    """
    def __init__(self, board, player_id):
        super().__init__(board, player_id)

    def _play(self, coup=None, delay=2):
        """
        Détermine le meilleur coup à jouer

        Returns:
            Action: le meilleur coup déterminé via minimax
        """
        self.timer_beg = time.time()  # début du timer
        self.delay = delay

        self.return_single_delay = 0.005*self.board.N
        self.return_delay = 0  # délais pour resortir de minimax

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
        # print(self.accessible_cells())
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
            return (None, self.objective_function(maximizing))
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

    def objective_function(self, maximizing):
        """Retourne une valeur heurisitque à Minimax."""
        score, current, other = 0, 0, 0
        alone = True
        components, components_ids = self.board.label_components()
        for component in components:
            player, count = self.board.count_queens(component)
            if player == self.player_id and count != 0:
                current += (len(component)-count)/count
            elif player == self.other_player_id and count != 0:
                other += (len(component)-count)/count
            else:
                alone = False  # tous pions pas isolés
                score += self.movements_component(component)

        if alone:  # si tous les pions sont isolés
            if current >= other and maximizing:
                score += 100
            elif current < other and not maximizing:
                score -= 100
        print(self.board,score +current-other, score, current, other)
        return (score + current - other)/10

    def movements_component(self, component):
        """Retourne les movements possibles pour chaque reine dans la composante.

        Args:
            component(list): composante présente
        """
        score, current, other = 0, 0, 0
        current_queens = set(component) & set(self.board.queens[self.player_id])
        opponent_queens = set(component) & set(self.board.queens[self.other_player_id])

        for queen in current_queens:
            test = self.board._possible_moves_from(queen)
            if next(test, None) is not None:
                for move in self.board._possible_moves_from(queen):
                    for arrow_move in self.board._possible_moves_from(move, ignore=queen):
                        current += 1
            else:  # si une reine du joueur est bloquée
                score -= 100

        for queen in opponent_queens:
            test = self.board._possible_moves_from(queen)
            if next(test, None) is not None:
                for move in self.board._possible_moves_from(queen):
                    for arrow_move in self.board._possible_moves_from(move, ignore=queen):
                        other += 1
            else:  # si une reine du joueur adverse est bloquée
                score += 100

        return score + current - other
