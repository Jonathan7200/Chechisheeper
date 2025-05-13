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
http://localhost:3250/state
```
- 200 OK: Returns JSON with State of the Board
- 404 Not Found: Response body: No game state available

### POST ```/command```
Sends commands to Open Game.

```{bash}
http://localhost:3250/command
```

- 204 No Content: Command successfully sent.

Use these two endpoints to pull game state and push control commands.

## Available Commands
These are the following commands via ```POST /command```

| Command         | Description                                          | Parameters |
|-----------------|------------------------------------------------------|------------|
| `moveleft`        | Move the active tetromino one cell to the left       | `None`|
| `moveright`       | Move the active tetromino one cell to the right      | `None` |
| `softdrop`        | Soft-drop the active tetromino                        | `None` |
| `harddrop`        | Hard-drop the active tetromino                        | `None` |
| `rotate`          | Rotate the active tetromino clockwise                 | `None` |
| `rotateccw`       | Rotate the active tetromino counterclockwise          | `None` |
| `hold`            | Hold the current tetromino                            | `None` |
| `reveal`          | Reveal specific tetromino                             | `x, y` |
| `flag`            | Flag specific tetromino                               | `x, y` |
| `chord`           | Reveal Chord for specific tetromino                   | `x, y` |
|`chordflag`        | Flag Chord for specific tetromino                     | `x, y` |


## Example
For one command with no parameters
```{json}
{"command" : "moveleft"}
```

For one command with parameters
```{json}
{   
    "command" : "flag", 
    "x" : 0,
    "y" : 0
}
```
For multiple commands
```{json}
[
    {"command" : "moveleft"},
    {"command" : "rotate"},
    {"command" : "harddrop"}
]
```
