--
-- PostgreSQL database dump
--

\restrict m3p0KUL7fowb5SC09I3ALaMvhUs5DhQhCUB9Iz3Y03Vg97hzBZJTAZ8I5ODcoLL

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chats (
    chatid integer NOT NULL,
    userid integer,
    csvid integer,
    jsonid integer,
    title character varying(100) NOT NULL,
    prompt character varying(500) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_chat_prompt CHECK ((char_length(TRIM(BOTH FROM prompt)) > 0)),
    CONSTRAINT chk_chat_title CHECK ((char_length(TRIM(BOTH FROM title)) > 0))
);


ALTER TABLE public.chats OWNER TO postgres;

--
-- Name: chats_chatid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chats_chatid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chats_chatid_seq OWNER TO postgres;

--
-- Name: chats_chatid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chats_chatid_seq OWNED BY public.chats.chatid;


--
-- Name: csvs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.csvs (
    csvid integer NOT NULL,
    file bytea NOT NULL
);


ALTER TABLE public.csvs OWNER TO postgres;

--
-- Name: csvs_csvid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.csvs_csvid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.csvs_csvid_seq OWNER TO postgres;

--
-- Name: csvs_csvid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.csvs_csvid_seq OWNED BY public.csvs.csvid;


--
-- Name: jsons; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jsons (
    jsonid integer NOT NULL,
    file jsonb NOT NULL
);


ALTER TABLE public.jsons OWNER TO postgres;

--
-- Name: jsons_jsonid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.jsons_jsonid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.jsons_jsonid_seq OWNER TO postgres;

--
-- Name: jsons_jsonid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.jsons_jsonid_seq OWNED BY public.jsons.jsonid;


--
-- Name: slides; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.slides (
    slideid integer NOT NULL,
    chatid integer,
    num smallint NOT NULL,
    CONSTRAINT slides_num_check CHECK ((num > 0))
);


ALTER TABLE public.slides OWNER TO postgres;

--
-- Name: slides_slideid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.slides_slideid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.slides_slideid_seq OWNER TO postgres;

--
-- Name: slides_slideid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.slides_slideid_seq OWNED BY public.slides.slideid;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    taskid integer NOT NULL,
    chatid integer,
    versionid integer,
    type integer NOT NULL,
    prompt character varying(500) NOT NULL,
    status integer DEFAULT 0 NOT NULL,
    error_message character varying(100) DEFAULT NULL::character varying,
    CONSTRAINT chk_task_prompt CHECK ((char_length(TRIM(BOTH FROM prompt)) > 0)),
    CONSTRAINT chk_task_status CHECK (((status >= 0) AND (status <= 3)))
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- Name: tasks_taskid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tasks_taskid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tasks_taskid_seq OWNER TO postgres;

--
-- Name: tasks_taskid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tasks_taskid_seq OWNED BY public.tasks.taskid;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    userid integer NOT NULL,
    department character varying(40) NOT NULL,
    CONSTRAINT chk_user_department CHECK ((char_length(TRIM(BOTH FROM department)) > 0))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_userid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_userid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_userid_seq OWNER TO postgres;

--
-- Name: users_userid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_userid_seq OWNED BY public.users.userid;


--
-- Name: versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.versions (
    versionid integer NOT NULL,
    slideid integer,
    "json" jsonb NOT NULL,
    prompt character varying(250) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    is_final boolean DEFAULT false NOT NULL,
    CONSTRAINT chk_version_prompt CHECK ((char_length(TRIM(BOTH FROM prompt)) > 0))
);


ALTER TABLE public.versions OWNER TO postgres;

--
-- Name: versions_versionid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.versions_versionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.versions_versionid_seq OWNER TO postgres;

--
-- Name: versions_versionid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.versions_versionid_seq OWNED BY public.versions.versionid;


--
-- Name: chats chatid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats ALTER COLUMN chatid SET DEFAULT nextval('public.chats_chatid_seq'::regclass);


--
-- Name: csvs csvid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.csvs ALTER COLUMN csvid SET DEFAULT nextval('public.csvs_csvid_seq'::regclass);


--
-- Name: jsons jsonid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jsons ALTER COLUMN jsonid SET DEFAULT nextval('public.jsons_jsonid_seq'::regclass);


--
-- Name: slides slideid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slides ALTER COLUMN slideid SET DEFAULT nextval('public.slides_slideid_seq'::regclass);


--
-- Name: tasks taskid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks ALTER COLUMN taskid SET DEFAULT nextval('public.tasks_taskid_seq'::regclass);


--
-- Name: users userid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN userid SET DEFAULT nextval('public.users_userid_seq'::regclass);


--
-- Name: versions versionid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.versions ALTER COLUMN versionid SET DEFAULT nextval('public.versions_versionid_seq'::regclass);


