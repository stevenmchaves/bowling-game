import pytest
from bowling.frame_parser import FrameParser

def test_converts_symbols_correctly():
    raw = [["1", "/"], ["X"], ["0", "5"]]
    expected = [[1, 9], [10], [0, 5]]
    assert FrameParser.parse_to_numbers(raw) == expected


@pytest.mark.parametrize(
    "symbol_input",
    [
        ([["-", "/"], ["5", "4"], ["9", "0"], ["X"], ["X"], ["5", "/"], ["5", "3"], ["6", "3"], ["9", "/"], ["9", "/", "X"]]),
        ([["W"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X"], ["X", "X", "X"]]),
        ([["_", "0"]]),
        ([["-3", "4"]])
    ]
)
def test_invalid_tokens(symbol_input):
    with pytest.raises(ValueError, match="Unsupported character"):
        FrameParser.parse_to_numbers(symbol_input)

def test_invalid_list():
    with pytest.raises(ValueError, match="Input parameter must be a list"):
        FrameParser.parse_to_numbers("4")

def test_invalid_nest_list_list():
    with pytest.raises(ValueError, match="Frame 1: Must be a nested list."):
        FrameParser.parse_to_numbers(["4"])

def test_invalid_nest_list_type_list():
    with pytest.raises(ValueError, match="Frame 1, roll 1: Token must be a string."):
        FrameParser.parse_to_numbers([[4]])

def test_rejects_spare_on_first_roll():
    with pytest.raises(ValueError, match="cannot start with a spare"):
        FrameParser.parse_to_numbers([["/", "r"]])

