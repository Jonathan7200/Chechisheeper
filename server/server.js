const express   = require('express');
const http      = require('http');
const WebSocket = require('ws');

const app    = express();
const server = http.createServer(app);
// still listen on /ws, but no query params any more
const wss    = new WebSocket.Server({ server, path: '/ws' });

// keep track of all open WS connections
const clients = new Set();

let latestState = null;

wss.on('connection', ws => {
  // add new client to our set
  clients.add(ws);

  ws.on('message', raw => {
    try {
      const msg = JSON.parse(raw);
      if (msg.type === 'state') {
        latestState = msg.payload;
        console.log('Received state:', latestState);
      }
    } catch (err) {
      console.error('Invalid JSON:', err);
    }
  });

  ws.on('close', () => {
    // remove closed client
    clients.delete(ws);
  });
});

// HTTP GET to fetch the latest board state
app.get('/state', (req, res) => {
  if (!latestState) {
    return res.status(404).send('No game state available');
  }
  res.json(latestState);
});

// HTTP POST to push one or more commands to all connected Unity clients
// Body may be either { "command": "..."}
// or [ { "command": "..."}, { … } ]
app.post('/command', express.json(), (req, res) => {
  // Turn req.body into an array of commands
  const commandList = Array.isArray(req.body) ? req.body : [req.body];

  // Broadcast each command in turn
  commandList.forEach(cmd => {
    const msg = JSON.stringify({
      type:    'command',
      payload: cmd    
    });
    clients.forEach(ws =>
      ws.readyState === WebSocket.OPEN && ws.send(msg)
    );
  });

  // No content
  res.sendStatus(204);
});

const PORT = 3250;
server.listen(PORT, () => console.log(`API+WS on port ${PORT}`));