--
-- Data for Name: chats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chats (chatid, userid, csvid, jsonid, title, prompt, created_at) FROM stdin;
1	1	1	1	Анализ продаж Q1	Сгенерируй презентацию для анализ продаж q1	2026-07-06 16:54:20.064504+03
2	2	2	2	Отчет по маркетингу	Сгенерируй презентацию для отчет по маркетингу	2026-07-06 16:54:20.064504+03
3	3	3	3	Финансовые показатели	Сгенерируй презентацию для финансовые показатели	2026-07-06 16:54:20.064504+03
4	4	4	4	HR метрики	Сгенерируй презентацию для hr метрики	2026-07-06 16:54:20.064504+03
5	5	5	5	Прогноз на год	Сгенерируй презентацию для прогноз на год	2026-07-06 16:54:20.064504+03
\.


--
-- Data for Name: csvs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.csvs (csvid, file) FROM stdin;
1	\\x69642c6e616d652c76616c75650a302c4974656d5f302c30
2	\\x69642c6e616d652c76616c75650a312c4974656d5f312c313030
3	\\x69642c6e616d652c76616c75650a322c4974656d5f322c323030
4	\\x69642c6e616d652c76616c75650a332c4974656d5f332c333030
5	\\x69642c6e616d652c76616c75650a342c4974656d5f342c343030
\.


--
-- Data for Name: jsons; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.jsons (jsonid, file) FROM stdin;
1	{"index": 0, "theme": "dark", "active": true}
2	{"index": 1, "theme": "light", "active": true}
3	{"index": 2, "theme": "dark", "active": true}
4	{"index": 3, "theme": "light", "active": true}
5	{"index": 4, "theme": "dark", "active": true}
\.


--
-- Data for Name: slides; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.slides (slideid, chatid, num) FROM stdin;
1	1	1
2	1	2
3	1	3
4	1	4
5	1	5
6	1	6
7	2	1
8	2	2
9	2	3
10	2	4
11	2	5
12	2	6
13	3	1
14	3	2
15	3	3
16	3	4
17	3	5
18	3	6
19	4	1
20	4	2
21	4	3
22	4	4
23	4	5
24	4	6
25	5	1
26	5	2
27	5	3
28	5	4
29	5	5
30	5	6
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (taskid, chatid, versionid, type, prompt, status, error_message) FROM stdin;
1	1	11	1	Обработать версию 11 для чата 1	2	\N
2	1	20	1	Обработать версию 20 для чата 1	3	Провал
3	1	23	0	Обработать версию 23 для чата 1	2	\N
4	1	21	0	Обработать версию 21 для чата 1	1	\N
5	1	18	0	Обработать версию 18 для чата 1	2	\N
6	2	50	1	Обработать версию 50 для чата 2	1	\N
7	2	51	1	Обработать версию 51 для чата 2	3	Провал
8	2	\N	2	Задача для чата 2	1	\N
9	2	33	2	Обработать версию 33 для чата 2	1	\N
10	3	\N	0	Задача для чата 3	3	Провал
11	3	\N	0	Задача для чата 3	2	\N
12	3	\N	0	Задача для чата 3	1	\N
13	3	67	0	Обработать версию 67 для чата 3	2	\N
14	4	\N	1	Задача для чата 4	0	\N
15	4	\N	0	Задача для чата 4	3	Провал
16	5	\N	2	Задача для чата 5	2	\N
17	5	\N	2	Задача для чата 5	0	\N
18	5	145	2	Обработать версию 145 для чата 5	2	\N
19	5	144	1	Обработать версию 144 для чата 5	1	\N
20	5	148	0	Обработать версию 148 для чата 5	3	Провал
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (userid, department) FROM stdin;
1	Отдел продаж
2	Отдел планирования
3	Отдел приколов
4	Отдел плоскогубцев
5	Отдел отделов
\.


