import pytest

from frontend_server import build_response_payload


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
