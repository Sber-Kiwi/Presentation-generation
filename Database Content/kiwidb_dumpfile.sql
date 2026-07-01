--
-- PostgreSQL database dump
--

\restrict dUZRA86kmoGT4LogBQlPWr8WbhmI6eyE5uWhdUq9AaLBmesd5uMaB7GGiiLnHCF

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
    metricid integer NOT NULL,
    name character varying(50),
    CONSTRAINT chk_metric_name CHECK ((char_length(TRIM(BOTH FROM name)) > 0))
);


ALTER TABLE public.metrics OWNER TO postgres;

--
-- Name: metrics_metricid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.metrics_metricid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.metrics_metricid_seq OWNER TO postgres;

--
-- Name: metrics_metricid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.metrics_metricid_seq OWNED BY public.metrics.metricid;


--
-- Name: slides; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.slides (
    slideid integer NOT NULL,
    chatid integer,
    metricid integer,
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
-- Name: metrics metricid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metrics ALTER COLUMN metricid SET DEFAULT nextval('public.metrics_metricid_seq'::regclass);


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
1	1	1	1	Анализ продаж Q1	Сгенерируй презентацию для анализ продаж q1	2026-07-01 12:25:05.541081+03
2	2	2	2	Отчет по маркетингу	Сгенерируй презентацию для отчет по маркетингу	2026-07-01 12:25:05.541081+03
3	3	3	3	Финансовые показатели	Сгенерируй презентацию для финансовые показатели	2026-07-01 12:25:05.541081+03
4	4	4	4	HR метрики	Сгенерируй презентацию для hr метрики	2026-07-01 12:25:05.541081+03
5	5	5	5	Прогноз на год	Сгенерируй презентацию для прогноз на год	2026-07-01 12:25:05.541081+03
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

COPY public.metrics (metricid, name) FROM stdin;
1	Accuracy
2	F1-Score
3	Precision
4	Recall
\.


--
-- Data for Name: slides; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.slides (slideid, chatid, metricid, num) FROM stdin;
1	1	3	1
2	1	4	2
3	1	3	3
4	1	2	4
5	1	1	5
6	1	2	6
7	2	4	1
8	2	4	2
9	2	4	3
10	2	2	4
11	2	2	5
12	2	1	6
13	3	1	1
14	3	1	2
15	3	1	3
16	3	3	4
17	3	4	5
18	3	1	6
19	4	4	1
20	4	4	2
21	4	2	3
22	4	2	4
23	4	1	5
24	4	3	6
25	5	2	1
26	5	2	2
27	5	1	3
28	5	2	4
29	5	4	5
30	5	1	6
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (taskid, chatid, versionid, type, prompt, status) FROM stdin;
1	1	8	2	Обработать версию 8 для чата 1	1
2	2	30	2	Обработать версию 30 для чата 2	2
3	3	77	2	Обработать версию 77 для чата 3	1
4	4	114	1	Обработать версию 114 для чата 4	2
5	5	119	2	Обработать версию 119 для чата 5	0
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
1	1	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
2	1	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
3	1	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
4	1	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
5	2	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
6	2	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
7	2	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
8	2	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
9	3	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
10	3	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
11	3	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
12	3	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
13	4	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
14	4	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
15	4	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
16	4	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
17	4	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
18	5	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
19	5	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
20	5	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
21	5	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
22	5	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-01 13:05:05.597938+03	f
23	5	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
24	6	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
25	6	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
26	6	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
27	6	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
28	7	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
29	7	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
30	7	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
31	7	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
32	7	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
33	8	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
34	8	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
35	8	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
36	8	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
37	8	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-01 13:05:05.597938+03	f
38	8	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
39	9	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
40	9	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
41	9	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
42	9	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
43	10	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
44	10	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
45	10	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
46	10	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
47	10	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-01 13:05:05.597938+03	f
48	10	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
49	11	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
50	11	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
51	11	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
52	11	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
53	12	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
54	12	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
55	12	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
56	12	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
57	12	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
58	13	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
59	13	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
60	13	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
61	13	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
62	14	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
63	14	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
64	14	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
65	14	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
66	14	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
67	15	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
68	15	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
69	15	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
70	15	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
71	15	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
72	16	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
73	16	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
74	16	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
75	16	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
76	16	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
77	17	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
78	17	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
79	17	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
80	17	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
81	18	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
82	18	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
83	18	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
84	18	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
85	18	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-01 13:05:05.597938+03	f
86	18	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
87	19	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
88	19	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
89	19	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
90	19	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
91	20	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
92	20	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
93	20	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
94	20	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
95	20	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
96	21	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
97	21	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
98	21	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
99	21	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
100	22	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
101	22	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
102	22	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
103	22	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
104	22	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-01 13:05:05.597938+03	f
105	22	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
106	23	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
107	23	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
108	23	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
109	23	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
110	24	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
111	24	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
112	24	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
113	24	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
114	24	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
115	25	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
116	25	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
117	25	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
118	25	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
119	25	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
120	26	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
121	26	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
122	26	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
123	26	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
124	27	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
125	27	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
126	27	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
127	27	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
128	27	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
129	28	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
130	28	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
131	28	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
132	28	{"status": "draft", "changes": "Правка 4", "iteration": 4}	Что-то сделать	2026-07-01 12:55:05.597938+03	f
133	28	{"status": "draft", "changes": "Правка 5", "iteration": 5}	Что-то сделать	2026-07-01 13:05:05.597938+03	f
134	28	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
135	29	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
136	29	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
137	29	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
138	29	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
139	30	{"status": "draft", "changes": "Правка 1", "iteration": 1}	Что-то сделать	2026-07-01 12:25:05.597938+03	f
140	30	{"status": "draft", "changes": "Правка 2", "iteration": 2}	Что-то сделать	2026-07-01 12:35:05.597938+03	f
141	30	{"status": "draft", "changes": "Правка 3", "iteration": 3}	Что-то сделать	2026-07-01 12:45:05.597938+03	f
142	30	{"status": "final", "version": "1.0", "approved": true}	Заменить график на гистограмму	2026-07-01 12:25:05.541081+03	t
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
-- Name: metrics_metricid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.metrics_metricid_seq', 4, true);


--
-- Name: slides_slideid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.slides_slideid_seq', 30, true);


--
-- Name: tasks_taskid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_taskid_seq', 5, true);


--
-- Name: users_userid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_userid_seq', 5, true);


--
-- Name: versions_versionid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.versions_versionid_seq', 142, true);


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
    ADD CONSTRAINT metrics_pkey PRIMARY KEY (metricid);


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
-- Name: slides slides_metricid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slides
    ADD CONSTRAINT slides_metricid_fkey FOREIGN KEY (metricid) REFERENCES public.metrics(metricid) ON DELETE CASCADE;


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

\unrestrict dUZRA86kmoGT4LogBQlPWr8WbhmI6eyE5uWhdUq9AaLBmesd5uMaB7GGiiLnHCF

