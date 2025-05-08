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

// HTTP POST to push a command to all connected Unity clients
// Body should be JSON: { "command": "moveleft", "parameter": 0 }
app.post('/command', express.json(), (req, res) => {
  const { command, parameter = 0 } = req.body;
  const msg = JSON.stringify({
    type:    'command',
    payload: { command, parameter }
  });
  clients.forEach(ws => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(msg);
    }
  });
  res.sendStatus(204);
});

const PORT = 3250;
server.listen(PORT, () => console.log(`API+WS on port ${PORT}`));
