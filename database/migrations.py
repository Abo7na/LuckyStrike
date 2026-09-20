# -*- coding: utf-8 -*-

from database.db import init_db, ensure_default_round


def run_migrations():
    init_db()
    ensure_default_round()
