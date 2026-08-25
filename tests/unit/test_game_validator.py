import pytest
import re

from bowling.bowling_rules_validator import BowlingRulesValidator

# Happy Path Tests

def test_accepts_valid_game():
    valid_game = [[7, 2], [5, 4], [9, 0], [10], [10], [5, 5], [5, 3], [6, 3], [9, 1], [9, 1, 10]]
    # Should run cleanly without raising errors
    assert BowlingRulesValidator.validate_game(valid_game)

# Negative Path  / Edge Case Tests

def test_catches_exceeded_pins_in_mid_frames():
    invalid_game = [[1, 2], [7, 7], [1, 0], [1], [1], [1, 5], [1, 3], [1, 3], [9, 1], [9, 1, 10]]
    with pytest.raises(ValueError, match="Frame 2: Total pins knocked down cannot exceed 10 pins."):
        BowlingRulesValidator.validate_game(invalid_game)

def test_catches_empty_frame():
    invalid_game = [[], [7, 7], [1, 0], [1], [1], [1, 5], [1, 3], [1, 3], [9, 1], [9, 1, 10]]
    with pytest.raises(ValueError, match="Frame 1: Frame cannot be empty. Missing rolls in a frame."):
        BowlingRulesValidator.validate_game(invalid_game)

def test_catches_no_frames():
    invalid_game = []
    with pytest.raises(ValueError, match="A complete game must have exactly 10 frames. Received 0 frames."):
        BowlingRulesValidator.validate_game(invalid_game)

def test_catches_invalid_strike_frame():
    invalid_game = [[7, 2], [5, 4], [9, 0], [10, 0], [10], [5, 5], [5, 3], [6, 3], [9, 1], [9, 1, 10]]
    with pytest.raises(ValueError, match=re.escape("Frame 4: A strike ('X') must stand alone in frames 1-9.")):
        BowlingRulesValidator.validate_game(invalid_game)

def test_catches_exceeded_three_rolls():
    invalid_game = [[1, 2, 3], [7, 7], [1, 0], [1], [1], [1, 5], [1, 3], [1, 3], [9, 1], [9, 1, 10]]
    with pytest.raises(ValueError, match="Frame 1: Frames: 1-9 cannot contain more than 2 rolls."):
        BowlingRulesValidator.validate_game(invalid_game)

def test_invalid_game_missing_frames():
    incomplete_10th = [[1, 4]] * 5 + [[10]]  # Only 6 frames
    with pytest.raises(ValueError, match="A complete game must have exactly 10 frames. Received 6 frames."):
        BowlingRulesValidator.validate_game(incomplete_10th)

def test_catches_missing_bonus_rolls_in_frame_10():
    incomplete_10th = [[1, 1]] * 9 + [[10]]  # Strike with no bonus rolls
    with pytest.raises(ValueError, match="Frame 10: Getting a strike requires 2 additional bonus rolls."):
        BowlingRulesValidator.validate_game(incomplete_10th)

def test_too_many_bonus_rolls_in_frame_10():
    incomplete_10th = [[1, 1]] * 9 + [[10, 1, 1, 1]]  # Strike with no bonus rolls
    with pytest.raises(ValueError, match="Frame 10: Final Frame cannot contain more than 3 rolls."):
        BowlingRulesValidator.validate_game(incomplete_10th)

def test_strike_exceed_ten_in_frame_10():
    incomplete_10th = [[1, 1]] * 9 + [[10, 2, 9]]  # Strike exceeds 10
    with pytest.raises(ValueError, match="Frame 10: Bonus rolls cannot exceed 10 pins combined unless executing a spare."):
        BowlingRulesValidator.validate_game(incomplete_10th)

def test_missing_bonus_roll_spare_in_frame_10():
    incomplete_10th = [[1, 1]] * 9 + [[1, 9]]  # Spare with no bonus rolls
    with pytest.raises(ValueError, match="Frame 10: Getting a spare requires 1 additional bonus roll."):
        BowlingRulesValidator.validate_game(incomplete_10th)

def test_open_frame_exceed_ten_in_frame_10():
    incomplete_10th = [[1, 1]] * 9 + [[2, 9]]  # Open Frame exceeds 10
    with pytest.raises(ValueError, match="Frame 10: Total open frame score cannot exceed 10 pins."):
        BowlingRulesValidator.validate_game(incomplete_10th)

def test_open_frame_missing_roll_in_frame_10():
    incomplete_10th = [[1, 1]] * 9 + [[1]]  # Open frame missing roll
    with pytest.raises(ValueError, match="Frame 10: An open frame must have exactly 2 rolls."):
        BowlingRulesValidator.validate_game(incomplete_10th)

