CREATE TABLE IF NOT EXISTS cyclones (
    id_cyclone text PRIMARY KEY,
    name text NOT NULL,
    vmax double precision NOT NULL,
    mslp double precision NOT NULL,
    lat double precision NOT NULL,
    lon double precision NOT NULL,
    classification text NOT NULL,
    basin text NOT NULL,
    is_invest boolean NOT NULL DEFAULT false,
    source text NOT NULL DEFAULT '',
    last_update text NOT NULL DEFAULT ''
);
