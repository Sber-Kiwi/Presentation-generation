CREATE TABLE "User" (
    userID      SERIAL NOT NULL PRIMARY KEY
);

CREATE TABLE "Chat" (
    chatID      SERIAL NOT NULL PRIMARY KEY,
    userID      INT REFERENCES "User"(userID) ON DELETE CASCADE;
    prompt      VARCHAR(500) NOT NULL,
    csv         BYTEA NOT NULL,
    title       VARCHAR(100) NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE TABLE "Metrica" (
    metricaID       SERIAL NOT NULL PRIMARY KEY,
    name            VARCHAR(50)
)

CREATE TABLE "Slide" (
    slideID     SERIAL NOT NULL PRIMARY KEY,
    chatID      INT REFERENCES "Chat"(chatID) ON DELETE CASCADE,
    metricaID   INT REFERENCES "Metrica"(metricaIF) ON DELETE CASCADE,
    num         SMALLINT NOT NULL CHECK (num > 0),
    comment     VARCHAR(250) NULL
);

CREATE TABLE "Version" (
    versionID       SERIAL NOT NULL PRIMARY KEY,
    slideID         INT REFERENCES "Slide"(slideID) ON DELETE CASCADE,
    version_num     SMALLINT NOT NULL CHECK (version_num >= 0),
    json_content    JSONB NOT NULL,
    edit_note       VARCHAR(250) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    is_final        BOOLEAN DEFAULT False NOT NULL
);

CREATE UNIQUE INDEX one_final_per_slide
ON "Version"(slideID) WHERE is_final = TRUE;

CREATE TABLE "Task" (
    taskID         SERIAL NOT NULL PRIMARY KEY,
    versionID      INT REFERENCES "Version"(versionID) ON DELETE CASCADE,
    status         INT DEFAULT 0 NOT NULL
);