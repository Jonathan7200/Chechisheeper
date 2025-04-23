using System;
using System.Collections.Generic;
using System.Net;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

// Data Transfer Objects
[Serializable]
public class TileDto {
    public int x;
    public int y;
    public bool isRevealed;
    public bool isFlagged;
    public int nearbyMines;
    public string aura;
}

[Serializable]
public class PieceDto {
    public string type;
    public List<Vector2Int> cells;
}

[Serializable]
public class BoardStateDto {
    public List<TileDto> board;
    public PieceDto nextPiece;
    public PieceDto heldPiece;
}

public class GameStateApi : MonoBehaviour {
    private HttpListener _http;
    private List<WebSocket> _clients = new List<WebSocket>();
    private GameManager _gm;
    private TetrominoSpawner _spawner;

    void Awake() {
        // Reference existing game components using updated APIs
        _gm = GameObject.FindWithTag("GameController").GetComponent<GameManager>();
        _spawner = UnityEngine.Object.FindFirstObjectByType<TetrominoSpawner>();
    }

    void Start() {
        // Initialize HTTP listener
        _http = new HttpListener();
        _http.Prefixes.Add("http://*:8080/");
        _http.Start();
        Debug.Log("GameStateApi listening on port 8080");

        // Fire-and-forget accept loop
        _ = HandleIncomingConnections();

        // Subscribe to game events for real-time push
        GameManager.OnHardDropEvent += BroadcastState;
        GameManager.OnLeftStuckEvent += BroadcastState;
        GameManager.OnRightStuckEvent += BroadcastState;
        GameManager.OnMinoLockEvent += BroadcastState;
        GameManager.OnNewPieceEvent += BroadcastState;
    }

    async Task HandleIncomingConnections() {
        while (_http.IsListening) {
            var ctx = await _http.GetContextAsync();
            if (ctx.Request.IsWebSocketRequest) {
                var wsCtx = await ctx.AcceptWebSocketAsync(null);
                _clients.Add(wsCtx.WebSocket);
                await SendJson(wsCtx.WebSocket, GetBoardState());
            } else if (ctx.Request.HttpMethod == "GET" && ctx.Request.Url.AbsolutePath == "/state") {
                var dto = GetBoardState();
                var json = JsonUtility.ToJson(dto);
                var data = Encoding.UTF8.GetBytes(json);
                ctx.Response.ContentType = "application/json";
                await ctx.Response.OutputStream.WriteAsync(data, 0, data.Length);
                ctx.Response.Close();
            } else {
                ctx.Response.StatusCode = 404;
                ctx.Response.Close();
            }
        }
    }

    BoardStateDto GetBoardState() {
        var dto = new BoardStateDto { board = new List<TileDto>() };
        for (int x = 0; x < _gm.sizeX; x++) {
            for (int y = 0; y < _gm.sizeY; y++) {
                var go = GameManager.gameBoard[x][y];
                if (go == null) continue;
                var tile = go.GetComponent<Tile>();
                dto.board.Add(new TileDto {
                    x = x,
                    y = y,
                    isRevealed = tile.isRevealed,
                    isFlagged = tile.isFlagged,
                    nearbyMines = tile.isRevealed ? tile.nearbyMines : -1,
                    aura = tile.aura.ToString()
                });
            }
        }
        dto.nextPiece = _spawner.tetrominoPreviewList.Count > 0
            ? BuildPieceDto(_spawner.tetrominoPreviewList[0])
            : null;
        var holdComp = UnityEngine.Object.FindFirstObjectByType<HoldTetromino>();
        dto.heldPiece = (holdComp != null && holdComp.heldTetromino != null)
            ? BuildPieceDto(holdComp.heldTetromino)
            : null;
        return dto;
    }

    PieceDto BuildPieceDto(GameObject piece) {
        var group = piece.GetComponent<Group>();
        var cells = new List<Vector2Int>();
        foreach (var t in group.GetChildTiles())
            cells.Add(new Vector2Int(t.coordX, t.coordY));
        return new PieceDto {
            type = group.tetrominoType.ToString(),
            cells = cells
        };
    }

    async void BroadcastState() {
        var dto = GetBoardState();
        var json = JsonUtility.ToJson(dto);
        var buffer = Encoding.UTF8.GetBytes(json);
        foreach (var ws in _clients.ToArray()) {
            if (ws.State != WebSocketState.Open) { _clients.Remove(ws); continue; }
            await ws.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
        }
    }

    async Task SendJson(WebSocket ws, BoardStateDto dto) {
        var json = JsonUtility.ToJson(dto);
        var buffer = Encoding.UTF8.GetBytes(json);
        await ws.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
    }

    void OnDestroy() {
        _http?.Stop();
    }
}
