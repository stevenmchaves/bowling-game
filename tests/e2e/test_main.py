import pytest
from main import main

# Full End to End tests for the bowling game application.

def test_successful_example_game(monkeypatch, capsys, example_game_input):
    inputs = iter([example_game_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0  # Successful status code
    captured = capsys.readouterr().out
    
    output_string = "\n" + "=" * 68
    assert output_string in captured
    assert captured.count(output_string) == 2, f"Expected to see {output_string} twice"
    assert " FRAME:   1     2     3     4     5     6     7     8     9     10" in captured
    assert "-" * 68 in captured
    assert " ROLLS:  8 /   5 4   9 0   X     X     5 /   5 3   6 3   9 /   9 / X" in captured
    assert " SCORE:  15    24    33    58    78    93    101   110   129   149" in captured

def test_perfect_game(monkeypatch, capsys, perfect_game_input):
    inputs = iter([perfect_game_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0  # Successful status code
    captured = capsys.readouterr().out
    
    output_string = "\n" + "=" * 68
    assert output_string in captured
    assert captured.count(output_string) == 2, f"Expected to see {output_string} twice"
    assert " FRAME:   1     2     3     4     5     6     7     8     9     10" in captured
    assert "-" * 68 in captured
    assert " ROLLS:  X     X     X     X     X     X     X     X     X     X X X" in captured
    assert " SCORE:  30    60    90    120   150   180   210   240   270   300" in captured


def test_all_spares(monkeypatch, capsys, all_spares_game_input):
    inputs = iter([all_spares_game_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0  # Successful status code
    captured = capsys.readouterr().out
    
    output_string = "\n" + "=" * 68
    assert output_string in captured
    assert captured.count(output_string) == 2, f"Expected to see {output_string} twice"
    assert " FRAME:   1     2     3     4     5     6     7     8     9     10" in captured
    assert "-" * 68 in captured
    assert " ROLLS:  5 /   5 /   5 /   5 /   5 /   5 /   5 /   5 /   5 /   5 / 5" in captured
    assert " SCORE:  15    30    45    60    75    90    105   120   135   150" in captured

def test_all_open_frames(monkeypatch, capsys, all_open_frames_game_input):
    inputs = iter([all_open_frames_game_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0  # Successful status code
    captured = capsys.readouterr().out
    
    output_string = "\n" + "=" * 68
    assert output_string in captured
    assert captured.count(output_string) == 2, f"Expected to see {output_string} twice"
    assert " FRAME:   1     2     3     4     5     6     7     8     9     10" in captured
    assert "-" * 68 in captured
    assert " ROLLS:  5 1   5 2   5 3   5 4   6 1   6 2   6 3   7 1   7 2   4 0" in captured
    assert " SCORE:  6     13    21    30    37    45    54    62    71    75" in captured

def test_strike_bonus_rolls_tenth_frame(monkeypatch, capsys, strike_bonus_rolls_tenth_input):
    inputs = iter([strike_bonus_rolls_tenth_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0  # Successful status code
    captured = capsys.readouterr().out
    
    output_string = "\n" + "=" * 68
    assert output_string in captured
    assert captured.count(output_string) == 2, f"Expected to see {output_string} twice"
    assert " FRAME:   1     2     3     4     5     6     7     8     9     10" in captured
    assert "-" * 68 in captured
    assert " ROLLS:  8 /   4 3   7 1   X     X     7 /   5 4   1 3   9 /   X 3 3" in captured
    assert " SCORE:  14    21    29    56    76    91    100   104   124   140" in captured

def test_spare_bonus_roll_tenth_frame(monkeypatch, capsys, spare_bonus_roll_tenth_input):
    inputs = iter([spare_bonus_roll_tenth_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0  # Successful status code
    captured = capsys.readouterr().out
    
    output_string = "\n" + "=" * 68
    assert output_string in captured
    assert captured.count(output_string) == 2, f"Expected to see {output_string} twice"
    assert " FRAME:   1     2     3     4     5     6     7     8     9     10" in captured
    assert "-" * 68 in captured
    assert " ROLLS:  8 /   4 3   7 1   X     X     7 /   5 4   1 3   9 /   9 / 3" in captured
    assert " SCORE:  14    21    29    56    76    91    100   104   123   136" in captured

def test_open_frame_tenth_frame(monkeypatch, capsys, open_frame_tenth_input):
    inputs = iter([open_frame_tenth_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0  # Successful status code
    captured = capsys.readouterr().out
    
    output_string = "\n" + "=" * 68
    assert output_string in captured
    assert captured.count(output_string) == 2, f"Expected to see {output_string} twice"
    assert " FRAME:   1     2     3     4     5     6     7     8     9     10" in captured
    assert "-" * 68 in captured
    assert " ROLLS:  8 /   4 3   7 1   X     X     7 /   5 4   1 3   9 /   6 0" in captured
    assert " SCORE:  14    21    29    56    76    91    100   104   120   126" in captured

def test_no_input_failure_exits(monkeypatch, capsys):
    """Verifies No Input and terminates with an error code."""
    monkeypatch.setattr("builtins.input", lambda _: "")

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1  # Error exit status code
    captured = capsys.readouterr().out
    assert "" in captured

def test_spare_first_roll_exits(monkeypatch, capsys, spare_first_roll_input):
    inputs = iter([spare_first_roll_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 3 # Error exit status code on json.loads
    captured = capsys.readouterr().out
    assert "Frame 1: A frame cannot start with a spare ('/')." in captured

def test_invalid_char_exits(monkeypatch, capsys, invalid_character_input):
    inputs = iter([invalid_character_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 3 # Error exit status code on json.loads
    captured = capsys.readouterr().out
    assert "Input Rule Validation Failed -> Frame 1, roll 1: Unsupported character 'W'." in captured

def test_too_many_rolls_tenth_frame(monkeypatch, capsys, too_many_rolls_tenth_input):
    inputs = iter([too_many_rolls_tenth_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 3 # Error exit status code on json.loads
    captured = capsys.readouterr().out
    assert "Input Rule Validation Failed -> Frame 10: An open frame must have exactly 2 rolls." in captured

def test_frame_pin_count_exceeds_ten_without_spare(monkeypatch, capsys, frame_pin_count_no_spare_input):
    inputs = iter([frame_pin_count_no_spare_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 3 # Error exit status code on json.loads
    captured = capsys.readouterr().out
    assert "Input Rule Validation Failed -> Frame 2: Total pins knocked down cannot exceed 10 pins." in captured

def test_extra_rolls_after_game_completed(monkeypatch, capsys, extra_rolls_game_completion_input):
    inputs = iter([extra_rolls_game_completion_input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 3 # Error exit status code on json.loads
    captured = capsys.readouterr().out
    assert "Input Rule Validation Failed -> A complete game must have exactly 10 frames. Received 11 frames." in captured

def test_invalid_json_failure_exits(monkeypatch, capsys):
    """Verifies that bad json input prints an error message and terminates with an error code."""
    monkeypatch.setattr("builtins.input", lambda _: "{'cause': 'json_load_error'}")

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2  # Error exit status code on json.loads
    captured = capsys.readouterr().out
    assert "JSON Syntax Error" in captured
