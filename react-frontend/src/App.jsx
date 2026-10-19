import { useMemo, useState } from 'react';

const frameCount = 10;
const defaultFrames = [
  ['8', '/'], ['5', '4'], ['9', '0'], ['X'], ['X'],
  ['5', '/'], ['5', '3'], ['6', '3'], ['9', '/'], ['9', '/', 'X'],
];

function blankFrames() {
  return Array.from({ length: frameCount }, () => []);
}

function normalizeToken(value) {
  return String(value ?? '').trim().toUpperCase().replace(/[^0-9X/]/g, '').slice(0, 1);
}

function parseRollToken(token, previousRoll) {
  if (token === 'X') return 10;
  if (token === '/') {
    if (previousRoll === undefined) throw new Error("A frame cannot start with a spare ('/').");
    return 10 - previousRoll;
  }
  if (/^[0-9]$/.test(token)) return Number(token);
  throw new Error(`Unsupported character '${token}'.`);
}

function buildScoreboard(frames) {
  const cleanedFrames = frames.map((frame) => frame.map(normalizeToken).filter(Boolean));
  if (cleanedFrames.length !== frameCount) throw new Error(`A complete game must have exactly 10 frames. Received ${cleanedFrames.length} frames.`);
  const numericGame = cleanedFrames.map((frame) => frame.map((token, i, values) => parseRollToken(token, values[i - 1])));

  for (let i = 0; i < numericGame.length; i += 1) {
    const frame = numericGame[i];
    const frameNum = i + 1;
    if (!frame.length) throw new Error(`Frame ${frameNum}: Frame cannot be empty. Missing rolls in a frame.`);
    if (frameNum < 10) {
      if (frame.length > 2) throw new Error(`Frame ${frameNum}: Frames 1-9 cannot contain more than 2 rolls.`);
      if (frame.length === 2 && frame[0] + frame[1] > 10) throw new Error(`Frame ${frameNum}: Total pins knocked down cannot exceed 10 pins.`);
      if (frame[0] === 10 && frame.length > 1) throw new Error(`Frame ${frameNum}: A strike ('X') must stand alone in frames 1-9.`);
    } else {
      if (frame.length > 3) throw new Error('Frame 10: Final Frame cannot contain more than 3 rolls.');
      if (frame[0] === 10 && frame.length < 3) throw new Error('Frame 10: Getting a strike requires 2 additional bonus rolls.');
      if (frame[0] !== 10 && frame.length >= 2 && frame[0] + frame[1] === 10 && frame.length < 3) throw new Error('Frame 10: Getting a spare requires 1 additional bonus roll.');
      if (frame[0] !== 10 && frame.length === 2 && frame[0] + frame[1] > 10) throw new Error('Frame 10: Total open frame score cannot exceed 10 pins.');
      if (frame[0] !== 10 && frame.length !== 2 && !(frame.length >= 2 && frame[0] + frame[1] === 10)) throw new Error('Frame 10: An open frame must have exactly 2 rolls.');
      if (frame[0] === 10 && frame[1] === 10 && frame.length === 3 && frame[2] === '/') throw new Error("Frame 10: '/' cannot immediately follow a strike ('X'); the next roll starts a new rack.");
      if (frame[0] === 10 && frame[1] !== 10 && frame[1] + frame[2] > 10) throw new Error('Frame 10: The bonus rolls after a strike cannot exceed 10 pins unless the second roll is a strike.');
    }
  }

  const flattened = numericGame.flat();
  const cumulativeScores = [];
  let total = 0;
  let rollIndex = 0;
  for (let frameIndex = 0; frameIndex < frameCount; frameIndex += 1) {
    const roll = flattened[rollIndex];
    if (roll === 10) total += 10 + flattened[rollIndex + 1] + flattened[rollIndex + 2], rollIndex += 1;
    else if (roll + flattened[rollIndex + 1] === 10) total += 10 + flattened[rollIndex + 2], rollIndex += 2;
    else total += roll + flattened[rollIndex + 1], rollIndex += 2;
    cumulativeScores.push(total);
  }
  const displayFrames = cleanedFrames.map((frame, index) => index < 9 && frame.length === 1 && frame[0] === 'X' ? [...frame, '_'] : frame);
  return { score: total, cumulative_scores: cumulativeScores, display_frames: displayFrames };
}

function calculateBoard(frames) {
  try { return buildScoreboard(frames); }
  catch (error) { return { score: 0, cumulative_scores: Array(frameCount).fill(''), display_frames: Array(frameCount).fill([]), error: error.message }; }
}

