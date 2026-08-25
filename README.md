# bowling-game

This repo creates a Python application that scores a bowling game. There are
unit, integration, and e2e tests available utilizing pytest.

## Setup

Application was created within a ChromeOS Linux environment utizing Python
3.13.5 and pip 25.1.1. It is advised to use a virtual environment. The `venv` 
 library was used for the virtual environment. Environment can be setup by 
 executing: `pip install -r requirements.txt` at the root directory.

## Input

Style A - Frames was choosen. This was easier to score by utilizing a nested
list structure.

### Acceptable Input Values
- An "x" or "X" for a Strike
- An "/" for a spare
- 0-9 for each shot if its not a strike or spare

## Output

I decided not to support partially completed games. If the game isn't 
completed, you will see a messaged like the following:
```
Input Rule Validation Failed -> A complete game must have exactly 10 frames. Received 9 frames.
```
Otherwise, the ouput will be like the following:
```
=================== Bowling Game Final Scoreboard ===================

====================================================================
 FRAME:   1     2     3     4     5     6     7     8     9     10
--------------------------------------------------------------------
 ROLLS:  8 /   5 4   9 0   X     X     5 /   5 3   6 3   9 /   9 / X
 SCORE:  15    24    33    58    78    93    101   110   129   149

====================================================================
```

## Execution

All the Testing Requirements use cases can be executed by executing:
```
pytest tests/e2e/test_main.py
```
Each test case name is self explainatory.

To execute the actual program, it can be executed by entering: `python main.py`
at the root directory.
At the "Enter the bowling frames JSON:" prompt, the expected format is:
```
[["8", "/"], ["5", "4"], ["9", "0"], ["X"], ["X"], ["5", "/"], ["5", "3"], ["6", "3"], ["9", "/"], ["9", "/", "X"]]
```

The output will look something like the following:
```

====================================================================
 FRAME:   1     2     3     4     5     6     7     8     9     10
--------------------------------------------------------------------
 ROLLS:  8 /   5 4   9 0   X     X     5 /   5 3   6 3   9 /   9 / X
 SCORE:  15    24    33    58    78    93    101   110   129   149

====================================================================

```

There are 4 possible exit codes:
1) 0 - successful execution
1) 1 - No user input
1) 2 - JSON Decode Error
1) 3 - Input Rule Validation Error

## Validation Requirements

Implementation validates input and raises a exception such as ValueError for invalid
games. At minimum, the application handles:

- Spare ("/") cannot be the first roll of a frame.
- Frame totals cannot exceed 10 unless the second roll is a spare indicator
- 10th frame extra rolls ony allowed with strike or spare
- No extra rolls beyond a complete game
- Invalid symbols - anything other than X/x, /, 0-9

## Testing - pytest

I did incorporate test coverage.

1) Provided example game
 - Input:  [ "8", "/", "5", "4", "9", "0", "X", "X", "5", "/", "5", "3", "6", "3", "9". "/", "9", "/", "X" ]
 - Output: [15, 24, 33, 58, 78, 93, 101, 110, 129, 149]

1) Perfect Game - 12 strikes - returns 300

1) All Spares - bonus 5 - returns 150

1) All open frames

1) 10th frame behavior:
 - Strike + 2 bonus rolls
 - Spare + 1 bonus roll
 - Open frame

1) Validation tests
 - Spare in first roll
 - Invalid character
 - Too many rolls in 10th
 - frame pin count exceeds 10 w/o spare
 - extra rolls after game completion




