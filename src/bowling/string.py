from typing import List, Dict

class BowlingGame:
    """Pure scoring calculations engine for pre-validated numerical bowling data."""

    def __init__(self, raw_frames: List[List[str]], numerical_game: List[List[int]]) -> None:
        self.raw_frames = raw_frames
        # Flatten frames into a continuous roll timeline for easy score index lookups
        self._rolls: List[int] = [roll for frame in numerical_game for roll in frame]

    def score(self) -> int:
        """Returns the final computed score."""
        return self.get_scoreboard_data()["cumulative_scores"][-1]

    def get_scoreboard_data(self) -> Dict[str, list]:
        """Generates real-time tracking points for rendering output grids."""
        cumulative_scores: List[int] = []
        display_frames: List[List[str]] = []
        
        total_score = 0
        roll_index = 0

        for frame_idx in range(10):
            if self._rolls[roll_index] == 10:  # Strike
                total_score += 10 + self._rolls[roll_index + 1] + self._rolls[roll_index + 2]
                roll_index += 1
            elif self._rolls[roll_index] + self._rolls[roll_index + 1] == 10:  # Spare
                total_score += 10 + self._rolls[roll_index + 2]
                roll_index += 2
            else:  # Open frame
                total_score += self._rolls[roll_index] + self._rolls[roll_index + 1]
                roll_index += 2
            
            cumulative_scores.append(total_score)

            # Map the exact layout labels
            clean_frame = [token.strip().upper() for token in self.raw_frames[frame_idx]]
            if frame_idx < 9 and "X" in clean_frame and len(clean_frame) == 1:
                clean_frame.append("_")
            display_frames.append(clean_frame)

        return {
            "cumulative_scores": cumulative_scores,
            "display_frames": display_frames
        }

