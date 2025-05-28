import { spawn } from 'child_process';
import fetch     from 'node-fetch';

const URL      = process.env.TSW_URL ?? 'http://localhost:3250';
const INTERVAL = 500;            // ms

async function loop () {
  console.log('[minebot] Tick…');

  /* game state  */
  let res;
  try {
    res = await fetch(`${URL}/state`);
  } catch (err) {
    console.error('[minebot] Cannot reach /state →', err.message);
    return;
  }
  if (res.status !== 200) {
    console.log(`[minebot] /state → ${res.status}`);
    return;
  }

  const state = await res.json();
  if (!state.board?.length) {
    console.log('[minebot] Empty board, skipping.');
    return;
  }

  /* JSON into Prolog facts  */
  const py = spawn('py', ['board_to_facts.py']);
  py.stdin.write(JSON.stringify(state));
  py.stdin.end();

  let facts = '';
  for await (const chunk of py.stdout) facts += chunk.toString();
  await new Promise(r => py.on('close', r));

  if (!facts.includes('cell(')) {
    console.log('[minebot] No facts produced.');
    return;
  }

  /*  Run Prolog  */
  const query = `
      consult('minesweeper.pl'),
      ${facts.trim().split('\n').join(' ')},
      next_action(A), writeln(A), halt.
  `;
  const pl = spawn('swipl', ['-q', '-g', query]);

  let move = '';
  for await (const chunk of pl.stdout) move += chunk.toString();
  await new Promise(r => pl.on('close', r));
  move = move.trim();

  if (!move || move === 'no_move') {
    console.log('[minebot] No move decided.');
    return;
  }
  console.log('[minebot] Move →', move);

  const [cmd, x, y] = move.replace(/[()]/g, '').split(',');
  let body;

  if (['reveal', 'flag', 'chord', 'chordflag'].includes(cmd)) {
    body = { command: cmd, x: +x, y: +y };
  } else {
    body = { command: cmd };                
  }
  console.log('[minebot] POST /command →', body);

  await fetch(`${URL}/command`, {
    method : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body   : JSON.stringify(body)
  });
}

setInterval(loop, INTERVAL);
