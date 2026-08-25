from typing import List

class FrameParser:
    """Handles parsing string frames into numbers."""

    @staticmethod
    def parse_to_numbers(frames: List[List[str]]) -> List[List[int]]:
        """Transforms a nested array of string tokens (rolls) into standard numeric lists."""
        if not isinstance(frames, list):
            # Input parameter must be a list
            raise ValueError("Input parameter must be a list.")

        numerical_game: List[List[int]] = []

        for i, frame in enumerate(frames):
            # Validate that each frame
            frame_num = i + 1
            if not isinstance(frame, list):
                # Nested list validation
                raise ValueError(f"Frame {frame_num}: Must be a nested list.")

            numerical_frame: List[int] = []
            for j, raw_char in enumerate(frame):
                # Validate that each roll is a string
                if not isinstance(raw_char, str):
                    # Roll token validation - Needs to be a string
                    raise ValueError(f"Frame {frame_num}, roll {j+1}: Token must be a string.")
                
                clean_char = raw_char.strip().upper()
            
                if clean_char == "X":
                    # Handle strike
                    numerical_frame.append(10)
                elif clean_char == "/":
                    # Handle spare
                    if j == 0:
                        # A frame cannot start with a spare validation
                        raise ValueError(f"Frame {frame_num}: A frame cannot start with a spare ('/').")
                    prev_roll = numerical_frame[j - 1]
                    numerical_frame.append(10 - prev_roll)
                elif clean_char.isdigit():
                    numerical_frame.append(int(clean_char))
                else:
                    # Unsupported character validation
                    raise ValueError(f"Frame {frame_num}, roll {j+1}: Unsupported character '{clean_char}'.")

            numerical_game.append(numerical_frame)

        return numerical_game

