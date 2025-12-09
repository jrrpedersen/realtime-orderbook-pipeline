-- Create table for validated ticks
CREATE TABLE IF NOT EXISTS ticks (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    received_time TIMESTAMPTZ NOT NULL,
    bid_price DOUBLE PRECISION NOT NULL,
    ask_price DOUBLE PRECISION NOT NULL,
    bid_volume DOUBLE PRECISION NOT NULL,
    ask_volume DOUBLE PRECISION NOT NULL,
    sequence_id BIGINT NOT NULL
);

-- Index to speed up queries by symbol and time
CREATE INDEX IF NOT EXISTS idx_ticks_symbol_time
ON ticks (symbol, event_time DESC);