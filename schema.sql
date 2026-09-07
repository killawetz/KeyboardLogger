CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER NOT NULL PRIMARY KEY,
    started_at REAL,
    ended_at REAL,
    hostname TEXT
);

CREATE TABLE IF NOT EXISTS key_events (
    id INTEGER NOT NULL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    event_time REAL,
    key_name TEXT,
    event_type TEXT NOT NULL CHECK (event_type in ('press', 'release')),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_key_events_session ON key_events(session_id);
CREATE INDEX IF NOT EXISTS idx_key_events_timestamp ON key_events(timestamp);