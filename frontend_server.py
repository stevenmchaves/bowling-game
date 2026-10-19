import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from main import game_pipeline

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / 'static' / 'index.html'
STATIC_DIR = ROOT / 'static'


def _score_player(player_name: str, frames: list[list[str]]) -> dict:
    game = game_pipeline(json.dumps(frames))
    board = game.get_scoreboard_data()
    return {
        'name': player_name,
        'score': game.score(),
        'cumulative_scores': board['cumulative_scores'],
        'display_frames': board['display_frames'],
        'frames': game.raw_frames,
    }


def build_response_payload(payload: dict) -> dict:
    """Build the score response for either a single game or multiple players."""
    if 'players' in payload:
        players = payload['players']
        if not isinstance(players, list) or not players:
            raise ValueError("Request body must include a non-empty 'players' list.")

        response = {'players': []}
        for index, player in enumerate(players):
            name = str(player.get('name') or f'Player {index + 1}')
            frames = player.get('frames', [])
            if not isinstance(frames, list):
                raise ValueError(f"Player '{name}' must include a 'frames' list.")
            response['players'].append(_score_player(name, frames))
        return response

    frames = payload.get('frames')
    if not isinstance(frames, list):
        raise ValueError("Request body must include a 'frames' list or a 'players' list.")
    return _score_player('Player 1', frames)


def _read_static_file(path: str) -> bytes | None:
    safe = path.lstrip('/')
    if not safe or safe == 'index.html':
        return INDEX_FILE.read_bytes()
    resolved = (STATIC_DIR / safe).resolve()
    if STATIC_DIR.resolve() not in resolved.parents and resolved != STATIC_DIR.resolve():
        return None
    if resolved.is_file():
        return resolved.read_bytes()
    return None


class BowlingFrontendHandler(BaseHTTPRequestHandler):
    server_version = 'BowlingGameFrontend/1.1'

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {'/', '/index.html'}:
            self._send_response(200, INDEX_FILE.read_text(encoding='utf-8'), 'text/html; charset=utf-8')
            return
        if parsed.path == '/health':
            self._send_response(200, json.dumps({'status': 'ok'}), 'application/json; charset=utf-8')
            return
        if parsed.path.endswith(('.svg', '.png', '.jpg', '.jpeg', '.gif', '.css', '.js')):
            data = _read_static_file(parsed.path)
            if data is not None:
                content_type = 'image/svg+xml' if parsed.path.endswith('.svg') else 'text/css; charset=utf-8' if parsed.path.endswith('.css') else 'application/javascript; charset=utf-8'
                self._send_response(200, data.decode('utf-8') if isinstance(data, bytes) and parsed.path.endswith(('.svg', '.css', '.js')) else data, content_type)
                return
        self._send_response(404, json.dumps({'error': 'Not found'}), 'application/json; charset=utf-8')

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != '/api/score':
            self._send_response(404, json.dumps({'error': 'Not found'}), 'application/json; charset=utf-8')
            return

        try:
            content_length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode('utf-8'))
            result = build_response_payload(payload)
            self._send_response(200, json.dumps(result), 'application/json; charset=utf-8')
        except Exception as exc:  # pragma: no cover - defensive API path
            self._send_response(400, json.dumps({'error': str(exc)}), 'application/json; charset=utf-8')

    def _send_response(self, status_code: int, body, content_type: str) -> None:
        if isinstance(body, str):
            data = body.encode('utf-8')
        else:
            data = body

        if hasattr(self, 'requestline') and hasattr(self, 'request_version'):
            self.send_response(status_code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
        else:
            self.status = status_code
            self.headers_sent = getattr(self, 'headers_sent', [])
            self.headers_sent.append(('Content-Type', content_type))
            self.headers_sent.append(('Content-Length', str(len(data))))
            if hasattr(self, 'wfile'):
                self.wfile.write(data)

        if data and hasattr(self, 'wfile') and not hasattr(self, 'headers_sent'):
            self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        return


def serve_frontend(host: str = '127.0.0.1', port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), BowlingFrontendHandler)
    print(f'Bowling game frontend running at http://{host}:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down frontend server.')
    finally:
        server.server_close()


if __name__ == '__main__':
    serve_frontend()