--
-- Data for Name: versions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.versions (versionid, slideid, "json", prompt, created_at, is_final) FROM stdin;
1	1	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
2	1	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
3	1	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
4	1	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
5	1	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
6	2	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
7	2	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
8	2	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
9	2	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
10	2	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
11	3	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
12	3	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
13	3	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
14	3	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
15	3	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
16	4	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
17	4	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
18	4	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
19	4	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
20	5	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
21	5	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
22	5	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
23	5	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
24	6	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
25	6	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
26	6	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
27	6	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
28	6	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-06 17:34:20.140268+03	f
29	6	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
30	7	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
31	7	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
32	7	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
33	7	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
34	7	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
35	8	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
36	8	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
37	8	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
38	8	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
39	8	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
40	9	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
41	9	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
42	9	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
43	9	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
44	9	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-06 17:34:20.140268+03	f
45	9	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
46	10	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
47	10	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
48	10	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
49	10	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
50	11	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
51	11	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
52	11	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
53	11	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
54	11	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
55	12	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
56	12	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
57	12	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
58	12	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
59	12	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
60	13	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
61	13	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
62	13	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
63	13	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
64	14	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
65	14	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
66	14	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
67	14	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
68	15	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
69	15	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
70	15	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
71	15	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
72	16	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
73	16	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
74	16	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
75	16	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
76	16	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-06 17:34:20.140268+03	f
77	16	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
78	17	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
79	17	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
80	17	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
81	17	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
82	17	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-06 17:34:20.140268+03	f
83	17	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
84	18	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
85	18	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
86	18	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
87	18	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
88	19	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
89	19	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
90	19	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
91	19	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
92	20	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
93	20	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
94	20	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
95	20	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
96	20	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
97	21	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
98	21	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
99	21	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
100	21	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
101	21	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-06 17:34:20.140268+03	f
102	21	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
103	22	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
104	22	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
105	22	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
106	22	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
107	22	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-06 17:34:20.140268+03	f
108	22	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
109	23	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
110	23	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
111	23	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
112	23	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
113	24	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
114	24	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
115	24	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
116	24	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
117	24	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-06 17:34:20.140268+03	f
118	24	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
119	25	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
120	25	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
121	25	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
122	25	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
123	25	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-06 17:34:20.140268+03	f
124	25	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
125	26	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
126	26	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
127	26	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
128	26	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
129	26	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
130	27	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
131	27	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
132	27	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
133	27	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
134	28	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
135	28	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
136	28	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
137	28	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
138	28	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-06 17:34:20.140268+03	f
139	28	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
140	29	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
141	29	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
142	29	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
143	29	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
144	29	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
145	30	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-06 16:54:20.140268+03	f
146	30	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-06 17:04:20.140268+03	f
147	30	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-06 17:14:20.140268+03	f
148	30	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-06 17:24:20.140268+03	f
149	30	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-06 17:34:20.140268+03	f
150	30	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-06 16:54:20.064504+03	t
\.


--
-- Name: chats_chatid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chats_chatid_seq', 5, true);


--
-- Name: csvs_csvid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.csvs_csvid_seq', 5, true);


--
-- Name: jsons_jsonid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.jsons_jsonid_seq', 5, true);


--
-- Name: slides_slideid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.slides_slideid_seq', 30, true);


--
-- Name: tasks_taskid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_taskid_seq', 20, true);


--
-- Name: users_userid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_userid_seq', 5, true);


--
-- Name: versions_versionid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.versions_versionid_seq', 150, true);


--
-- Name: chats chats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_pkey PRIMARY KEY (chatid);


--
-- Name: csvs csvs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.csvs
    ADD CONSTRAINT csvs_pkey PRIMARY KEY (csvid);


--
-- Name: jsons jsons_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jsons
    ADD CONSTRAINT jsons_pkey PRIMARY KEY (jsonid);


--
-- Name: slides slides_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slides
    ADD CONSTRAINT slides_pkey PRIMARY KEY (slideid);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (taskid);


--
-- Name: slides uq_slide_num; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slides
    ADD CONSTRAINT uq_slide_num UNIQUE (chatid, num);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);


--
-- Name: versions versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.versions
    ADD CONSTRAINT versions_pkey PRIMARY KEY (versionid);


--
-- Name: one_final_version_per_slide; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX one_final_version_per_slide ON public.versions USING btree (slideid) WHERE (is_final = true);


--
-- Name: chats chats_csvid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_csvid_fkey FOREIGN KEY (csvid) REFERENCES public.csvs(csvid) ON DELETE CASCADE;


--
-- Name: chats chats_jsonid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_jsonid_fkey FOREIGN KEY (jsonid) REFERENCES public.jsons(jsonid) ON DELETE SET NULL;


--
-- Name: chats chats_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(userid) ON DELETE CASCADE;


--
-- Name: slides slides_chatid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slides
    ADD CONSTRAINT slides_chatid_fkey FOREIGN KEY (chatid) REFERENCES public.chats(chatid) ON DELETE CASCADE;


--
-- Name: tasks tasks_chatid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_chatid_fkey FOREIGN KEY (chatid) REFERENCES public.chats(chatid) ON DELETE CASCADE;


--
-- Name: tasks tasks_versionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_versionid_fkey FOREIGN KEY (versionid) REFERENCES public.versions(versionid) ON DELETE CASCADE;


--
-- Name: versions versions_slideid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.versions
    ADD CONSTRAINT versions_slideid_fkey FOREIGN KEY (slideid) REFERENCES public.slides(slideid) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict m3p0KUL7fowb5SC09I3ALaMvhUs5DhQhCUB9Iz3Y03Vg97hzBZJTAZ8I5ODcoLL

