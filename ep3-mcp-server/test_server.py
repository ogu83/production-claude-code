"""test_server.py — Test both tools directly without running the MCP server.

No API key, no Claude Code session, no MCP transport required.
Import the tool functions directly and call them with controlled inputs.

Run with:
    pytest test_server.py -v
    pytest test_server.py -v -k "query"    # query tool tests only
    pytest test_server.py -v -k "file"     # file tool tests only
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from tools.query_tool import query_db
from tools.read_file_tool import read_file

# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture()
def temp_db(tmp_path: Path) -> Path:
    """Create a minimal SQLite database for query_tool tests."""
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
        CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL);
        INSERT INTO items VALUES (1, 'alpha', 10.5);
        INSERT INTO items VALUES (2, 'beta',  20.0);
        INSERT INTO items VALUES (3, 'gamma',  5.75);
    """)
    conn.commit()
    conn.close()
    return db


@pytest.fixture()
def data_dir(tmp_path: Path) -> Path:
    """Create a temporary data directory with a couple of readable files."""
    d = tmp_path / "data"
    d.mkdir()
    (d / "notes.txt").write_text("Hello from data/notes.txt", encoding="utf-8")
    (d / "schema.json").write_text('{"table": "items"}', encoding="utf-8")
    # A file in a sibling directory — should be unreachable.
    sibling = tmp_path / "data_evil"
    sibling.mkdir()
    (sibling / "secret.txt").write_text("should not be readable", encoding="utf-8")
    return d


# ─── query_tool tests ─────────────────────────────────────────────────────────


class TestQueryTool:
    def test_select_returns_rows(self, temp_db: Path) -> None:
        result = json.loads(query_db("SELECT * FROM items", temp_db))
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["name"] == "alpha"

    def test_select_with_where(self, temp_db: Path) -> None:
        result = json.loads(query_db("SELECT name FROM items WHERE value > 10", temp_db))
        names = [r["name"] for r in result]
        assert "alpha" in names
        assert "beta" in names
        assert "gamma" not in names

    def test_with_cte_allowed(self, temp_db: Path) -> None:
        sql = "WITH ranked AS (SELECT * FROM items) SELECT * FROM ranked"
        result = json.loads(query_db(sql, temp_db))
        assert isinstance(result, list)
        assert len(result) == 3

    def test_insert_blocked_by_prefix_check(self, temp_db: Path) -> None:
        result = json.loads(query_db("INSERT INTO items VALUES (4, 'delta', 1.0)", temp_db))
        assert "error" in result
        assert "INSERT" in result["error"]

    def test_delete_blocked_by_prefix_check(self, temp_db: Path) -> None:
        result = json.loads(query_db("DELETE FROM items", temp_db))
        assert "error" in result

    def test_update_blocked_by_prefix_check(self, temp_db: Path) -> None:
        result = json.loads(query_db("UPDATE items SET value = 0", temp_db))
        assert "error" in result

    def test_drop_blocked_by_prefix_check(self, temp_db: Path) -> None:
        result = json.loads(query_db("DROP TABLE items", temp_db))
        assert "error" in result

    def test_write_via_cte_blocked_by_mode_ro(self, temp_db: Path) -> None:
        # WITH ... DELETE is technically valid SQL but must be blocked.
        # The prefix check passes (first token = WITH), but mode=ro at the
        # DB level catches it.
        sql = "WITH x AS (SELECT 1) DELETE FROM items"
        result = json.loads(query_db(sql, temp_db))
        assert "error" in result

    def test_empty_query_returns_error(self, temp_db: Path) -> None:
        result = json.loads(query_db("", temp_db))
        assert "error" in result

    def test_missing_database_returns_error(self, tmp_path: Path) -> None:
        result = json.loads(query_db("SELECT 1", tmp_path / "nonexistent.db"))
        assert "error" in result

    def test_syntax_error_returns_error(self, temp_db: Path) -> None:
        result = json.loads(query_db("SELECT FROM WHERE", temp_db))
        assert "error" in result

    def test_returns_json_string(self, temp_db: Path) -> None:
        result = query_db("SELECT * FROM items", temp_db)
        assert isinstance(result, str)
        # Must be valid JSON
        json.loads(result)


# ─── read_file_tool tests ─────────────────────────────────────────────────────


class TestReadFileTool:
    def test_reads_file_in_allowed_dir(self, data_dir: Path) -> None:
        result = read_file(str(data_dir / "notes.txt"), data_dir)
        assert result == "Hello from data/notes.txt"

    def test_reads_json_file(self, data_dir: Path) -> None:
        result = read_file(str(data_dir / "schema.json"), data_dir)
        assert '"table"' in result

    def test_path_traversal_blocked(self, data_dir: Path) -> None:
        # ../sibling path — must be blocked
        traversal = str(data_dir / ".." / "data_evil" / "secret.txt")
        result = json.loads(read_file(traversal, data_dir))
        assert "error" in result
        assert "outside allowed directory" in result["error"].lower()

    def test_sibling_dir_blocked(self, data_dir: Path) -> None:
        # data_evil shares a prefix string with data — must still be blocked.
        sibling_file = str(data_dir.parent / "data_evil" / "secret.txt")
        result = json.loads(read_file(sibling_file, data_dir))
        assert "error" in result

    def test_absolute_path_outside_allowed_blocked(self, data_dir: Path, tmp_path: Path) -> None:
        outside = tmp_path / "outside.txt"
        outside.write_text("secret", encoding="utf-8")
        result = json.loads(read_file(str(outside), data_dir))
        assert "error" in result

    def test_missing_file_returns_error(self, data_dir: Path) -> None:
        result = json.loads(read_file(str(data_dir / "nofile.txt"), data_dir))
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_large_file_rejected(self, data_dir: Path) -> None:
        big = data_dir / "big.txt"
        big.write_bytes(b"x" * 60_000)
        result = json.loads(read_file(str(big), data_dir))
        assert "error" in result
        assert "large" in result["error"].lower()

    def test_binary_file_rejected(self, data_dir: Path) -> None:
        binary = data_dir / "blob.bin"
        binary.write_bytes(bytes(range(256)))
        result = json.loads(read_file(str(binary), data_dir))
        assert "error" in result
