import io
import json

import pytest

from frontend_server import BowlingFrontendHandler, build_response_payload, _read_static_file


class FakeResponseHandler:
    def __init__(self, path: str, payload: bytes | None = None):
        self.path = path
        self.headers = {'Content-Length': str(len(payload or b''))}
        self.rfile = io.BytesIO(payload or b'')
        self.wfile = io.BytesIO()
        self.status = None
        self.headers_sent = []

    def send_response(self, code):
        self.status = code

    def send_header(self, key, value):
        self.headers_sent.append((key, value))

    def end_headers(self):
        pass

    def log_message(self, *args, **kwargs):
        pass


def test_multiplayer_service_scores_each_player():
    payload = {
        'players': [
            {
                'name': 'Alice',
                'frames': [
                    ['8', '/'], ['5', '4'], ['9', '0'], ['X'], ['X'], ['5', '/'], ['5', '3'], ['6', '3'], ['9', '/'], ['9', '/', 'X']
                ],
            },
            {
                'name': 'Bob',
                'frames': [
                    ['X'], ['7', '/'], ['9', '0'], ['X'], ['X'], ['5', '5'], ['7', '2'], ['8', '/'], ['9', '0'], ['X', 'X', 'X']
                ],
            },
        ]
    }

    result = build_response_payload(payload)

    assert result['players'][0]['name'] == 'Alice'
    assert result['players'][0]['score'] == 149
    assert result['players'][1]['name'] == 'Bob'
    assert result['players'][1]['score'] == 177


def test_multiplayer_service_rejects_non_list_player_frames():
    payload = {'players': [{'name': 'Alice', 'frames': 'not-a-list'}]}

    with pytest.raises(ValueError, match="'frames' list"):
        build_response_payload(payload)


def test_multiplayer_service_rejects_empty_player_list():
    payload = {'players': []}

    with pytest.raises(ValueError, match="non-empty 'players' list"):
        build_response_payload(payload)


def test_multiplayer_service_defaults_player_name_when_missing():
    payload = {'players': [{'frames': [['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X', 'X', 'X']]}]}

    result = build_response_payload(payload)

    assert result['players'][0]['name'] == 'Player 1'
    assert result['players'][0]['score'] == 300


def test_single_player_payload_still_works():
    payload = {'frames': [['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X', 'X', 'X']]}

    result = build_response_payload(payload)

    assert result['name'] == 'Player 1'
    assert result['score'] == 300


def test_read_static_file_handles_asset_and_security_case():
    index_bytes = _read_static_file('index.html')
    assert index_bytes is not None
    assert b'<html' in index_bytes.lower()

    svg_bytes = _read_static_file('/bowling-ball.svg')
    assert svg_bytes is not None
    assert b'<svg' in svg_bytes.lower()

    assert _read_static_file('../secret.txt') is None


def test_http_handler_get_routes_and_static_asset():
    handler = BowlingFrontendHandler.__new__(BowlingFrontendHandler)
    handler.__dict__.update(FakeResponseHandler('/').__dict__)
    handler.do_GET()
    assert handler.status == 200

    handler = BowlingFrontendHandler.__new__(BowlingFrontendHandler)
    handler.__dict__.update(FakeResponseHandler('/health').__dict__)
    handler.do_GET()
    assert handler.status == 200

    handler = BowlingFrontendHandler.__new__(BowlingFrontendHandler)
    handler.__dict__.update(FakeResponseHandler('/bowling-ball.svg').__dict__)
    handler.do_GET()
    assert handler.status == 200

    handler = BowlingFrontendHandler.__new__(BowlingFrontendHandler)
    handler.__dict__.update(FakeResponseHandler('/missing').__dict__)
    handler.do_GET()
    assert handler.status == 404


def test_http_handler_post_routes_and_error_mode():
    payload = json.dumps({'players': [{'name': 'Alice', 'frames': [['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X'], ['X', 'X', 'X']]}]}).encode()
    handler = BowlingFrontendHandler.__new__(BowlingFrontendHandler)
    handler.__dict__.update(FakeResponseHandler('/api/score', payload).__dict__)
    handler.do_POST()
    assert handler.status == 200

    bad_handler = BowlingFrontendHandler.__new__(BowlingFrontendHandler)
    bad_handler.__dict__.update(FakeResponseHandler('/api/score', b'{bad json}').__dict__)
    bad_handler.do_POST()
    assert bad_handler.status == 400

    wrong_route = BowlingFrontendHandler.__new__(BowlingFrontendHandler)
    wrong_route.__dict__.update(FakeResponseHandler('/wrong', b'{}').__dict__)
    wrong_route.do_POST()
    assert wrong_route.status == 404


def test_serve_frontend_starts_and_stops(monkeypatch):
    calls = {}

    class FakeServer:
        def __init__(self, address, handler):
            calls['address'] = address
            calls['handler'] = handler
            self.closed = False

        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            self.closed = True

    monkeypatch.setattr('frontend_server.ThreadingHTTPServer', lambda address, handler: FakeServer(address, handler))

    from frontend_server import serve_frontend
    serve_frontend('127.0.0.1', 9000)

    assert calls['address'] == ('127.0.0.1', 9000)
    assert calls['handler'] is not None
