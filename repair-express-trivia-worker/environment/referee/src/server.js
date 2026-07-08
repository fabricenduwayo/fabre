import { readFileSync } from "node:fs";

import express from "express";

const PORT = 3000;
const MATCH_ID = "match-night-2026-03-15";
const RULINGS_PATH = "/app/data/rulings.json";

function loadRulings() {
  try {
    const parsed = JSON.parse(readFileSync(RULINGS_PATH, "utf-8"));
    return Array.isArray(parsed.rulings) ? parsed.rulings : [];
  } catch {
    return [];
  }
}

/** @type {Map<string, { body: string, applied: boolean }>} */
const idempotency = new Map();

/** @type {Map<string, { open: boolean, locked: boolean, buzzer: string|null, answered: boolean }>} */
const questions = new Map();

/** @type {Map<string, { score: number, correct: number, firstBuzzSeq: number|null }>} */
const players = new Map();

/** @type {Set<string>} */
const transientFailures = new Set();

function ensurePlayer(id) {
  if (!id) return;
  if (!players.has(id)) {
    players.set(id, { score: 0, correct: 0, firstBuzzSeq: null });
  }
}

function ensureQuestion(id) {
  if (!questions.has(id)) {
    questions.set(id, { open: false, locked: false, buzzer: null, answered: false });
  }
}

function resetState() {
  idempotency.clear();
  questions.clear();
  players.clear();
  transientFailures.clear();
}

function standings() {
  const rows = [...players.entries()].map(([player, stats]) => ({
    player,
    score: stats.score,
    correct: stats.correct,
    first_buzz_seq: stats.firstBuzzSeq,
  }));

  rows.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    if (b.correct !== a.correct) return b.correct - a.correct;
    const af = a.first_buzz_seq ?? Number.MAX_SAFE_INTEGER;
    const bf = b.first_buzz_seq ?? Number.MAX_SAFE_INTEGER;
    if (af !== bf) return af - bf;
    return a.player.localeCompare(b.player);
  });

  return rows.map((row, idx) => ({ rank: idx + 1, ...row }));
}

function shouldFailTransient(seq) {
  return Number(seq) % 6 === 0;
}

function applyEvent(row) {
  const { kind, question, player, payload = {} } = row;
  ensureQuestion(question || "_none");
  if (player) ensurePlayer(player);
  if (payload.player) ensurePlayer(payload.player);

  const q = question ? questions.get(question) : null;

  switch (kind) {
    case "open": {
      if (!question) throw new Error("open requires question");
      q.open = true;
      q.locked = false;
      break;
    }
    case "lock": {
      if (!question) throw new Error("lock requires question");
      q.open = false;
      q.locked = true;
      break;
    }
    case "buzzer": {
      if (!question || !player) throw new Error("buzzer requires question and player");
      if (q.locked || !q.open || q.answered) {
        const err = new Error("locked or unavailable");
        err.status = 422;
        throw err;
      }
      if (q.buzzer) {
        return { ignored: true };
      }
      q.buzzer = player;
      const p = players.get(player);
      if (p.firstBuzzSeq === null) {
        p.firstBuzzSeq = Number(row.seq);
      }
      break;
    }
    case "answer": {
      if (!question || !player) throw new Error("answer requires question and player");
      if (q.locked || !q.open || q.answered) {
        const err = new Error("locked or unavailable");
        err.status = 422;
        throw err;
      }
      if (q.buzzer !== player) {
        const err = new Error("not buzzer holder");
        err.status = 422;
        throw err;
      }
      q.answered = true;
      const p = players.get(player);
      if (payload.correct) {
        p.score += 10;
        p.correct += 1;
      } else {
        p.score -= 5;
      }
      break;
    }
    case "penalty": {
      if (!player) throw new Error("penalty requires player");
      const points = payload.points ?? 5;
      players.get(player).score -= Number(points);
      break;
    }
    case "mod_override": {
      if (!question) throw new Error("mod_override requires question");
      const action = payload.action;
      if (action === "award") {
        ensurePlayer(player);
        players.get(player).score += Number(payload.points ?? 0);
      } else if (action === "deduct") {
        ensurePlayer(player);
        players.get(player).score -= Number(payload.points ?? 0);
      } else if (action === "void_buzzer") {
        q.buzzer = null;
      } else if (action === "reassign") {
        if (q.locked || !q.open || q.answered) {
          const err = new Error("cannot reassign");
          err.status = 422;
          throw err;
        }
        const target = payload.player;
        ensurePlayer(target);
        q.buzzer = target;
        const tp = players.get(target);
        if (tp.firstBuzzSeq === null) {
          tp.firstBuzzSeq = Number(row.seq);
        }
      } else {
        const err = new Error("unknown override");
        err.status = 422;
        throw err;
      }
      break;
    }
    default: {
      const err = new Error("unknown kind");
      err.status = 422;
      throw err;
    }
  }
  return { ignored: false };
}

const app = express();
app.use(express.json({ limit: "32kb" }));

app.get("/health", (_req, res) => {
  res.json({ status: "ok", match: MATCH_ID });
});

app.post("/v1/reset", (_req, res) => {
  resetState();
  res.json({ status: "reset" });
});

app.get("/v1/standings", (_req, res) => {
  res.json({ match: MATCH_ID, status: "provisional", standings: standings() });
});

app.get("/v1/rulings", (_req, res) => {
  res.json({ match: MATCH_ID, rulings: loadRulings() });
});

app.post("/v1/ingest", (req, res) => {
  const key = req.header("X-Idempotency-Key");
  if (!key) {
    return res.status(400).json({ error: "missing_idempotency_key" });
  }

  const row = req.body;
  if (!row || row.seq === undefined || !row.kind) {
    return res.status(400).json({ error: "invalid_body" });
  }

  const body = JSON.stringify(row);
  const prior = idempotency.get(key);
  if (prior) {
    if (prior.body !== body) {
      return res.status(409).json({ error: "idempotency_conflict" });
    }
    return res.json({ status: "duplicate", standings: standings() });
  }

  const failKey = `${key}:transient`;
  if (shouldFailTransient(row.seq) && !transientFailures.has(failKey)) {
    transientFailures.add(failKey);
    return res.status(503).json({ error: "transient_overload", retry: true });
  }

  try {
    const result = applyEvent(row);
    idempotency.set(key, { body, applied: true });
    return res.json({ status: result.ignored ? "ignored" : "applied", standings: standings() });
  } catch (err) {
    const status = err.status || 500;
    return res.status(status).json({ error: err.message });
  }
});

resetState();
app.listen(PORT, "127.0.0.1", () => {
  // eslint-disable-next-line no-console
  console.log(`referee listening on ${PORT}`);
});
