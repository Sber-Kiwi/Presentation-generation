CREATE DATABASE kiwidb;

CREATE TABLE users (
    userID      SERIAL NOT NULL PRIMARY KEY,
    department  VARCHAR(40) NOT NULL,

    CONSTRAINT chk_user_department CHECK (char_length(trim(department)) > 0)
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
    jsonID      INT REFERENCES jsons(jsonid) ON DELETE SET NULL,
    title       VARCHAR(100) NOT NULL,
    prompt      VARCHAR(500) NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now() NOT NULL,  

    CONSTRAINT chk_chat_title CHECK (char_length(trim(title)) > 0),
    CONSTRAINT chk_chat_prompt CHECK (char_length(trim(prompt)) > 0)
);

CREATE TABLE slides (
    slideID     SERIAL NOT NULL PRIMARY KEY,
    chatID      INT REFERENCES chats(chatID) ON DELETE CASCADE,
    num         SMALLINT NOT NULL CHECK (num > 0),
    
    CONSTRAINT uq_slide_num UNIQUE (chatID, num)
);

CREATE TABLE versions (
    versionID       SERIAL NOT NULL PRIMARY KEY,
    slideID         INT REFERENCES slides(slideID) ON DELETE CASCADE,
    json            JSONB NOT NULL,
    prompt          VARCHAR(250) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    is_final        BOOLEAN DEFAULT false NOT NULL,

    CONSTRAINT chk_version_prompt CHECK (char_length(trim(prompt)) > 0)
);

-- 1 slide - 1 final ver 
CREATE UNIQUE INDEX one_final_version_per_slide 
    ON versions(slideID) 
    WHERE is_final = true;

CREATE TABLE tasks (
    taskID         SERIAL NOT NULL PRIMARY KEY,
    chatID         INT REFERENCES chats(chatID) ON DELETE CASCADE,
    versionID      INT REFERENCES versions(versionID) ON DELETE CASCADE,
    type           INT NOT NULL,
    prompt         VARCHAR(500) NOT NULL,
    status         INT DEFAULT 0 NOT NULL,           -- 0 - новая, 1 - в работе, 2 - завершена, 3 -- завершена с ошибкой
    error_message  VARCHAR(100) DEFAULT NULL,

    CONSTRAINT chk_task_status CHECK (status BETWEEN 0 AND 3),
    CONSTRAINT chk_task_prompt CHECK (char_length(trim(prompt)) > 0)
);