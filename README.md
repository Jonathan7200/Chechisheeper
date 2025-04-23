# TetrisMineSweeper

Open Unity Project

Insert API folder inside Assets/Scripts/

Add Empty Object inside scene, attach GameStateApi script to it

Remove Localization dependency from FileManager, Build The Project

For now
run 
```
curl localhost:8080/state | python3 DiagramGenerator.py
```
to get latest diagram update of the board, which is from either spawning, dropping or rotating.

/state gives a json with all the pieces.