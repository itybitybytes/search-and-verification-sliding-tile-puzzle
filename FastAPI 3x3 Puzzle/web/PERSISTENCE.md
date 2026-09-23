# Completion Persistence

The web application stores puzzle completions server-side with SQLite.

Set `PUZZLE_COMPLETIONS_DB` to choose the database file. For Render, point this
environment variable at a mounted persistent disk path, for example:

```text
PUZZLE_COMPLETIONS_DB=/var/data/completions.sqlite3
```

If the variable is not set, local development uses:

```text
data/completions.sqlite3
```

The application creates the schema automatically on first write. Completion
records include:

- username
- board size
- duration in seconds
- move count
- server-side UTC completion timestamp

The app intentionally uses simple usernames only. It does not add passwords,
email, OAuth, or a public leaderboard.
