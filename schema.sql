CREATE TABLE IF NOT EXISTS country (
  cca3       CHAR(3) PRIMARY KEY,
  name       TEXT      NOT NULL,
  region     TEXT,
  subregion  TEXT,
  population BIGINT,
  area       DOUBLE PRECISION,
  capital    TEXT[]
);