import json
import os
from typing import Any

from openai import OpenAI


SYSTEM_PROMPT = """You are Bowling Coach, a practical bowling coach inside a bowling score app.

Use the supplied game-analysis tool before giving advice. Never invent frame scores or bowling statistics.
Explain scoring in plain language, identify the biggest opportunities first, and give 1-3 concrete practice suggestions.
You can answer questions about score, strikes, spares, open frames, consistency, and what to practice next.
If the game data is incomplete or invalid, say so rather than pretending the analysis is complete.
Keep responses concise unless the user asks for detail.
"""


def _roll_value(token: str, previous: int | None = None) -> int:
    token = str(token).strip().upper()
    if token == "X":
        return 10
    if token == "/":
        if previous is None:
            raise ValueError("A spare cannot be the first roll of a frame.")
        return 10 - previous
    if token.isdigit() and 0 <= int(token) <= 9:
        return int(token)
    raise ValueError(f"Invalid roll: {token}")


def analyze_bowling_game(frames: list[list[str]]) -> dict[str, Any]:
    """Return deterministic coaching metrics from the game's raw frame notation."""
    if len(frames) != 10:
        return {"valid": False, "error": "A complete game must contain exactly 10 frames."}

    strikes = 0
    spares = 0
    opens = 0
    open_pins = 0
    missed_spare_opportunities = 0
    frame_details: list[dict[str, Any]] = []

    for index, raw_frame in enumerate(frames, start=1):
        frame = [str(x).strip().upper() for x in raw_frame if str(x).strip()]
        if not frame:
            return {"valid": False, "error": f"Frame {index} is empty."}
        try:
            first = _roll_value(frame[0])
            if index < 10:
                if frame[0] == "X":
                    strikes += 1
                    frame_details.append({"frame": index, "type": "strike", "pins": 10})
                    continue
                if len(frame) != 2:
                    return {"valid": False, "error": f"Frame {index} must have two rolls unless it is a strike."}
                second = _roll_value(frame[1], first)
                if frame[1] == "/":
                    spares += 1
                    frame_details.append({"frame": index, "type": "spare", "pins": 10})
                else:
                    total = first + second
                    if total > 10:
                        return {"valid": False, "error": f"Frame {index} exceeds 10 pins."}
                    opens += 1
                    open_pins += 10 - total
                    frame_details.append({"frame": index, "type": "open", "pins": total, "pins_left": 10 - total})
                    if first < 10 and second > 0 and first + second < 10:
                        missed_spare_opportunities += 1
            else:
                # In the 10th frame, every X is a strike roll, including a fill ball
                # after a spare or after a strike on the first ball.
                strikes += sum(1 for roll in frame if roll == "X")
                if frame[0] != "X" and len(frame) >= 2 and frame[1] == "/":
                    spares += 1
                elif frame[0] != "X" and len(frame) >= 2:
                    second = _roll_value(frame[1], first)
                    if first + second < 10:
                        opens += 1
                        open_pins += 10 - (first + second)
                frame_details.append({"frame": index, "rolls": frame, "type": "tenth_frame"})
        except ValueError as exc:
            return {"valid": False, "error": str(exc), "frame": index}

    return {
        "valid": True,
        "strikes": strikes,
        "spares": spares,
        "open_frames": opens,
        "pins_left_in_open_frames": open_pins,
        "missed_spare_opportunities": missed_spare_opportunities,
        "frame_details": frame_details,
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_bowling_game",
            "description": "Analyze the current ten-frame bowling game using deterministic bowling rules.",
            "parameters": {
                "type": "object",
                "properties": {
                    "frames": {
                        "type": "array",
                        "description": "Ten bowling frames, using X for strike and / for spare.",
                        "items": {"type": "array", "items": {"type": "string"}},
                    }
                },
                "required": ["frames"],
                "additionalProperties": False,
            },
        },
    }
]


def coach_response(question: str, frames: list[list[str]], score: int) -> str:
    api_key = os.getenv("AI_GATEWAY_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        analysis = analyze_bowling_game(frames)
        if not analysis.get("valid"):
            return f"I can coach this game once the score is valid. {analysis.get('error', '')}"
        strikes = analysis["strikes"]
        spares = analysis["spares"]
        open_frames = analysis["open_frames"]
        strike_label = "strike" if strikes == 1 else "strikes"
        spare_label = "spare" if spares == 1 else "spares"
        open_label = "open frame" if open_frames == 1 else "open frames"
        if open_frames == 0:
            takeaway = (
                "You avoided open frames, which is great spare shooting. To raise your score, work on "
                "getting more strikes by improving first-ball accuracy and pin carry."
            )
        else:
            pins_left = analysis["pins_left_in_open_frames"]
            pin_phrase = "pin" if pins_left == 1 else "pins"
            takeaway = (
                f"The main opportunity is spare shooting: you had {open_frames} {open_label} and left "
                f"{pins_left} {pin_phrase} standing in total. Practice picking up the common leaves "
                "you missed, while aiming to leave fewer pins after your first ball."
            )
        return (
            f"You scored {score}, with {strikes} {strike_label}, {spares} {spare_label}, "
            f"and {open_frames} {open_label}. {takeaway}"
        )

    client = OpenAI(api_key=api_key, base_url=os.getenv("AI_GATEWAY_BASE_URL", "https://ai-gateway.vercel.sh/v1"))
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps({"question": question, "current_score": score, "frames": frames}),
        },
    ]

    first = client.chat.completions.create(
        model=os.getenv("BOWLING_COACH_MODEL", "openai/gpt-5.5"),
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.3,
    )
    message = first.choices[0].message

    if message.tool_calls:
        messages.append(message)
        for tool_call in message.tool_calls:
            if tool_call.function.name != "analyze_bowling_game":
                continue
            args = json.loads(tool_call.function.arguments)
            result = analyze_bowling_game(args["frames"])
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

        second = client.chat.completions.create(
            model=os.getenv("BOWLING_COACH_MODEL", "openai/gpt-5.5"),
            messages=messages,
            temperature=0.3,
        )
        return second.choices[0].message.content or "I couldn't generate coaching feedback for that question."

    return message.content or "I couldn't generate coaching feedback for that question."
