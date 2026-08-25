import json
import sys

from bowling.frame_parser import FrameParser
from bowling.bowling_rules_validator import BowlingRulesValidator
from bowling.string import BowlingGame

def game_pipeline(raw_json: str) -> BowlingGame:
    """Parsing, validation, and scoring steps into pipeline.
    Args:
        raw_json (str): The raw JSON string input representing the bowling frames.
    Returns:
        BowlingGame: An instance of the BowlingGame class containing the parsed and validated game data.
    Raises:
        ValueError: If the input JSON is invalid or does not conform to bowling rules.
    """
    # Step 1: String Parsing
    raw_frames = json.loads(raw_json)
    # convert to numerical representation for validation and scoring
    numerical_game = FrameParser.parse_to_numbers(raw_frames)
    
    # Step 2: Input Rule Validation 
    BowlingRulesValidator.validate_game(numerical_game)
    
    # Step 3: Calculate Game Initial State
    return BowlingGame(raw_frames, numerical_game)

def print_gameboard(game: BowlingGame):
    """
    Prints the bowling score of a game
    Args:
        game (BowlingGame): The BowlingGame instance containing the game data.
    """

    # Get the scoreboard data from the game instance
    data = game.get_scoreboard_data()
    # Extract the cumulative scores and display frames
    scores = data["cumulative_scores"]
    # Extract the display frames for printing
    frames = data["display_frames"]
    
    format_rolls = []

    for frame_index, f in enumerate(frames):
        # Format the rolls for each frame, ensuring proper alignment and spacing
        if frame_index < 9:
            # first 9 frames
            rolls_str = " ".join(f).replace("_", " ")
            format_rolls.append(f"{rolls_str:<3}")
        else:
            # last frame
            rolls_str = " ".join(f)
            format_rolls.append(f"{rolls_str:<5}")

    # Create the formatted lines for frames, rolls, and scores
    frames_line = " FRAME:   " + "     ".join(f"{i}" for i in range(1, 10)) + "     10"
    rolls_line = " ROLLS:  " + "   ".join(format_rolls)

    # Score String padding
    score_line_list = []
    
    for score_index, score in enumerate(scores):
        # Format the score for each frame, ensuring proper alignment and spacing
        if score_index < 9:
            # found this to be the best way to align the scores for the first 9 frames
            score_line_list.append(f"{score:<4}")
        else:
            # last frame - because of extra rolls
            score_line_list.append(f"{score:<5}")
    
    # Create the final score line for printing
    final_score_line = " SCORE:  " + "  ".join(score_line_list)

    print("\n" + "=" * 19 + " Bowling Game Final Scoreboard " + "=" * 19)
    print("\n" + "=" * 68)
    print(frames_line)
    print("-" * 68)
    print(rolls_line.rstrip())
    print(final_score_line.rstrip())
    print("\n" + "=" * 68)

def main() -> None:
    """Main function to run the bowling game application."""

    # Print the application header
    print("=" * 27 + " Bowling Game Application " + "=" * 27 + "\n")
    print("*" * 80 + "\n")
    
    try:
        # Prompt the user for input and process the bowling game
        user_raw = input("\nEnter your bowling frames JSON: ").strip()
        if not user_raw:
            # Handle empty input gracefully
            print("No input entered. Terminating application.")
            sys.exit(1)

        # Process the input through the game pipeline
        game_instance = game_pipeline(user_raw)
        # Print the final gameboard with scores
        print_gameboard(game_instance)
        
        # Exit gracefully
        sys.exit(0)
            
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors and exit with a specific error code
        print(f"JSON Syntax Error: {e}")
        sys.exit(2)
    except ValueError as e:
        # Handle validation errors and exit with a specific error code``
        print(f"Input Rule Validation Failed -> {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()

