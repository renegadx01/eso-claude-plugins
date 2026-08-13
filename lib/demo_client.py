"""A minimal stand-in for the Supabase Python client, backed by the fixture
data in lib/demo_data.py. Supports just enough of the fluent query API
(.select/.eq/.neq/.in_/.order/.limit/.execute, plus the embedded-resource
select syntax like "projects(name)") to serve every query this app actually
makes — it isn't a general PostgREST reimplementation.

Used only when ?demo=1 is on the URL (see lib/auth.py) — never touches the
real Supabase project or requires real credentials.
"""

import re
import types

from lib.demo_data import TABLES

# (base_table, embed_key) -> foreign-key column on the base table's row that
# points at the embedded table's `id`. Covers every embed this app queries.
_EMBED_FK = {
    ("time_entries", "projects"): "project_id",
    ("time_entries", "phases"): "phase_id",
    ("time_entries", "people"): "person_id",
    ("allocations", "projects"): "project_id",
    ("allocations", "people"): "person_id",
    ("actions", "projects"): "project_id",
    ("actions", "people"): "raised_by",
    ("flags", "projects"): "project_id",
    ("flags", "people"): "person_id",
    ("milestones", "projects"): "project_id",
}

# (base_table, embed_key) -> (target_table, fk_column_on_target) for the one
# reverse (one-to-many) embed this app uses: projects -> phases.
_REVERSE_EMBED = {
    ("projects", "phases"): ("phases", "project_id"),
}

# Matches a select token like "name", "projects(name)", or
# "phases!phases_project_id_fkey(name)".
_TOKEN_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)(?:![a-zA-Z0-9_]+)?(?:\((.*)\))?$")


def _split_top_level(select_str):
    tokens, depth, current = [], 0, ""
    for ch in select_str:
        if ch == "(":
            depth += 1
            current += ch
        elif ch == ")":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            tokens.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        tokens.append(current.strip())
    return tokens


def _project_flat(row, select_str):
    """Plain column selection, no embeds — used for rows inside an embed."""
    if row is None:
        return None
    cols = [c.strip() for c in select_str.split(",")]
    return {c: row.get(c) for c in cols}


class DemoQuery:
    def __init__(self, table_name):
        self.table_name = table_name
        self.rows = list(TABLES[table_name])
        self._select = "*"

    def select(self, select_str):
        self._select = select_str
        return self

    def eq(self, key, val):
        self.rows = [r for r in self.rows if r.get(key) == val]
        return self

    def neq(self, key, val):
        self.rows = [r for r in self.rows if r.get(key) != val]
        return self

    def in_(self, key, values):
        values = set(values)
        self.rows = [r for r in self.rows if r.get(key) in values]
        return self

    def order(self, key, desc=False):
        self.rows = sorted(self.rows, key=lambda r: (r.get(key) is None, r.get(key)), reverse=desc)
        return self

    def limit(self, n):
        self.rows = self.rows[:n]
        return self

    def execute(self):
        return types.SimpleNamespace(data=[self._project_row(r) for r in self.rows])

    def _project_row(self, row):
        if self._select.strip() == "*":
            return dict(row)

        out = {}
        for token in _split_top_level(self._select):
            m = _TOKEN_RE.match(token)
            if not m:
                continue
            name, inner = m.group(1), m.group(2)

            if inner is None:
                out[name] = row.get(name)
                continue

            reverse = _REVERSE_EMBED.get((self.table_name, name))
            if reverse:
                target_table, fk_col = reverse
                related = [r for r in TABLES[target_table] if r.get(fk_col) == row.get("id")]
                out[name] = [_project_flat(r, inner) for r in related]
                continue

            fk_col = _EMBED_FK.get((self.table_name, name))
            if fk_col is None:
                out[name] = None
                continue
            target = next((r for r in TABLES[name] if r.get("id") == row.get(fk_col)), None)
            out[name] = _project_flat(target, inner)

        return out


class DemoClient:
    """Drop-in replacement for the authed Supabase client in demo mode."""

    def table(self, name):
        return DemoQuery(name)
