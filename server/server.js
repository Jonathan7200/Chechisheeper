const express   = require('express');
const url      = require('url');
const http      = require('http');
const WebSocket = require('ws');

const app    = express();
const server = http.createServer(app);
const wss    = new WebSocket.Server({ server, path: '/ws' });

let latestState = null;
const gameStates = new Map();

wss.on('connection', (ws, req) => {
    const {query} = url.parse(req.url, true);
    const gameId = query.gameId;
    if (!gameId) return ws.close(4000, 'gameId is required');
    ws.gameId = gameId;
    console.log(`New connection for gameId: ${gameId}`);

    ws.on('message', raw => {
        console.log(`[WS][${gameId}]`, raw);
        const state = JSON.parse(raw);
        gameStates.set(gameId, state);
    })
  });

// HTTP GET for your agent
app.get('/state/:gameId', (req, res) => {
    const state = gameStates.get(req.params.gameId);
    if (!state) return res.status(404).send('Game state not found');
    res.json(state);
});

const PORT = 3250;
server.listen(PORT, () => console.log(`API+WS on port ${PORT}`));