function App() {
  const [players, setPlayers] = useState([{ id: 1, name: 'Player 1', frames: defaultFrames, question: 'How did I do?', answer: '', coachBusy: false }]);
  const [nextPlayerId, setNextPlayerId] = useState(2);

  const boards = useMemo(() => Object.fromEntries(players.map((player) => [player.id, calculateBoard(player.frames)])), [players]);

  const updatePlayer = (playerId, update) => {
    setPlayers((current) => current.map((player) => player.id === playerId ? update(player) : player));
  };

  const handleChange = (playerId, frameIndex, rollIndex, value) => {
    updatePlayer(playerId, (player) => ({
      ...player,
      frames: player.frames.map((frame, idx) => idx === frameIndex ? Object.assign([...frame], { [rollIndex]: normalizeToken(value) }) : [...frame]),
      answer: '',
    }));
  };

  const addPlayer = () => {
    const id = nextPlayerId;
    setNextPlayerId((value) => value + 1);
    setPlayers((current) => [...current, { id, name: `Player ${id}`, frames: blankFrames(), question: 'How did I do?', answer: '', coachBusy: false }]);
  };

  const askCoach = async (event, player) => {
    event?.preventDefault();
    const board = boards[player.id];
    if (board.error) {
      updatePlayer(player.id, (current) => ({ ...current, answer: 'Finish a valid 10-frame game before asking for coaching.' }));
      return;
    }
    updatePlayer(player.id, (current) => ({ ...current, coachBusy: true, answer: '' }));
    try {
      const response = await fetch('/api/coach', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: player.question, frames: player.frames, score: board.score }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'The bowling coach is unavailable.');
      updatePlayer(player.id, (current) => ({ ...current, answer: data.answer }));
    } catch (error) {
      updatePlayer(player.id, (current) => ({ ...current, answer: error.message }));
    } finally {
      updatePlayer(player.id, (current) => ({ ...current, coachBusy: false }));
    }
  };

  return (
    <div className="page-shell">
      <div className="page-heading">
        <div>
          <h1>Bowling Game</h1>
          <p className="subtitle">Track scores for everyone playing. Add players and edit each frame.</p>
        </div>
        <button type="button" className="primary-button" onClick={addPlayer}>+ Add Player</button>
      </div>

      <div className="players-list">
        {players.map((player) => {
          const board = boards[player.id];
          return (
            <section className="panel player-panel" key={player.id} aria-labelledby={`player-title-${player.id}`}>
              <div className="player-heading">
                <label className="player-name-label" htmlFor={`player-name-${player.id}`}>Player name</label>
                <input id={`player-name-${player.id}`} className="player-name-input" value={player.name} onChange={(event) => updatePlayer(player.id, (current) => ({ ...current, name: event.target.value }))} />
                {players.length > 1 && <button type="button" className="secondary-button" onClick={() => setPlayers((current) => current.filter((item) => item.id !== player.id))} aria-label={`Remove ${player.name || 'player'}`}>Remove</button>}
              </div>
              <h2 id={`player-title-${player.id}`}>{player.name || 'Unnamed player'}</h2>
              <div className="frame-grid">
                {Array.from({ length: frameCount }).map((_, index) => {
                  const frame = player.frames[index] ?? [];
                  const maxRolls = index === 9 ? 3 : 2;
                  return <div className="frame-card" key={`frame-${index}`}><label className="frame-label">Frame {index + 1}</label><div className="roll-row">
                    {Array.from({ length: maxRolls }).map((__, rollIndex) => <input key={`frame-${index}-roll-${rollIndex}`} className="roll-input" value={frame[rollIndex] ?? ''} maxLength={1} onChange={(event) => handleChange(player.id, index, rollIndex, event.target.value)} placeholder={rollIndex === 0 ? 'roll' : ''} aria-label={`${player.name || 'Player'} frame ${index + 1} roll ${rollIndex + 1}`} />)}
                  </div></div>;
                })}
              </div>
              <div className="error-box" role="alert">{board.error || ''}</div>
              <div className="scoreboard" aria-label={`${player.name} scorecard`}>
                <div className="scoreboard-header">{Array.from({ length: frameCount }).map((_, index) => <div key={`header-${index}`} className="score-cell header-cell">{index + 1}</div>)}</div>
                <div className="scoreboard-body"><div className="scoreboard-row">{board.display_frames.map((frame, index) => <div key={`roll-${index}`} className="score-cell">{(frame || []).join(' ') || '—'}</div>)}</div><div className="scoreboard-row">{board.cumulative_scores.map((score, index) => <div key={`score-${index}`} className="score-value">{score || ''}</div>)}</div></div>
              </div>
              <div className="total-box"><span>Total score</span><strong>{board.score || 0}</strong></div>

              <section className="coach-panel" aria-label={`${player.name} bowling coach`}>
                <div><h3>🎳 Bowling Coach</h3><p>Ask for feedback on {player.name || 'this player'}’s game.</p></div>
                <form className="coach-form" onSubmit={(event) => askCoach(event, player)}><input value={player.question} onChange={(event) => updatePlayer(player.id, (current) => ({ ...current, question: event.target.value }))} aria-label={`Ask the Bowling Coach about ${player.name}`} placeholder="What should I practice?" /><button type="submit" disabled={player.coachBusy}>{player.coachBusy ? 'Thinking…' : 'Ask Coach'}</button></form>
                <div className="coach-prompts">{['How did I do?', 'What was my weakest frame?', 'What should I practice next?'].map((prompt) => <button type="button" key={prompt} onClick={() => updatePlayer(player.id, (current) => ({ ...current, question: prompt }))}>{prompt}</button>)}</div>
                {player.answer && <div className="coach-answer"><strong>Coach:</strong><p>{player.answer}</p></div>}
              </section>
            </section>
          );
        })}
      </div>
    </div>
  );
}

export default App;
