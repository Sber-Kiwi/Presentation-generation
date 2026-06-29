--
-- PostgreSQL database dump
--

\restrict akNtNtlZYaNH1pdiyqm7gCdS2wxo0vv4LSsfSVBc5U7xi2Em8Al2VhKnkRjex8e

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
-- Name: metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.metrics (
    metricaid integer NOT NULL,
    name character varying(50),
    CONSTRAINT chk_metric_name CHECK ((char_length(TRIM(BOTH FROM name)) > 0))
);


ALTER TABLE public.metrics OWNER TO postgres;

--
-- Name: metrics_metricaid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.metrics_metricaid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.metrics_metricaid_seq OWNER TO postgres;

--
-- Name: metrics_metricaid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.metrics_metricaid_seq OWNED BY public.metrics.metricaid;


--
-- Name: slides; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.slides (
    slideid integer NOT NULL,
    chatid integer,
    metricaid integer,
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
    CONSTRAINT chk_task_prompt CHECK ((char_length(TRIM(BOTH FROM prompt)) > 0)),
    CONSTRAINT chk_task_status CHECK (((status >= 0) AND (status <= 2)))
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
-- Name: metrics metricaid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metrics ALTER COLUMN metricaid SET DEFAULT nextval('public.metrics_metricaid_seq'::regclass);


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
1	1	1	1	Анализ продаж Q1	Сгенерируй презентацию для анализ продаж q1	2026-06-29 12:07:13.447423+03
2	2	2	2	Отчет по маркетингу	Сгенерируй презентацию для отчет по маркетингу	2026-06-29 12:07:13.447423+03
3	3	3	3	Финансовые показатели	Сгенерируй презентацию для финансовые показатели	2026-06-29 12:07:13.447423+03
4	4	4	4	HR метрики	Сгенерируй презентацию для hr метрики	2026-06-29 12:07:13.447423+03
5	5	5	5	Прогноз на год	Сгенерируй презентацию для прогноз на год	2026-06-29 12:07:13.447423+03
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
-- Data for Name: metrics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.metrics (metricaid, name) FROM stdin;
1	Accuracy
2	F1-Score
3	Precision
4	Recall
\.


--
-- Data for Name: slides; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.slides (slideid, chatid, metricaid, num) FROM stdin;
1	1	4	1
2	1	3	2
3	1	1	3
4	1	1	4
5	1	1	5
6	1	2	6
7	2	2	1
8	2	1	2
9	2	3	3
10	2	1	4
11	2	2	5
12	2	4	6
13	3	4	1
14	3	3	2
15	3	1	3
16	3	1	4
17	3	4	5
18	3	2	6
19	4	3	1
20	4	2	2
21	4	4	3
22	4	4	4
23	4	3	5
24	4	1	6
25	5	4	1
26	5	3	2
27	5	1	3
28	5	1	4
29	5	3	5
30	5	1	6
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (taskid, chatid, versionid, type, prompt, status) FROM stdin;
1	1	11	1	Обработать версию 11 для чата 1	0
2	1	27	2	Обработать версию 27 для чата 1	1
3	1	4	2	Обработать версию 4 для чата 1	2
4	2	43	1	Обработать версию 43 для чата 2	0
5	2	39	2	Обработать версию 39 для чата 2	1
6	2	56	3	Обработать версию 56 для чата 2	2
7	3	93	3	Обработать версию 93 для чата 3	0
8	3	62	3	Обработать версию 62 для чата 3	1
9	3	65	3	Обработать версию 65 для чата 3	2
10	4	95	1	Обработать версию 95 для чата 4	0
11	4	97	3	Обработать версию 97 для чата 4	1
12	4	102	1	Обработать версию 102 для чата 4	2
13	5	148	2	Обработать версию 148 для чата 5	0
14	5	143	2	Обработать версию 143 для чата 5	1
15	5	130	1	Обработать версию 130 для чата 5	2
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
1	1	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
2	1	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
3	1	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
4	1	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
5	2	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
6	2	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
7	2	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
8	2	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
9	2	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
10	3	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
11	3	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
12	3	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
13	3	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
14	3	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
15	3	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
16	4	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
17	4	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
18	4	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
19	4	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
20	5	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
21	5	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
22	5	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
23	5	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
24	5	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
25	6	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
26	6	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
27	6	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
28	6	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
29	6	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
30	7	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
31	7	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
32	7	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
33	7	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
34	7	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
35	7	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
36	8	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
37	8	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
38	8	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
39	8	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
40	9	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
41	9	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
42	9	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
43	9	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
44	9	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
45	10	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
46	10	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
47	10	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
48	10	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
49	10	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
50	10	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
51	11	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
52	11	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
53	11	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
54	11	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
55	11	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
56	12	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
57	12	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
58	12	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
59	12	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
60	12	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
61	12	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
62	13	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
63	13	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
64	13	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
65	13	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
66	13	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
67	13	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
68	14	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
69	14	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
70	14	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
71	14	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
72	14	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
73	15	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
74	15	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
75	15	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
76	15	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
77	15	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
78	16	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
79	16	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
80	16	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
81	16	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
82	16	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
83	17	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
84	17	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
85	17	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
86	17	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
87	17	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
88	17	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
89	18	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
90	18	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
91	18	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
92	18	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
93	18	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
94	18	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
95	19	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
96	19	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
97	19	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
98	19	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
99	20	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
100	20	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
101	20	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
102	20	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
103	21	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
104	21	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
105	21	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
106	21	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
107	21	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
108	21	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
109	22	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
110	22	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
111	22	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
112	22	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
113	22	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
114	22	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
115	23	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
116	23	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
117	23	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
118	23	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
119	24	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
120	24	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
121	24	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
122	24	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
123	24	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
124	25	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
125	25	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
126	25	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
127	25	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
128	26	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
129	26	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
130	26	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
131	26	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
132	26	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
133	27	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
134	27	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
135	27	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
136	27	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
137	27	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
138	27	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
139	28	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
140	28	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
141	28	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
142	28	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
143	28	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
144	29	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
145	29	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
146	29	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
147	29	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
148	30	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
149	30	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
150	30	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
151	30	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-06-29 12:07:13.447423+03	f
152	30	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-06-29 12:07:13.447423+03	t
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
-- Name: metrics_metricaid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.metrics_metricaid_seq', 4, true);


--
-- Name: slides_slideid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.slides_slideid_seq', 30, true);


--
-- Name: tasks_taskid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_taskid_seq', 15, true);


--
-- Name: users_userid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_userid_seq', 5, true);


--
-- Name: versions_versionid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.versions_versionid_seq', 152, true);


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
-- Name: metrics metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metrics
    ADD CONSTRAINT metrics_pkey PRIMARY KEY (metricaid);


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
-- Name: slides slides_metricaid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slides
    ADD CONSTRAINT slides_metricaid_fkey FOREIGN KEY (metricaid) REFERENCES public.metrics(metricaid) ON DELETE CASCADE;


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

\unrestrict akNtNtlZYaNH1pdiyqm7gCdS2wxo0vv4LSsfSVBc5U7xi2Em8Al2VhKnkRjex8e

