# Chechisheeper


**Team Members**: Jemma Arona, Sean Estrella, Jonathan Flores, Jonathan Jara  
**Course**: CSC 481 - Knowledge Based Systems
**Instructor**: Dr. Rodrigo Canaan

## Project Summary

Chechisheeper is a knowledge-based agent for Tetrisweeper, a hybrid game combining **Tetris** and **Minesweeper** mechanics. 
Our system integrates real-time decision-making and logical reasoning, managing the dynamic Tetris board while finding safe cells and mines using Minesweeper-style clues.

The bot is split into:
- A **Minesweeper Agent** (Python) that handles safe/mine inference.
- A **Tetris Agent** for handling Tetris placements.
- A **Node.js server** that connects to the Tetrisweeper game and mediates state/command communication.


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


Start Minesweeper Agent:
```{bash}
python main_agent.py
```


## Reproducing Results

Launch main_agent.py with the server running.
Play the game in MARATHON mode and track how many lines are cleared automatically.
The system resets logical knowledge on each line clear (linesCleared change).
You can monitor the agent’s reasoning via terminal logs.


## Resources and Acknowledgments

Tetrisweeper Game by Kertis Jones
https://github.com/KertisJones/minesweeper 

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
