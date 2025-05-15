import random
from enum import Enum
from typing import List
from pydantic import BaseModel
from src.py.interface import Game, Player


class GuessLetterAction(BaseModel):
    letter: str



class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState(BaseModel):
    word_to_guess: str
    phase: GamePhase
    guesses: List[str]
    incorrect_guesses: List[str]

    class Config:
        use_enum_values = True

    def __str__(self) -> str:
        outstring = f"Phase: {self.phase}\nWord to guess: {self.word_to_guess}\n"
        num_wrong = len(self.incorrect_guesses)
        if num_wrong == 0:
            outstring += "\n\n\n\n\n\n _\n"
        else:
            back = " "
            left_arm = " "
            right_arm = " "
            left_leg = " "
            right_leg = " "
            if num_wrong > 2:
                back = '|'
            if num_wrong > 3:
                left_arm = '/'
            if num_wrong > 4:
                right_arm = '\\'
            if num_wrong > 5:
                left_leg = "/"
            if num_wrong > 6:
                right_leg = "\\"
            outstring += " _______\n"
            outstring += " |/    |\n" if num_wrong > 7 else " |/\n"
            outstring += " |     O\n" if num_wrong > 1 else " |\n"
            outstring += f" |    {left_arm}{back}{right_arm}\n"
            outstring += f" |    {left_leg} {right_leg}\n"
            outstring += " |_\n"
        outstring += f"All guesses: {' '.join(self.guesses)}\n"
        outstring += f"Incorrect guesses: {' '.join(self.incorrect_guesses)}\n"
        return outstring

class Hangman(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        self.state: HangmanGameState = HangmanGameState(
            word_to_guess='DEFAULT',
            phase=GamePhase.SETUP,
            guesses=[],
            incorrect_guesses=[]
        )
        self.alphabet = ['A', 'B', 'C', 'D', 'E', 'F',
                         'G', 'H', 'I', 'J', 'K', 'L',
                         'M', 'N', 'O', 'P', 'Q', 'R',
                         'S', 'T', 'U', 'V', 'W', 'X',
                         'Y', 'Z']

    def get_state(self) -> HangmanGameState:
        """ Get the complete, unmasked game state """
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        self.state = state

    def print_state(self) -> None:
        """ Print the current game state """
        state = self.state
        outstring = str(state)

        print(outstring)

    def get_list_action(self) -> list[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        actionlist = []

        for letter in self.alphabet:
            if letter not in self.state.guesses:
                actionlist.append(GuessLetterAction(letter=letter))  # Pass letter as a keyword argument

        return actionlist

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        current_state = self.get_state()

        # For test 005 because wrong guessed letters are not added to incorrect guesses in setup of state.
        for letter in current_state.guesses:
            if letter not in current_state.word_to_guess.upper():
                if letter not in current_state.incorrect_guesses:
                    current_state.incorrect_guesses.append(letter)

        guessed_letter = action.letter.upper()

        if not guessed_letter.isalpha() or guessed_letter in current_state.guesses:
            raise ValueError("Invalid or repeated guess.")

        current_state.guesses.append(guessed_letter)

        if guessed_letter not in current_state.word_to_guess.upper():
            current_state.incorrect_guesses.append(guessed_letter)


        if len(current_state.incorrect_guesses) >= 8:
            current_state.phase = GamePhase.FINISHED
        elif all(letter.upper() in current_state.guesses for letter in current_state.word_to_guess):
            current_state.phase = GamePhase.FINISHED

        self.set_state(current_state)

    def get_player_view(self, _idx_player: int) -> HangmanGameState:
        """
        Get the masked state for the active player (e.g., the opponent's cards are face down).
        """
        masked_word = ''
        for letter in self.state.word_to_guess:
            if letter.upper() in self.state.guesses:
                masked_word += letter
            else:
                masked_word += '_'

        return HangmanGameState(
            word_to_guess=masked_word,
            phase=self.state.phase,
            guesses=self.state.guesses,
            incorrect_guesses=self.state.incorrect_guesses
        )


class RandomPlayer(Player):

    def select_action(self, _state: HangmanGameState, actions: list[GuessLetterAction]) -> GuessLetterAction:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) == 0:
            raise ValueError('There are no actions to choose from')
        return random.choice(actions)


if __name__ == "__main__":

    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps', phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)
    game.print_state()

    player = RandomPlayer()
    while game_state.phase != GamePhase.FINISHED:
        possible_actions = game.get_list_action()
        next_action = player.select_action(game_state, possible_actions)
        game.apply_action(next_action)
        game.print_state()
        game_state = game.get_state()
        print("\n\n")
