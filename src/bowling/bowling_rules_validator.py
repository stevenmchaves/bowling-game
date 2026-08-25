from typing import List

class BowlingRulesValidator:
    """Enforces Input validation for bowling rules."""

    @staticmethod
    def validate_game(numerical_game: List[List[int]]) -> bool:
        """Validates all game rules and pin capacities.
        Full Game is 10 frames.
        Does not support games with more or less (partial games) than 10 frames.
        Args:
            numerical_game (List[List[int]]): A list of frames, where each frame is a list of rolls represented as integers.
        Returns:
            bool: True if the game is valid, raises ValueError otherwise.
        Raises:
            ValueError: If the game does not conform to bowling rules.
        """
        if len(numerical_game) != 10:
            # Not supporting games with more or less than 10 frames
            raise ValueError(f"A complete game must have exactly 10 frames. Received {len(numerical_game)} frames.")

        for i, frame in enumerate(numerical_game):
            # Validate each frame
            frame_num = i + 1
            
            if len(frame) == 0:
                # Missing rolls in a frame
                raise ValueError(f"Frame {frame_num}: Frame cannot be empty. Missing rolls in a frame.")
            
            # Rules for Frames 1-9
            if frame_num < 10:
                if len(frame) > 2:
                    # Too many rolls
                    raise ValueError(f"Frame {frame_num}: Frames: 1-9 cannot contain more than 2 rolls.")
                if len(frame) == 2 and sum(frame) > 10:
                    # Total pins knocked down exceeds 10
                    raise ValueError(f"Frame {frame_num}: Total pins knocked down cannot exceed 10 pins.")
                if frame[0] == 10 and len(frame) > 1:
                    # A strike must stand alone for frames 1-9
                    raise ValueError(f"Frame {frame_num}: A strike ('X') must stand alone in frames 1-9.")

            # Rules for the 10th Final Frame
            else:
                if len(frame) > 3:
                    # Too many rolls in the final frame
                    raise ValueError("Frame 10: Final Frame cannot contain more than 3 rolls.")
                
                first_roll = frame[0]
                if first_roll == 10:  
                    # Strike in 10th
                    if len(frame) < 3:
                        # Not enough bonus rolls for a strike
                        raise ValueError("Frame 10: Getting a strike requires 2 additional bonus rolls.")
                    if frame[1] != 10 and (frame[1] + frame[2] > 10) and (frame[1] + frame[2] != 20):
                        # Accounts for normal rolls or a consecutive spare conversion in bonus fields
                        if frame[2] != 10 - frame[1]: 
                            # If the second roll is not a strike, the third roll cannot exceed the remaining pins unless it's a spare conversion
                            raise ValueError("Frame 10: Bonus rolls cannot exceed 10 pins combined unless executing a spare choice.")
                elif len(frame) >= 2 and (frame[0] + frame[1] == 10):  
                    # Spare in 10th
                    if len(frame) < 3:
                        # Not enough bonus rolls for a spare
                        raise ValueError("Frame 10: Getting a spare requires 1 additional bonus roll.")
                else:  
                    # Open frame in 10th
                    if len(frame) != 2:
                        # Not enough rolls for an open frame
                        raise ValueError("Frame 10: An open frame must have exactly 2 rolls.")
                    if sum(frame) > 10:
                        # Total pins knocked down exceeds 10 for an open frame
                        raise ValueError("Frame 10: Total open frame score cannot exceed 10 pins.")
        return True
