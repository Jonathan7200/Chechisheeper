/* server.js — Node bridge for Tetrisweeper  (one-file CSV log) */
const express   = require("express");
const http      = require("http");
const WebSocket = require("ws");
const fs        = require("fs");
const path      = require("path");

const app    = express();
const server = http.createServer(app);
const wss    = new WebSocket.Server({ server, path: "/ws" });

/* ────────────  logging setup  ────────────────────────────────────── */
const logsDir = path.join(__dirname, "..", "logs");
fs.mkdirSync(logsDir, { recursive: true });

const csvPath = path.join(logsDir, "runs.csv");
if (!fs.existsSync(csvPath))
  fs.writeFileSync(csvPath, "run,linesCleared,level\n");

let nextIdx =
  fs.readFileSync(csvPath, "utf8").trim().split("\n").length - 1;
/* ─────────────────────────────────────────────────────────────────── */

const clients     = new Set();
let   latestState = null;                // exposed at /state

/* ---------------- REST endpoints ----------------------------------- */
app.get("/state", (req, res) =>
  latestState ? res.json(latestState)
              : res.status(404).send("No game state"));

app.post("/command", express.json(), (req, res) => {
  const cmds = Array.isArray(req.body) ? req.body : [req.body];
  const msg  = JSON.stringify({ type: "command", payload: cmds });
  clients.forEach(ws =>
    ws.readyState === WebSocket.OPEN && ws.send(msg));
  res.sendStatus(204);
});

/* ---------------- helper: append one CSV line ---------------------- */
function logRun(state) {
  const row = `${nextIdx},${state.linesCleared},${state.level}\n`;
  fs.appendFileSync(csvPath, row);
  console.log("[bridge] logged", row.trim());
  nextIdx += 1;
}

/* ---------------- WebSocket handling ------------------------------- */
wss.on("connection", ws => {
  clients.add(ws);

  /* per-playthrough flags & timer */
  let gameplayStarted  = false;   // becomes true after first real frame
  let sawProgress      = false;   // linesCleared ever > 0  (guards early log)
  let wroteLog         = false;   // ensures 1 row only
  let idleTimer        = null;
  const DEAD_MS        = 3000;

  /* ---------- finish helper --------------------------------------- */
  function finish() {
    if (!wroteLog && sawProgress && latestState) {
      logRun(latestState);
      wroteLog = true;
    }
  }

  /* ---------- refresh 3-second idle timer ------------------------- */
  function refreshTimer() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(finish, DEAD_MS);
  }

  /* ---------- incoming packets ------------------------------------ */
  ws.on("message", raw => {
    try {
      const { type, payload } = JSON.parse(raw);
      if (type !== "state") return;

      latestState = payload;

      /* ––– detect real gameplay start ––– */
      const hasPiece = (payload.currentPiece?.cells?.length ?? 0) > 0;
      if (!gameplayStarted && (hasPiece || payload.linesCleared > 0)) {
        gameplayStarted = true;
        console.log("[bridge] gameplay started");
      }
      if (!gameplayStarted) return;          // still menu / countdown

      /* ––– record progress flag ––– */
      if (payload.linesCleared > 0) sawProgress = true;

      /* ––– idle detection ––– */
      const boardIdle =
        !hasPiece &&                        // no falling piece
        payload.board?.length === 0;        // nothing moving (Unity sets board empty on solved screen)

      if (boardIdle) finish();              // immediate write
      else refreshTimer();                  // wait for possible idle
    } catch (e) {
      console.error("[bridge] bad JSON:", e.message);
    }
  });

  /* ---------- socket closes --------------------------------------- */
  ws.on("close", () => {
    clearTimeout(idleTimer);
    finish();               // last-chance write
    clients.delete(ws);
  });
});

/* ---------------- launch ------------------------------------------- */
const PORT = 3250;
server.listen(PORT, () =>
  console.log(`Bridge ready → http://localhost:${PORT}`));
