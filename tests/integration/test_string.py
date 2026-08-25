import pytest
import json
from bowling.frame_parser import FrameParser
from bowling.bowling_rules_validator import BowlingRulesValidator
from bowling.string import BowlingGame

@pytest.mark.parametrize(
    "raw_json, expected_score",
    [
        ('[["8", "/"], ["5", "4"], ["9", "0"], ["X"], ["X"], ["5", "/"], ["5", "3"], ["6", "3"], ["9", "/"], ["9", "/", "X"]]', 149),
        ('[["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X", "X", "X"]]', 300),
        ('[["0", "0"]] * 10', 0),
        ('[["3", "4"]] * 10', 70)
    ]
)
def test_complete_scoring_pipeline(raw_json, expected_score):
    # If using string multiplication syntax like '[["-", "-"]] * 10', patch via json load or hardcode arrays
    if " * " in raw_json:
        base, multiplier = raw_json.split(" * ")
        raw_frames = json.loads(base) * int(multiplier)
    else:
        raw_frames = json.loads(raw_json)

    numerical_game = FrameParser.parse_to_numbers(raw_frames)
    BowlingRulesValidator.validate_game(numerical_game)
    game = BowlingGame(raw_frames, numerical_game)
    
    assert game.score() == expected_score

