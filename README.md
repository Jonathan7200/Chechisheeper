# Chechisheeper

## Setup
Clone or pull the repository and install dependencies:

```{bash}
git clone https://github.com/Jonathan7200/Chechisheeper.git
cd Chechisheeper
npm install
```

Start the server:
```{bash}
node server.js
```

> **Important**: Make sure the server is running *before* pressing **PLAY MARATHON** on the modified [Tetrisweeper](https://tetris.goldfishjonny.com/). When the game initializes it will connect to ws://localhost:3250/ws and begin sending state updates; after that you can push commands at any time using the /command endpoint. The PLAY MARATHON command will be added later, so the websocket connects the moment it is up.

## HTTP Endpoints
### GET ```/state```
Returns the latest game state.
```{bash}
curl http://localhost:3250/state
```
- 200 OK: Returns JSON with State of the Board
- 404 Not Found: Response body: No game state available

### POST ```/command```
Sends commands to Open Game

```{bash}
curl -X POST http://localhost:3250/command -H "Content-Type: application/json" -d "{\"command\":\"moveleft\",\"parameter\":0}"
```

- 204 No Content: Command successfully sent.

Use these two endpoints to pull game state and push control commands.

## Available Commands
These are the following commands via ```POST /command```

| Command         | Description                                          |
|-----------------|------------------------------------------------------|
| `moveleft`        | Move the active tetromino one cell to the left       |
| `moveright`       | Move the active tetromino one cell to the right      |
| `softdrop`        | Soft-drop the active tetromino                        |
| `harddrop`        | Hard-drop the active tetromino                        |
| `rotate`          | Rotate the active tetromino clockwise                 |
| `rotateccw`       | Rotate the active tetromino counterclockwise          |
| `hold`            | Hold the current tetromino                            |