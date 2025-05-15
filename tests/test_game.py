import pytest
from src.py.game import Hangman, HangmanGameState, GamePhase, GuessLetterAction, RandomPlayer

class TestHangmanGameState:

    @pytest.fixture
    def game_state_running(self):
        return HangmanGameState(
            word_to_guess="DEVOPS",
            phase=GamePhase.RUNNING,
            guesses=["E", "O", "A", "I", "S"],
            incorrect_guesses=["A", "I"],
        )

    @pytest.fixture
    def game_state_finished_lose(self):
        return HangmanGameState(
            word_to_guess="DEVOPS",
            phase=GamePhase.FINISHED,
            guesses=["D", "E", "V", "A", "I", "U", "T", "M", "N", "L", "G"],
            incorrect_guesses=["A", "I", "U", "T", "M", "N", "L", "G"],
        )

    def test_str_running(self, game_state_running):
        output = str(game_state_running)
        assert "Phase: running" in output
        assert "Word to guess: DEVOPS" in output
        assert "|     O" in output
        assert "All guesses: E O A I S" in output
        assert "Incorrect guesses: A I" in output

    def test_str_finished_lose(self, game_state_finished_lose):
        output = str(game_state_finished_lose)
        assert "Phase: finished" in output
        assert "Word to guess: DEVOPS" in output
        assert "|/    |" in output
        assert "All guesses: D E V A I U T M N L G" in output
        assert "Incorrect guesses: A I U T M N L G" in output

class TestHangman:

    @pytest.fixture
    def random_game_state(self):
        return HangmanGameState(
            word_to_guess="DEVOPS",
            phase=GamePhase.RUNNING,
            guesses=["E", "O", "S", "A"],
            incorrect_guesses=["A"]
        )

    @pytest.fixture
    def game(self, random_game_state):
        new_game = Hangman()
        new_game.set_state(random_game_state)
        return new_game

    def test_get_list_action(self, game, random_game_state):
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F',
                    'G', 'H', 'I', 'J', 'K', 'L',
                    'M', 'N', 'O', 'P', 'Q', 'R',
                    'S', 'T', 'U', 'V', 'W', 'X',
                    'Y', 'Z']
        expected_letters = [l for l in alphabet if l not in random_game_state.guesses]
        actions = game.get_list_action()
        action_letters = [action.letter for action in actions]

        assert sorted(action_letters) == sorted(expected_letters)


    def test_apply_correct_guess(self, game):
        game.apply_action(GuessLetterAction(letter = "V"))

        state = game.get_state()
        assert "V" in state.guesses
        assert "V" not in state.incorrect_guesses
        assert state.phase == GamePhase.RUNNING


    def test_apply_incorrect_guess(self, game):
        game.apply_action(GuessLetterAction(letter = "Z"))

        state = game.get_state()
        assert "Z" in state.guesses
        assert "Z" in state.incorrect_guesses
        assert state.phase == GamePhase.RUNNING


    def test_apply_repeated_guess(self, game):
        with pytest.raises(ValueError, match="Invalid or repeated guess."):
            game.apply_action(GuessLetterAction(letter="E"))


    def test_win_game(self, game):
        game.apply_action(GuessLetterAction(letter = "D"))
        game.apply_action(GuessLetterAction(letter = "V"))
        game.apply_action(GuessLetterAction(letter = "P"))
        state = game.get_state()

        assert state.phase == GamePhase.FINISHED

    def test_lose_game(self, game):
        game.apply_action(GuessLetterAction(letter = "B"))
        game.apply_action(GuessLetterAction(letter = "C"))
        game.apply_action(GuessLetterAction(letter = "F"))
        game.apply_action(GuessLetterAction(letter = "G"))
        game.apply_action(GuessLetterAction(letter = "I"))
        game.apply_action(GuessLetterAction(letter = "H"))
        game.apply_action(GuessLetterAction(letter = "Z"))

        state = game.get_state()
        assert state.phase == GamePhase.FINISHED
        assert "Z" in state.incorrect_guesses


    def test_get_player_view(self, random_game_state, game):
        expected_game_state = HangmanGameState(
            word_to_guess="_E_O_S",
            phase=random_game_state.phase,
            guesses=random_game_state.guesses,
            incorrect_guesses=random_game_state.incorrect_guesses
        )

        actual_state = game.get_player_view(_idx_player=1)
        assert actual_state == expected_game_state


class TestRandomPlayer:

    @pytest.fixture
    def random_game_state(self):
        return HangmanGameState(
            word_to_guess="DEVOPS",
            phase=GamePhase.RUNNING,
            guesses=["E", "O", "S", "A"],
            incorrect_guesses=["A"]
        )

    def test_select_action_returns_valid_choice(self, random_game_state):
        player = RandomPlayer()
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F',
                         'G', 'H', 'I', 'J', 'K', 'L',
                         'M', 'N', 'O', 'P', 'Q', 'R',
                         'S', 'T', 'U', 'V', 'W', 'X',
                         'Y', 'Z']
        remaining_letters = [l for l in alphabet if l not in random_game_state.guesses]
        actions = [GuessLetterAction(letter=l) for l in remaining_letters]
        selected = player.select_action(random_game_state, actions)
        assert selected in actions

    def test_select_action_raises_exception(self, random_game_state):
        player = RandomPlayer()
        with pytest.raises(ValueError, match="There are no actions to choose from"):
            player.select_action(random_game_state, [])
