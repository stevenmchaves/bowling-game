import { useMemo, useState } from 'react';

const frameCount = 10;
const defaultFrames = [
  ['8', '/'], ['5', '4'], ['9', '0'], ['X'], ['X'],
  ['5', '/'], ['5', '3'], ['6', '3'], ['9', '/'], ['9', '/', 'X'],
];

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
  const numericGame = cleanedFrames.map((frame) => frame.map((token, i, values) => parseRollToken(token, values[i - 1])));
  if (numericGame.length !== frameCount) throw new Error(`A complete game must have exactly 10 frames. Received ${numericGame.length} frames.`);

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

function App() {
  const [frames, setFrames] = useState(defaultFrames);
  const [question, setQuestion] = useState('How did I do?');
  const [answer, setAnswer] = useState('');
  const [coachBusy, setCoachBusy] = useState(false);

  const board = useMemo(() => {
    try { return buildScoreboard(frames); }
    catch (error) { return { score: 0, cumulative_scores: Array(frameCount).fill(''), display_frames: Array(frameCount).fill([]), error: error.message }; }
  }, [frames]);

  const handleChange = (frameIndex, rollIndex, value) => {
    setFrames(frames.map((frame, idx) => idx === frameIndex ? Object.assign([...frame], { [rollIndex]: normalizeToken(value) }) : [...frame]));
  };

  const askCoach = async (event) => {
    event?.preventDefault();
    if (board.error) { setAnswer('Finish a valid 10-frame game before asking for coaching.'); return; }
    setCoachBusy(true);
    setAnswer('');
    try {
      const response = await fetch('/api/coach', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question, frames, score: board.score }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'The bowling coach is unavailable.');
      setAnswer(data.answer);
    } catch (error) { setAnswer(error.message); }
    finally { setCoachBusy(false); }
  };

  return (
    <div className="page-shell">
      <div className="panel">
        <h1>Bowling Game</h1>
        <p className="subtitle">Edit any frame score and the board updates live.</p>
        <div className="frame-grid">
          {Array.from({ length: frameCount }).map((_, index) => {
            const frame = frames[index] ?? [];
            const maxRolls = index === 9 ? 3 : 2;
            return <div className="frame-card" key={`frame-${index}`}><label className="frame-label">Frame {index + 1}</label><div className="roll-row">
              {Array.from({ length: maxRolls }).map((__, rollIndex) => <input key={`frame-${index}-roll-${rollIndex}`} className="roll-input" value={frame[rollIndex] ?? ''} maxLength={1} onChange={(event) => handleChange(index, rollIndex, event.target.value)} placeholder={rollIndex === 0 ? 'roll' : ''} aria-label={`Frame ${index + 1} roll ${rollIndex + 1}`} />)}
            </div></div>;
          })}
        </div>
        <div className="error-box">{board.error || ''}</div>
        <div className="scoreboard">
          <div className="scoreboard-header">{Array.from({ length: frameCount }).map((_, index) => <div key={`header-${index}`} className="score-cell header-cell">{index + 1}</div>)}</div>
          <div className="scoreboard-body"><div className="scoreboard-row">{board.display_frames.map((frame, index) => <div key={`roll-${index}`} className="score-cell">{(frame || []).join(' ') || '—'}</div>)}</div><div className="scoreboard-row">{board.cumulative_scores.map((score, index) => <div key={`score-${index}`} className="score-value">{score || ''}</div>)}</div></div>
        </div>
        <div className="total-box"><span>Total score</span><strong>{board.score || 0}</strong></div>

        <section className="coach-panel" aria-labelledby="coach-title">
          <div><h2 id="coach-title">🎳 Bowling Coach</h2><p>Ask about this game and get feedback based on the frames above.</p></div>
          <form className="coach-form" onSubmit={askCoach}><input value={question} onChange={(event) => setQuestion(event.target.value)} aria-label="Ask the Bowling Coach" placeholder="What should I practice?" /><button type="submit" disabled={coachBusy}>{coachBusy ? 'Thinking…' : 'Ask Coach'}</button></form>
          <div className="coach-prompts">{['How did I do?', 'What was my weakest frame?', 'What should I practice next?'].map((prompt) => <button type="button" key={prompt} onClick={() => setQuestion(prompt)}>{prompt}</button>)}</div>
          {answer && <div className="coach-answer"><strong>Coach:</strong><p>{answer}</p></div>}
        </section>
      </div>
    </div>
  );
}

export default App;
