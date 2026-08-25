import pytest

@pytest.fixture
def example_game_input():
    """The example user input"""
    return '[["8", "/"], ["5", "4"], ["9", "0"], ["X"], ["X"], ["5", "/"], ["5", "3"], ["6", "3"], ["9", "/"], ["9", "/", "X"]]'

@pytest.fixture
def perfect_game_input():
    return '[["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X", "X", "X"]]'

@pytest.fixture
def all_spares_game_input():
    """The example user input"""
    return '[["5", "/"], ["5", "/"], ["5", "/"], ["5", "/"], ["5", "/"], ["5", "/"], ["5", "/"], ["5", "/"], ["5", "/"], ["5", "/", "5"]]'

@pytest.fixture
def all_open_frames_game_input():
    """The example user input"""
    return '[["5", "1"], ["5", "2"], ["5", "3"], ["5", "4"], ["6", "1"], ["6", "2"], ["6", "3"], ["7", "1"], ["7", "2"], ["4", "0"]]'

@pytest.fixture
def strike_bonus_rolls_tenth_input():
    return '[["8", "/"], ["4", "3"], ["7", "1"], ["X"], ["X"], ["7", "/"], ["5", "4"], ["1", "3"], ["9", "/"], ["X", "3", "3"]]'

@pytest.fixture
def spare_bonus_roll_tenth_input():
    return '[["8", "/"], ["4", "3"], ["7", "1"], ["X"], ["X"], ["7", "/"], ["5", "4"], ["1", "3"], ["9", "/"], ["9", "/", "3"]]'

@pytest.fixture
def open_frame_tenth_input():
    return '[["8", "/"], ["4", "3"], ["7", "1"], ["X"], ["X"], ["7", "/"], ["5", "4"], ["1", "3"], ["9", "/"], ["6", "0"]]'

@pytest.fixture
def spare_first_roll_input():
    return '[["/", "2"], ["4", "2"], ["7", "1"], ["X"], ["X"], ["7", "/"], ["5", "4"], ["1", "3"], ["9", "/"], ["9", "/", "X"]]'

@pytest.fixture
def invalid_character_input():
    return '[["W", "/"], ["4", "9"], ["7", "1"], ["X"], ["X"], ["7", "/"], ["5", "4"], ["1", "3"], ["9", "/"], ["9", "/", "X"]]'

@pytest.fixture
def too_many_rolls_tenth_input():
    return '[["8", "/"], ["4", "3"], ["7", "1"], ["X"], ["X"], ["7", "/"], ["5", "4"], ["1", "3"], ["9", "/"], ["2", "1", "2"]]'

@pytest.fixture
def frame_pin_count_no_spare_input():
    return '[["8", "/"], ["4", "9"], ["7", "1"], ["X"], ["X"], ["7", "/"], ["5", "4"], ["1", "3"], ["9", "/"], ["9", "/", "X"]]'

@pytest.fixture
def extra_rolls_game_completion_input():
    return '[["8", "/"], ["4", "3"], ["7", "1"], ["X"], ["X"], ["7", "/"], ["5", "4"], ["1", "3"], ["9", "/"], ["9", "/", "X"],["3"]]'

