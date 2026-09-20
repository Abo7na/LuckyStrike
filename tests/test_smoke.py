import ast
import pathlib
import sqlite3
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SyntaxTests(unittest.TestCase):
    def test_python_files_parse(self):
        for path in ROOT.rglob("*.py"):
            if ".git" in path.parts:
                continue
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


class DatabaseTests(unittest.TestCase):
    def test_sqlite_constraints(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as file:
            conn = sqlite3.connect(file.name)
            conn.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, balance REAL NOT NULL CHECK(balance >= 0))")
            conn.execute("INSERT INTO users VALUES (1, 0)")
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE users SET balance=-1 WHERE user_id=1")
            conn.close()


if __name__ == "__main__":
    unittest.main()
