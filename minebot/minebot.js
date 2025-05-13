import { spawn } from 'child_process';
import fetch     from 'node-fetch';

const URL = 'http://localhost:3250';
const INTERVAL = 500;

async function loop () {
  console.log('[minebot] Tick...');

  let res;
  try {
    res = await fetch(`${URL}/state`);
  } catch (err) {
    console.error('[minebot] Failed to fetch /state:', err.message);
    return;
  }

  if (res.status !== 200) {
    console.log(`[minebot] Server returned status ${res.status}`);
    return;
  }

  const state = await res.json();
  if (!state.board?.length) {
    console.log('[minebot] Empty board, skipping.');
    return;
  }

  console.log(`[minebot] Received ${state.board.length} tiles`);

  // --- JSON → Prolog facts ---
  const py = spawn('py', ['board_to_facts.py']);
  py.stdin.write(JSON.stringify(state));
  py.stdin.end();

  let facts = '';
  for await (const chunk of py.stdout) {
    facts += chunk.toString();
  }

  await new Promise((r) => py.on('close', r));
  if (!facts.includes('cell')) {
    console.log('[minebot] No facts generated.');
    return;
  }

  console.log('[minebot] Generated facts:\n', facts);

  // --- Run Prolog ---
  const cleanedFacts = facts.trim().split('\n').join(' ');
  const query = `
    consult('minesweeper.pl'),
    ${cleanedFacts},
    next_action(A), writeln(A), halt.
  `;

  const pl = spawn('swipl', ['-q', '-g', query]);

  let move = '';
  for await (const chunk of pl.stdout) {
    move += chunk.toString();
  }

  await new Promise((r) => pl.on('close', r));
  move = move.trim();

  if (!move || move === 'no_move') {
    console.log('[minebot] No move decided.');
    return;
  }

  console.log('[minebot] Decided move:', move);

  const parts = move.replace(/[()]/g, '').split(',');
  if (parts.length !== 3) {
    console.log('[minebot] Invalid move format:', move);
    return;
  }
  const [cmd, x, y] = parts;

  const body =
    cmd === 'flag'
      ? { command: 'flag', parameter: [+x, +y] }
      : { command: 'click', parameter: [+x, +y] };

  console.log('[minebot] Sending command:', body);

  await fetch(`${URL}/command`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

setInterval(loop, INTERVAL);
