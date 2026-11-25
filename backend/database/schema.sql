CREATE TABLE IF NOT EXISTS units (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('HEADQUARTERS', 'BRANCH', 'STATION')),
    parent_id TEXT,
    FOREIGN KEY (parent_id) REFERENCES units(id)
);