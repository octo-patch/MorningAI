"""Lightweight SQLite snapshot store for leaderboard tracking.

Stores daily snapshots of leaderboard state (model name, rank, score)
and diffs against the previous snapshot to detect new models, removals,
and ranking/score changes.

DB location: data/leaderboard.db (auto-created on first use).
"""

import json
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "leaderboard.db"

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS leaderboard_entries (
    leaderboard   TEXT NOT NULL,
    model         TEXT NOT NULL,
    rank          INTEGER,
    score         REAL,
    metadata      TEXT,
    snapshot_date TEXT NOT NULL,
    PRIMARY KEY (leaderboard, model, snapshot_date)
)
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_lb_date
ON leaderboard_entries (leaderboard, snapshot_date)
"""


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(_CREATE_TABLE)
        conn.execute(_CREATE_INDEX)


def save_snapshot(leaderboard: str, date: str, entries: list[dict]):
    """Save a list of model entries for a leaderboard on a given date.

    Each entry: {"model": str, "rank": int|None, "score": float|None, ...}
    Extra keys are stored in the metadata JSON column.
    """
    init_db()
    with _connect() as conn:
        for entry in entries:
            model = entry["model"]
            rank = entry.get("rank")
            score = entry.get("score")
            extra = {k: v for k, v in entry.items() if k not in ("model", "rank", "score")}
            metadata = json.dumps(extra, ensure_ascii=False) if extra else None
            conn.execute(
                """INSERT OR REPLACE INTO leaderboard_entries
                   (leaderboard, model, rank, score, metadata, snapshot_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (leaderboard, model, rank, score, metadata, date),
            )


def _get_snapshot(conn, leaderboard: str, date: str) -> dict[str, dict]:
    """Return {model_name: {rank, score, metadata}} for a specific date."""
    rows = conn.execute(
        """SELECT model, rank, score, metadata FROM leaderboard_entries
           WHERE leaderboard = ? AND snapshot_date = ?""",
        (leaderboard, date),
    ).fetchall()
    result = {}
    for r in rows:
        result[r["model"]] = {
            "rank": r["rank"],
            "score": r["score"],
            "metadata": json.loads(r["metadata"]) if r["metadata"] else {},
        }
    return result


def _get_prev_date(conn, leaderboard: str, date: str) -> str | None:
    """Find the most recent snapshot date before `date`."""
    row = conn.execute(
        """SELECT DISTINCT snapshot_date FROM leaderboard_entries
           WHERE leaderboard = ? AND snapshot_date < ?
           ORDER BY snapshot_date DESC LIMIT 1""",
        (leaderboard, date),
    ).fetchone()
    return row["snapshot_date"] if row else None


def diff_snapshot(leaderboard: str, date: str) -> dict:
    """Compare the snapshot at `date` with the previous one.

    Returns:
        {
            "leaderboard": str,
            "date": str,
            "prev_date": str | None,
            "is_initial": bool,
            "new_models": [{"model", "rank", "score"}, ...],
            "removed_models": [str, ...],
            "rank_changes": [{"model", "old_rank", "new_rank"}, ...],
            "score_changes": [{"model", "old_score", "new_score"}, ...],
        }
    """
    init_db()
    with _connect() as conn:
        current = _get_snapshot(conn, leaderboard, date)
        prev_date = _get_prev_date(conn, leaderboard, date)

        if prev_date is None:
            return {
                "leaderboard": leaderboard,
                "date": date,
                "prev_date": None,
                "is_initial": True,
                "new_models": [
                    {"model": m, "rank": d["rank"], "score": d["score"]}
                    for m, d in current.items()
                ],
                "removed_models": [],
                "rank_changes": [],
                "score_changes": [],
            }

        previous = _get_snapshot(conn, leaderboard, prev_date)
        curr_names = set(current)
        prev_names = set(previous)

        new_models = [
            {"model": m, "rank": current[m]["rank"], "score": current[m]["score"]}
            for m in sorted(curr_names - prev_names)
        ]
        removed_models = sorted(prev_names - curr_names)

        rank_changes = []
        score_changes = []
        for m in sorted(curr_names & prev_names):
            c, p = current[m], previous[m]
            if c["rank"] is not None and p["rank"] is not None and c["rank"] != p["rank"]:
                rank_changes.append({"model": m, "old_rank": p["rank"], "new_rank": c["rank"]})
            if c["score"] is not None and p["score"] is not None and c["score"] != p["score"]:
                score_changes.append({"model": m, "old_score": p["score"], "new_score": c["score"]})

        return {
            "leaderboard": leaderboard,
            "date": date,
            "prev_date": prev_date,
            "is_initial": False,
            "new_models": new_models,
            "removed_models": removed_models,
            "rank_changes": rank_changes,
            "score_changes": score_changes,
        }


def get_latest_snapshot(leaderboard: str) -> dict:
    """Return the most recent snapshot for a leaderboard.

    Returns: {"leaderboard", "date", "entries": [{"model", "rank", "score"}, ...]}
    """
    init_db()
    with _connect() as conn:
        row = conn.execute(
            """SELECT DISTINCT snapshot_date FROM leaderboard_entries
               WHERE leaderboard = ?
               ORDER BY snapshot_date DESC LIMIT 1""",
            (leaderboard,),
        ).fetchone()
        if not row:
            return {"leaderboard": leaderboard, "date": None, "entries": []}

        date = row["snapshot_date"]
        snapshot = _get_snapshot(conn, leaderboard, date)
        return {
            "leaderboard": leaderboard,
            "date": date,
            "entries": [
                {"model": m, "rank": d["rank"], "score": d["score"]}
                for m, d in snapshot.items()
            ],
        }
