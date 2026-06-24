CREATE TABLE users (
    userID      SERIAL NOT NULL PRIMARY KEY
);

CREATE TABLE csvs (
    csvID       SERIAL NOT NULL PRIMARY KEY,
    file        BYTEA NOT NULL
);

CREATE TABLE jsons (
    jsonID      SERIAL NOT NULL PRIMARY KEY,
    file        JSONB NOT NULL
);

CREATE TABLE chats (
    chatID      SERIAL NOT NULL PRIMARY KEY,
    userID      INT REFERENCES users(userID) ON DELETE CASCADE,
    csvID       INT REFERENCES csvs(csvid) ON DELETE CASCADE,
    jsonID      INT REFERENCES jsons(jsonid) ON DELETE CASCADE,
    title       VARCHAR(100) NOT NULL,
    prompt      VARCHAR(500) NOT NULL  
);

CREATE TABLE metricas (
    metricaID       SERIAL NOT NULL PRIMARY KEY,
    name            VARCHAR(50)
);

CREATE TABLE slides (
    slideID     SERIAL NOT NULL PRIMARY KEY,
    chatID      INT REFERENCES chats(chatID) ON DELETE CASCADE,
    metricaID   INT REFERENCES metricas(metricaID) ON DELETE CASCADE,
    num         SMALLINT NOT NULL CHECK (num > 0),
    comment     VARCHAR(250) NULL
);

CREATE TABLE versions (
    versionID       SERIAL NOT NULL PRIMARY KEY,
    slideID         INT REFERENCES slides(slideID) ON DELETE CASCADE,
    json            JSONB NOT NULL,
    prompt          VARCHAR(250) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    is_final        BOOLEAN DEFAULT False NOT NULL
);

CREATE TABLE tasks (
    taskID         SERIAL NOT NULL PRIMARY KEY,
    chatID         INT REFERENCES chats(chatID) ON DELETE CASCADE,
    versionID      INT REFERENCES versions(versionID) ON DELETE CASCADE,
    type           INT NOT NULL,
    prompt         VARCHAR(500) NOT NULL,
    status         INT DEFAULT 0 NOT NULL           -- 0 - новая, 1 - в работе, 2 - завершена
);