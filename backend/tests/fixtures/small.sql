--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.15
-- Dumped by pg_dump version 9.5.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: aktivitet; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.aktivitet (id) FROM stdin;
\.


--
-- Data for Name: aktivitet_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.aktivitet_registrering (id, aktivitet_id, registrering) FROM stdin;
\.


--
-- Data for Name: aktivitet_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.aktivitet_attr_egenskaber (id, brugervendtnoegle, aktivitetnavn, beskrivelse, starttidspunkt, sluttidspunkt, tidsforbrug, formaal, integrationsdata, virkning, aktivitet_registrering_id) FROM stdin;
\.


--
-- Name: aktivitet_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.aktivitet_attr_egenskaber_id_seq', 1, false);


--
-- Name: aktivitet_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.aktivitet_registrering_id_seq', 1, false);


--
-- Data for Name: aktivitet_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.aktivitet_relation (id, aktivitet_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type, rel_index, aktoer_attr) FROM stdin;
\.


--
-- Name: aktivitet_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.aktivitet_relation_id_seq', 1, false);


--
-- Data for Name: aktivitet_tils_publiceret; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.aktivitet_tils_publiceret (id, virkning, publiceret, aktivitet_registrering_id) FROM stdin;
\.


--
-- Name: aktivitet_tils_publiceret_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.aktivitet_tils_publiceret_id_seq', 1, false);


--
-- Data for Name: aktivitet_tils_status; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.aktivitet_tils_status (id, virkning, status, aktivitet_registrering_id) FROM stdin;
\.


--
-- Name: aktivitet_tils_status_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.aktivitet_tils_status_id_seq', 1, false);


--
-- Data for Name: bruger; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.bruger (id) FROM stdin;
0327b1cc-ad1a-47f2-aa14-e7278a92251f
fe6583da-3f63-43af-aeaa-e3cca9a5071f
0133916a-4449-4885-9db4-cea379af2d71
39c885cd-3bdb-4861-9316-4b8b8cd3c835
efa52e33-1b2e-4b06-999f-fb5af8fdefdb
bd910c76-5658-453a-9a7b-ba056c7dd561
608a3e4f-e9ac-49f1-8c64-efb1b2338cd4
25044a31-e4eb-4725-8dff-0ff8f032ae53
78bb9fd5-2c03-4d6a-9ea8-86f1a9c667f1
29fda44c-0e49-47d7-b68a-3cd6831095ba
1d41c22d-7796-4266-a07f-65c430593bfe
8d5b5521-9bff-46ab-aa91-44fd671ede6d
958aee35-13d5-49d5-98f2-348cd590d600
15a22fde-b7ae-424a-be74-f198ad00d915
bb84d7fa-bc05-4466-9051-d1c6208650ad
d8084037-6f9d-46ad-889a-0408aa6309a7
e4b34d8c-d824-4bca-a955-c08bd547742c
d3fff832-5740-451d-ac2d-5fcbb4a1822f
b15a3d56-2a60-48b5-9b4a-2d459b829fd0
f5e05fc2-a484-4fb5-95d3-d9ba89adc52e
9ff61686-1144-457b-b735-bf1871379cca
3187c0db-9b0d-4368-b756-de018f9b6ef9
936cb72e-dc1a-49a3-a297-e97f2d480195
38793c9c-3b30-4a3a-a63b-4894d943d2bc
5aee93fb-ce29-4518-98e0-643e4932c329
6b222d46-3260-4479-955c-d485eb16acca
3c45c707-9ae0-41fc-af91-b94f69e28a56
6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55
419e5157-6173-4b36-967d-17a5556c1279
23768c40-05bf-4d0d-b263-495750673b31
773abd21-fb11-44a6-930e-74227ad6a470
20bd601d-581a-4d96-96b7-188e7645bc24
139b917c-7135-4c26-847c-e13c9f871c87
c0e5f7cf-66c7-41d4-8dcb-6137da5d2343
74aa1e09-a97f-4465-94dc-f6568d31451d
96282f58-e10e-4d4f-ae1a-f25658d68cc8
a9b06498-92aa-4fde-b543-ed8661caa02e
de47b9c8-283f-4ea9-9bdf-0795eb5d6a50
1969059e-5b9e-43d7-ad9c-01f697c5bfc9
ba02c1bc-dd1d-4b04-8f6b-a6093d27a85e
0d2d249d-83ca-40f1-ac89-be7e246e7541
89e4bf94-8b1d-4ae0-bca2-3465a06f9f08
8ca64fe4-6231-48e9-818e-34e559a0574f
03f084de-3552-4817-b15b-21a5056366d4
17c12fbd-8816-4536-923c-cad5c749647e
73e0730b-d815-45f3-aad3-1ce9873741f3
\.


--
-- Data for Name: bruger_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.bruger_registrering (id, bruger_id, registrering) FROM stdin;
1	0327b1cc-ad1a-47f2-aa14-e7278a92251f	("[""2019-03-18 17:51:29.21603+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
2	fe6583da-3f63-43af-aeaa-e3cca9a5071f	("[""2019-03-18 17:51:29.779374+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
3	0133916a-4449-4885-9db4-cea379af2d71	("[""2019-03-18 17:51:30.445857+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
4	39c885cd-3bdb-4861-9316-4b8b8cd3c835	("[""2019-03-18 17:51:31.030826+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
5	efa52e33-1b2e-4b06-999f-fb5af8fdefdb	("[""2019-03-18 17:51:31.603909+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
6	bd910c76-5658-453a-9a7b-ba056c7dd561	("[""2019-03-18 17:51:32.196102+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
7	608a3e4f-e9ac-49f1-8c64-efb1b2338cd4	("[""2019-03-18 17:51:32.731268+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
8	25044a31-e4eb-4725-8dff-0ff8f032ae53	("[""2019-03-18 17:51:33.345634+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
9	78bb9fd5-2c03-4d6a-9ea8-86f1a9c667f1	("[""2019-03-18 17:51:33.938853+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
10	29fda44c-0e49-47d7-b68a-3cd6831095ba	("[""2019-03-18 17:51:34.544407+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
11	1d41c22d-7796-4266-a07f-65c430593bfe	("[""2019-03-18 17:51:35.227937+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
12	8d5b5521-9bff-46ab-aa91-44fd671ede6d	("[""2019-03-18 17:51:35.808502+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
13	958aee35-13d5-49d5-98f2-348cd590d600	("[""2019-03-18 17:51:36.32624+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
14	15a22fde-b7ae-424a-be74-f198ad00d915	("[""2019-03-18 17:51:36.876464+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
15	bb84d7fa-bc05-4466-9051-d1c6208650ad	("[""2019-03-18 17:51:37.417695+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
16	d8084037-6f9d-46ad-889a-0408aa6309a7	("[""2019-03-18 17:51:37.965719+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
17	e4b34d8c-d824-4bca-a955-c08bd547742c	("[""2019-03-18 17:51:38.503541+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
18	d3fff832-5740-451d-ac2d-5fcbb4a1822f	("[""2019-03-18 17:51:38.995491+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
19	b15a3d56-2a60-48b5-9b4a-2d459b829fd0	("[""2019-03-18 17:51:39.612065+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
20	f5e05fc2-a484-4fb5-95d3-d9ba89adc52e	("[""2019-03-18 17:51:40.203182+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
21	9ff61686-1144-457b-b735-bf1871379cca	("[""2019-03-18 17:51:40.737263+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
22	3187c0db-9b0d-4368-b756-de018f9b6ef9	("[""2019-03-18 17:51:41.357064+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
23	936cb72e-dc1a-49a3-a297-e97f2d480195	("[""2019-03-18 17:51:41.87505+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
24	38793c9c-3b30-4a3a-a63b-4894d943d2bc	("[""2019-03-18 17:51:42.372849+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
25	5aee93fb-ce29-4518-98e0-643e4932c329	("[""2019-03-18 17:51:42.927274+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
26	6b222d46-3260-4479-955c-d485eb16acca	("[""2019-03-18 17:51:43.473051+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
27	3c45c707-9ae0-41fc-af91-b94f69e28a56	("[""2019-03-18 17:51:44.03459+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
28	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55	("[""2019-03-18 17:51:44.545873+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
29	419e5157-6173-4b36-967d-17a5556c1279	("[""2019-03-18 17:51:45.152109+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
30	23768c40-05bf-4d0d-b263-495750673b31	("[""2019-03-18 17:51:45.690293+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
31	773abd21-fb11-44a6-930e-74227ad6a470	("[""2019-03-18 17:51:46.240363+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
32	20bd601d-581a-4d96-96b7-188e7645bc24	("[""2019-03-18 17:51:46.796712+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
33	139b917c-7135-4c26-847c-e13c9f871c87	("[""2019-03-18 17:51:47.354707+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
34	c0e5f7cf-66c7-41d4-8dcb-6137da5d2343	("[""2019-03-18 17:51:47.910603+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
35	74aa1e09-a97f-4465-94dc-f6568d31451d	("[""2019-03-18 17:51:48.446039+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
36	96282f58-e10e-4d4f-ae1a-f25658d68cc8	("[""2019-03-18 17:51:48.931512+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
37	a9b06498-92aa-4fde-b543-ed8661caa02e	("[""2019-03-18 17:51:49.521971+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
38	de47b9c8-283f-4ea9-9bdf-0795eb5d6a50	("[""2019-03-18 17:51:50.057967+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
39	1969059e-5b9e-43d7-ad9c-01f697c5bfc9	("[""2019-03-18 17:51:50.589083+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
40	ba02c1bc-dd1d-4b04-8f6b-a6093d27a85e	("[""2019-03-18 17:51:51.166038+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
41	0d2d249d-83ca-40f1-ac89-be7e246e7541	("[""2019-03-18 17:51:51.701091+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
42	89e4bf94-8b1d-4ae0-bca2-3465a06f9f08	("[""2019-03-18 17:51:52.284173+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
43	8ca64fe4-6231-48e9-818e-34e559a0574f	("[""2019-03-18 17:51:52.776898+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
44	03f084de-3552-4817-b15b-21a5056366d4	("[""2019-03-18 17:51:53.368219+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
45	17c12fbd-8816-4536-923c-cad5c749647e	("[""2019-03-18 17:51:53.942939+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
46	73e0730b-d815-45f3-aad3-1ce9873741f3	("[""2019-03-18 17:51:54.503319+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
\.


--
-- Data for Name: bruger_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.bruger_attr_egenskaber (id, brugervendtnoegle, brugernavn, brugertype, integrationsdata, virkning, bruger_registrering_id) FROM stdin;
1	e10359e4-c237-4146-b1cd-1ce164ec8e58	Duncan Underlin Hansen	\N	{"Artificial import": "\\"DuncanH\\"STOP"}	("[""1954-01-03 00:00:00+01"",infinity)",,,"")	1
2	50e8a48d-f49c-4a29-9f27-cdcdd97943cd	Ellen Jensen Christensen	\N	{"Artificial import": "\\"EllenC\\"STOP"}	("[""1942-11-06 00:00:00+01"",infinity)",,,"")	2
3	02ce7fc4-10d8-449e-9ae7-d988db3359df	Annesofie Jønsson	\N	{"Artificial import": "\\"AnnesofieJ\\"STOP"}	("[""1947-12-28 00:00:00+01"",infinity)",,,"")	3
4	b95b91b0-b738-4eb1-83b2-335b60e3a71e	Anna Gorm Fallesen	\N	{"Artificial import": "\\"AnnaF\\"STOP"}	("[""1949-10-08 00:00:00+01"",infinity)",,,"")	4
5	6b9820d4-de07-4d7b-8050-6489efbc957c	Bente Hviid Madsen	\N	{"Artificial import": "\\"BenteM\\"STOP"}	("[""1985-01-25 00:00:00+01"",infinity)",,,"")	5
6	eb8763e8-780e-4c13-ad2f-608a0d60e430	Jørn Vestergaard Pedersen	\N	{"Artificial import": "\\"J\\\\u00f8rnP\\"STOP"}	("[""1975-06-29 00:00:00+01"",infinity)",,,"")	6
7	00c09757-9453-47bd-898e-946b628840ee	Robert Gelting	\N	{"Artificial import": "\\"RobertG\\"STOP"}	("[""1943-11-06 00:00:00+01"",infinity)",,,"")	7
8	cae17564-00d8-47b6-b634-8c352a416075	Brian Stenbak Strøyberg	\N	{"Artificial import": "\\"BrianS\\"STOP"}	("[""1940-11-16 00:00:00+02"",infinity)",,,"")	8
9	bf51f09c-1385-4726-80a9-c7bb65ff534f	Betinna Banke Jørgensen	\N	{"Artificial import": "\\"BetinnaJ\\"STOP"}	("[""1953-11-28 00:00:00+01"",infinity)",,,"")	9
10	0bca1f8d-cf5d-48fa-a5dd-1b1aa6e1b218	Dorrit Skovmark Jørgensen	\N	{"Artificial import": "\\"DorritJ\\"STOP"}	("[""1942-10-02 00:00:00+02"",infinity)",,,"")	10
11	835e86ba-997d-48bb-b0a8-2b5f9f59711f	Hjalmar Jensen Jensen	\N	{"Artificial import": "\\"HjalmarJ\\"STOP"}	("[""1945-03-04 00:00:00+01"",infinity)",,,"")	11
12	2f2bec52-945c-423a-9657-1a01a848bb49	Peter Rønsholt Bengtsson	\N	{"Artificial import": "\\"PeterB\\"STOP"}	("[""1957-03-19 00:00:00+01"",infinity)",,,"")	12
13	af287b11-ff0a-4aff-ad9b-c797c1c7166c	Kirsten Sødergaard	\N	{"Artificial import": "\\"KirstenS\\"STOP"}	("[""1947-02-11 00:00:00+01"",infinity)",,,"")	13
14	a8fa984c-bbad-41be-a0e4-6034e96d2caf	Marie Lützhøft Bleibach	\N	{"Artificial import": "\\"MarieB\\"STOP"}	("[""1987-03-13 00:00:00+01"",infinity)",,,"")	14
15	86400d64-93ee-4bbc-a498-eafb1de9e564	Børge Sig Brander	\N	{"Artificial import": "\\"B\\\\u00f8rgeB\\"STOP"}	("[""1994-01-21 00:00:00+01"",infinity)",,,"")	15
16	649c9eab-fdce-49e6-b69c-12720e41b9c6	Ole Kaas Jørgensen	\N	{"Artificial import": "\\"OleJ\\"STOP"}	("[""1940-11-23 00:00:00+02"",infinity)",,,"")	16
17	4f2e6a6a-806c-434c-b40a-a4131a89ca88	Karen Lybecker Hummelshøj	\N	{"Artificial import": "\\"KarenH\\"STOP"}	("[""1957-05-27 00:00:00+01"",infinity)",,,"")	17
18	a1aa504e-bb4e-43f9-b8df-cb147ec9f7a2	Gustav Klingenberg Brund Knudsen	\N	{"Artificial import": "\\"GustavK\\"STOP"}	("[""1963-05-25 00:00:00+01"",infinity)",,,"")	18
19	d432ca4c-5fd4-4551-a119-0aa5ac855857	Jens Grønlund Lauritsen	\N	{"Artificial import": "\\"JensL\\"STOP"}	("[""1952-01-05 00:00:00+01"",infinity)",,,"")	19
20	12bd0516-639e-4936-a4cd-40ac4f1f6fc9	Birgitte Hansen	\N	{"Artificial import": "\\"BirgitteH\\"STOP"}	("[""1963-06-20 00:00:00+01"",infinity)",,,"")	20
21	2fe0fd39-17bb-4137-8672-8c1d8071a020	Eva Kornum Christensen	\N	{"Artificial import": "\\"EvaC\\"STOP"}	("[""1946-12-31 00:00:00+01"",infinity)",,,"")	21
22	398cadc6-2abe-4ed4-bbab-3207e67e309b	Gunner Nielsen	\N	{"Artificial import": "\\"GunnerN\\"STOP"}	("[""1973-01-25 00:00:00+01"",infinity)",,,"")	22
23	9bb16193-abdb-4f72-99f2-3975aa75c71e	Aage Junker	\N	{"Artificial import": "\\"AageJ\\"STOP"}	("[""1968-07-04 00:00:00+01"",infinity)",,,"")	23
24	140439ad-57e5-4fd0-8ed0-c6ca1be4afde	Flemming Bach Lassen	\N	{"Artificial import": "\\"FlemmingL\\"STOP"}	("[""1942-04-09 00:00:00+02"",infinity)",,,"")	24
25	5c4f0ccb-e5d5-41cf-bdcb-dafccd914a03	Poula Hoffmann Nielsen	\N	{"Artificial import": "\\"PoulaN\\"STOP"}	("[""1943-08-22 00:00:00+02"",infinity)",,,"")	25
26	69294162-4780-42f9-8d01-03c5380f06cf	Egon Jørgensen	\N	{"Artificial import": "\\"EgonJ\\"STOP"}	("[""1950-02-28 00:00:00+01"",infinity)",,,"")	26
27	1910fbf9-45de-4b44-86a1-e02df85a3162	Poul Meier Schulz	\N	{"Artificial import": "\\"PoulS\\"STOP"}	("[""1940-03-28 00:00:00+01"",infinity)",,,"")	27
28	56031b75-7e28-4319-bb67-a63d467cd142	Marthine Storgaard Hansen	\N	{"Artificial import": "\\"MarthineH\\"STOP"}	("[""1970-01-27 00:00:00+01"",infinity)",,,"")	28
29	70169fd2-e612-4b3a-9d6c-139d2ae5ce12	Mads Rasmussen	\N	{"Artificial import": "\\"MadsR\\"STOP"}	("[""1940-08-15 00:00:00+02"",infinity)",,,"")	29
30	9b831c9c-f51c-4738-ac81-93faf1925e56	Anne Jørgensen	\N	{"Artificial import": "\\"AnneJ\\"STOP"}	("[""1952-06-17 00:00:00+01"",infinity)",,,"")	30
31	9730bbdd-7042-4eff-a80d-ad9e78f596d7	Michael Lenander Warming	\N	{"Artificial import": "\\"MichaelW\\"STOP"}	("[""1968-02-13 00:00:00+01"",infinity)",,,"")	31
32	ccbe92b8-8aa4-47f1-8215-575748386d0a	Helga Jensen	\N	{"Artificial import": "\\"HelgaJ\\"STOP"}	("[""1969-12-16 00:00:00+01"",infinity)",,,"")	32
33	889ccdc9-f563-4eb0-b3e0-be2af908f6ae	Anton Eskelund Sørensen	\N	{"Artificial import": "\\"AntonS\\"STOP"}	("[""1967-04-24 00:00:00+01"",infinity)",,,"")	33
34	01e43c02-7e5e-486f-93fc-0b3a44558c6d	Anna Hansen	\N	{"Artificial import": "\\"AnnaH\\"STOP"}	("[""1944-08-04 00:00:00+02"",infinity)",,,"")	34
35	ec8ae6ee-ae74-4185-a42e-cbac2058dc3e	Karen Søndergaard Jakobsen	\N	{"Artificial import": "\\"KarenJ\\"STOP"}	("[""1951-06-28 00:00:00+01"",infinity)",,,"")	35
36	ea99434b-e51a-44ff-b527-da9544727460	Alma Lenbroch	\N	{"Artificial import": "\\"AlmaL\\"STOP"}	("[""1947-02-18 00:00:00+01"",infinity)",,,"")	36
37	1e93b582-03f7-4493-aae1-3163d9004498	Valborg Dehn Nielsen	\N	{"Artificial import": "\\"ValborgN\\"STOP"}	("[""1972-08-11 00:00:00+01"",infinity)",,,"")	37
38	cb7e968d-01f5-46df-9981-89be886b490e	Tina Winther Krarup Cam	\N	{"Artificial import": "\\"TinaC\\"STOP"}	("[""1940-02-26 00:00:00+01"",infinity)",,,"")	38
39	4dcda43b-f425-4468-9faa-1e44aceafac3	Mie Poulsen	\N	{"Artificial import": "\\"MieP\\"STOP"}	("[""1945-05-22 00:00:00+02"",infinity)",,,"")	39
40	dfddde1d-f0d7-4794-95e3-728d0ec23ae5	B Holler Christiansen	\N	{"Artificial import": "\\"BC\\"STOP"}	("[""1941-07-12 00:00:00+02"",infinity)",,,"")	40
41	8fcef1a5-f1b6-47e3-86fc-67cc48e88d08	Ryan Kristian Skov	\N	{"Artificial import": "\\"RyanS\\"STOP"}	("[""1948-01-17 00:00:00+01"",infinity)",,,"")	41
42	42c455c5-1cf1-4f03-a941-c453cbea75e4	Palle Hantusch Caspersen	\N	{"Artificial import": "\\"PalleC\\"STOP"}	("[""1944-02-14 00:00:00+01"",infinity)",,,"")	42
43	a7d0b0ba-1778-483b-a0e4-706b13f2edd1	Edith Petersen Ingemann Eriksen	\N	{"Artificial import": "\\"EdithE\\"STOP"}	("[""1981-01-26 00:00:00+01"",infinity)",,,"")	43
44	57e4e082-f2da-40f4-98f8-cb2989e9c48c	Jelva Banja Paulsen	\N	{"Artificial import": "\\"JelvaP\\"STOP"}	("[""1948-06-19 00:00:00+02"",infinity)",,,"")	44
45	e059e5f6-1c48-4239-b351-d1c777359f46	Else Christensen	\N	{"Artificial import": "\\"ElseC\\"STOP"}	("[""1971-02-25 00:00:00+01"",infinity)",,,"")	45
46	76c3898b-20dc-46a9-afff-442ef6939e9f	Mie Klingenbjerg Haagh	\N	{"Artificial import": "\\"MieH\\"STOP"}	("[""1980-08-06 00:00:00+02"",infinity)",,,"")	46
\.


--
-- Name: bruger_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.bruger_attr_egenskaber_id_seq', 46, true);


--
-- Name: bruger_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.bruger_registrering_id_seq', 46, true);


--
-- Data for Name: bruger_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.bruger_relation (id, bruger_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""1954-01-03 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
2	1	("[""1954-01-03 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:0301543212	tilknyttedepersoner	\N
3	2	("[""1942-11-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
4	2	("[""1942-11-06 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:0611422717	tilknyttedepersoner	\N
5	3	("[""1947-12-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
6	3	("[""1947-12-28 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2812472863	tilknyttedepersoner	\N
7	4	("[""1949-10-08 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
8	4	("[""1949-10-08 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:0810490594	tilknyttedepersoner	\N
9	5	("[""1985-01-25 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
10	5	("[""1985-01-25 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2501853812	tilknyttedepersoner	\N
11	6	("[""1975-06-29 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
12	6	("[""1975-06-29 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2906752940	tilknyttedepersoner	\N
13	7	("[""1943-11-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
14	7	("[""1943-11-06 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:0611432887	tilknyttedepersoner	\N
15	8	("[""1940-11-16 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
16	8	("[""1940-11-16 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:1611402275	tilknyttedepersoner	\N
17	9	("[""1953-11-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
18	9	("[""1953-11-28 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2811533125	tilknyttedepersoner	\N
19	10	("[""1942-10-02 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
20	10	("[""1942-10-02 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:0210422501	tilknyttedepersoner	\N
21	11	("[""1945-03-04 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
22	11	("[""1945-03-04 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:0403451274	tilknyttedepersoner	\N
23	12	("[""1957-03-19 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
24	12	("[""1957-03-19 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1903571574	tilknyttedepersoner	\N
25	13	("[""1947-02-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
26	13	("[""1947-02-11 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1102473171	tilknyttedepersoner	\N
27	14	("[""1987-03-13 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
28	14	("[""1987-03-13 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1303873119	tilknyttedepersoner	\N
29	15	("[""1994-01-21 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
30	15	("[""1994-01-21 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2101943952	tilknyttedepersoner	\N
31	16	("[""1940-11-23 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
32	16	("[""1940-11-23 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:2311403225	tilknyttedepersoner	\N
33	17	("[""1957-05-27 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
34	17	("[""1957-05-27 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2705570879	tilknyttedepersoner	\N
35	18	("[""1963-05-25 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
36	18	("[""1963-05-25 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2505633590	tilknyttedepersoner	\N
37	19	("[""1952-01-05 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
38	19	("[""1952-01-05 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:0501521973	tilknyttedepersoner	\N
39	20	("[""1963-06-20 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
40	20	("[""1963-06-20 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2006631730	tilknyttedepersoner	\N
41	21	("[""1946-12-31 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
42	21	("[""1946-12-31 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:3112463355	tilknyttedepersoner	\N
43	22	("[""1973-01-25 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
44	22	("[""1973-01-25 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2501731148	tilknyttedepersoner	\N
45	23	("[""1968-07-04 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
46	23	("[""1968-07-04 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:0407680731	tilknyttedepersoner	\N
47	24	("[""1942-04-09 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
48	24	("[""1942-04-09 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:0904422258	tilknyttedepersoner	\N
49	25	("[""1943-08-22 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
50	25	("[""1943-08-22 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:2208431458	tilknyttedepersoner	\N
51	26	("[""1950-02-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
52	26	("[""1950-02-28 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2802500761	tilknyttedepersoner	\N
53	27	("[""1940-03-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
54	27	("[""1940-03-28 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2803402976	tilknyttedepersoner	\N
55	28	("[""1970-01-27 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
56	28	("[""1970-01-27 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2701700387	tilknyttedepersoner	\N
57	29	("[""1940-08-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
58	29	("[""1940-08-15 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:1508403522	tilknyttedepersoner	\N
59	30	("[""1952-06-17 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
60	30	("[""1952-06-17 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1706523177	tilknyttedepersoner	\N
61	31	("[""1968-02-13 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
62	31	("[""1968-02-13 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1302681496	tilknyttedepersoner	\N
63	32	("[""1969-12-16 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
64	32	("[""1969-12-16 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1612693974	tilknyttedepersoner	\N
65	33	("[""1967-04-24 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
66	33	("[""1967-04-24 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2404670363	tilknyttedepersoner	\N
67	34	("[""1944-08-04 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
68	34	("[""1944-08-04 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:0408440130	tilknyttedepersoner	\N
69	35	("[""1951-06-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
70	35	("[""1951-06-28 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2806512543	tilknyttedepersoner	\N
71	36	("[""1947-02-18 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
72	36	("[""1947-02-18 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1802473954	tilknyttedepersoner	\N
73	37	("[""1972-08-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
74	37	("[""1972-08-11 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1108722947	tilknyttedepersoner	\N
75	38	("[""1940-02-26 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
76	38	("[""1940-02-26 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2602402331	tilknyttedepersoner	\N
77	39	("[""1945-05-22 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
78	39	("[""1945-05-22 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:2205452519	tilknyttedepersoner	\N
79	40	("[""1941-07-12 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
80	40	("[""1941-07-12 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:1207410213	tilknyttedepersoner	\N
81	41	("[""1948-01-17 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
82	41	("[""1948-01-17 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1701483517	tilknyttedepersoner	\N
83	42	("[""1944-02-14 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
84	42	("[""1944-02-14 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1402443533	tilknyttedepersoner	\N
85	43	("[""1981-01-26 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
86	43	("[""1981-01-26 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2601811572	tilknyttedepersoner	\N
87	44	("[""1948-06-19 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
88	44	("[""1948-06-19 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:1906481975	tilknyttedepersoner	\N
89	45	("[""1971-02-25 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
90	45	("[""1971-02-25 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:2502713968	tilknyttedepersoner	\N
91	46	("[""1980-08-06 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
92	46	("[""1980-08-06 00:00:00+02"",infinity)",,,"")	\N	urn:dk:cpr:person:0608800166	tilknyttedepersoner	\N
\.


--
-- Name: bruger_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.bruger_relation_id_seq', 92, true);


--
-- Data for Name: bruger_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.bruger_tils_gyldighed (id, virkning, gyldighed, bruger_registrering_id) FROM stdin;
1	("[""1954-01-03 00:00:00+01"",infinity)",,,"")	Aktiv	1
2	("[""1942-11-06 00:00:00+01"",infinity)",,,"")	Aktiv	2
3	("[""1947-12-28 00:00:00+01"",infinity)",,,"")	Aktiv	3
4	("[""1949-10-08 00:00:00+01"",infinity)",,,"")	Aktiv	4
5	("[""1985-01-25 00:00:00+01"",infinity)",,,"")	Aktiv	5
6	("[""1975-06-29 00:00:00+01"",infinity)",,,"")	Aktiv	6
7	("[""1943-11-06 00:00:00+01"",infinity)",,,"")	Aktiv	7
8	("[""1940-11-16 00:00:00+02"",infinity)",,,"")	Aktiv	8
9	("[""1953-11-28 00:00:00+01"",infinity)",,,"")	Aktiv	9
10	("[""1942-10-02 00:00:00+02"",infinity)",,,"")	Aktiv	10
11	("[""1945-03-04 00:00:00+01"",infinity)",,,"")	Aktiv	11
12	("[""1957-03-19 00:00:00+01"",infinity)",,,"")	Aktiv	12
13	("[""1947-02-11 00:00:00+01"",infinity)",,,"")	Aktiv	13
14	("[""1987-03-13 00:00:00+01"",infinity)",,,"")	Aktiv	14
15	("[""1994-01-21 00:00:00+01"",infinity)",,,"")	Aktiv	15
16	("[""1940-11-23 00:00:00+02"",infinity)",,,"")	Aktiv	16
17	("[""1957-05-27 00:00:00+01"",infinity)",,,"")	Aktiv	17
18	("[""1963-05-25 00:00:00+01"",infinity)",,,"")	Aktiv	18
19	("[""1952-01-05 00:00:00+01"",infinity)",,,"")	Aktiv	19
20	("[""1963-06-20 00:00:00+01"",infinity)",,,"")	Aktiv	20
21	("[""1946-12-31 00:00:00+01"",infinity)",,,"")	Aktiv	21
22	("[""1973-01-25 00:00:00+01"",infinity)",,,"")	Aktiv	22
23	("[""1968-07-04 00:00:00+01"",infinity)",,,"")	Aktiv	23
24	("[""1942-04-09 00:00:00+02"",infinity)",,,"")	Aktiv	24
25	("[""1943-08-22 00:00:00+02"",infinity)",,,"")	Aktiv	25
26	("[""1950-02-28 00:00:00+01"",infinity)",,,"")	Aktiv	26
27	("[""1940-03-28 00:00:00+01"",infinity)",,,"")	Aktiv	27
28	("[""1970-01-27 00:00:00+01"",infinity)",,,"")	Aktiv	28
29	("[""1940-08-15 00:00:00+02"",infinity)",,,"")	Aktiv	29
30	("[""1952-06-17 00:00:00+01"",infinity)",,,"")	Aktiv	30
31	("[""1968-02-13 00:00:00+01"",infinity)",,,"")	Aktiv	31
32	("[""1969-12-16 00:00:00+01"",infinity)",,,"")	Aktiv	32
33	("[""1967-04-24 00:00:00+01"",infinity)",,,"")	Aktiv	33
34	("[""1944-08-04 00:00:00+02"",infinity)",,,"")	Aktiv	34
35	("[""1951-06-28 00:00:00+01"",infinity)",,,"")	Aktiv	35
36	("[""1947-02-18 00:00:00+01"",infinity)",,,"")	Aktiv	36
37	("[""1972-08-11 00:00:00+01"",infinity)",,,"")	Aktiv	37
38	("[""1940-02-26 00:00:00+01"",infinity)",,,"")	Aktiv	38
39	("[""1945-05-22 00:00:00+02"",infinity)",,,"")	Aktiv	39
40	("[""1941-07-12 00:00:00+02"",infinity)",,,"")	Aktiv	40
41	("[""1948-01-17 00:00:00+01"",infinity)",,,"")	Aktiv	41
42	("[""1944-02-14 00:00:00+01"",infinity)",,,"")	Aktiv	42
43	("[""1981-01-26 00:00:00+01"",infinity)",,,"")	Aktiv	43
44	("[""1948-06-19 00:00:00+02"",infinity)",,,"")	Aktiv	44
45	("[""1971-02-25 00:00:00+01"",infinity)",,,"")	Aktiv	45
46	("[""1980-08-06 00:00:00+02"",infinity)",,,"")	Aktiv	46
\.


--
-- Name: bruger_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.bruger_tils_gyldighed_id_seq', 46, true);


--
-- Data for Name: dokument; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.dokument (id) FROM stdin;
\.


--
-- Data for Name: dokument_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.dokument_registrering (id, dokument_id, registrering) FROM stdin;
\.


--
-- Data for Name: dokument_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.dokument_attr_egenskaber (id, brugervendtnoegle, beskrivelse, brevdato, kassationskode, major, minor, offentlighedundtaget, titel, dokumenttype, integrationsdata, virkning, dokument_registrering_id) FROM stdin;
\.


--
-- Name: dokument_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.dokument_attr_egenskaber_id_seq', 1, false);


--
-- Data for Name: dokument_variant; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.dokument_variant (id, varianttekst, dokument_registrering_id) FROM stdin;
\.


--
-- Data for Name: dokument_del; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.dokument_del (id, deltekst, variant_id) FROM stdin;
\.


--
-- Data for Name: dokument_del_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.dokument_del_egenskaber (id, del_id, indeks, indhold, lokation, mimetype, virkning) FROM stdin;
\.


--
-- Name: dokument_del_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.dokument_del_egenskaber_id_seq', 1, false);


--
-- Name: dokument_del_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.dokument_del_id_seq', 1, false);


--
-- Data for Name: dokument_del_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.dokument_del_relation (id, del_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
\.


--
-- Name: dokument_del_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.dokument_del_relation_id_seq', 1, false);


--
-- Name: dokument_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.dokument_registrering_id_seq', 1, false);


--
-- Data for Name: dokument_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.dokument_relation (id, dokument_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
\.


--
-- Name: dokument_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.dokument_relation_id_seq', 1, false);


--
-- Data for Name: dokument_tils_fremdrift; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.dokument_tils_fremdrift (id, virkning, fremdrift, dokument_registrering_id) FROM stdin;
\.


--
-- Name: dokument_tils_fremdrift_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.dokument_tils_fremdrift_id_seq', 1, false);


--
-- Data for Name: dokument_variant_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.dokument_variant_egenskaber (id, variant_id, arkivering, delvisscannet, offentliggoerelse, produktion, virkning) FROM stdin;
\.


--
-- Name: dokument_variant_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.dokument_variant_egenskaber_id_seq', 1, false);


--
-- Name: dokument_variant_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.dokument_variant_id_seq', 1, false);


--
-- Data for Name: facet; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.facet (id) FROM stdin;
cea235bb-9ea2-4154-87b1-13d2dba2b538
fe958b8d-e6a0-45f6-b9f3-6be0982099d0
67110d1c-902a-4229-b1f0-3c4d7bd3a2f6
a6227db5-b2aa-4369-8632-6f8b6ea5f67f
5c5a0657-bb0c-44dc-9c9d-6c926342f23b
94aeb553-052d-448e-b542-9c8e25568d12
d9fddbef-64ac-4a27-a32a-439fb6442a3e
46956d32-8c32-43a1-bda7-63f276d5de0c
dfe30744-2c5b-4ef3-943e-e5a0841f45ba
af4f2585-22af-49a2-85f4-0c6642a8d341
fbd6beb5-8e48-4bad-85fc-633a5aedd1d7
2cd46025-4beb-4c5b-bed3-6f1a47da2426
914559f4-dadb-4ffb-89c2-d46f689f1d3a
ddb81cd2-87cd-4256-b99f-0a20312f2f67
e26cd940-6856-4d55-a4d4-ff924d8e4a7e
\.


--
-- Data for Name: facet_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.facet_registrering (id, facet_id, registrering) FROM stdin;
1	cea235bb-9ea2-4154-87b1-13d2dba2b538	("[""2019-03-18 17:51:11.384079+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
2	fe958b8d-e6a0-45f6-b9f3-6be0982099d0	("[""2019-03-18 17:51:11.407558+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
3	67110d1c-902a-4229-b1f0-3c4d7bd3a2f6	("[""2019-03-18 17:51:11.426992+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
4	a6227db5-b2aa-4369-8632-6f8b6ea5f67f	("[""2019-03-18 17:51:11.447697+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
5	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	("[""2019-03-18 17:51:11.465945+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
6	94aeb553-052d-448e-b542-9c8e25568d12	("[""2019-03-18 17:51:11.485315+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
7	d9fddbef-64ac-4a27-a32a-439fb6442a3e	("[""2019-03-18 17:51:11.504489+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
8	46956d32-8c32-43a1-bda7-63f276d5de0c	("[""2019-03-18 17:51:11.522751+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
9	dfe30744-2c5b-4ef3-943e-e5a0841f45ba	("[""2019-03-18 17:51:11.541021+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
10	af4f2585-22af-49a2-85f4-0c6642a8d341	("[""2019-03-18 17:51:11.559744+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
11	fbd6beb5-8e48-4bad-85fc-633a5aedd1d7	("[""2019-03-18 17:51:11.578748+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
12	2cd46025-4beb-4c5b-bed3-6f1a47da2426	("[""2019-03-18 17:51:11.597101+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
13	914559f4-dadb-4ffb-89c2-d46f689f1d3a	("[""2019-03-18 17:51:11.616403+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
14	ddb81cd2-87cd-4256-b99f-0a20312f2f67	("[""2019-03-18 17:51:11.634436+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
15	e26cd940-6856-4d55-a4d4-ff924d8e4a7e	("[""2019-03-18 17:51:11.652978+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
\.


--
-- Data for Name: facet_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.facet_attr_egenskaber (id, brugervendtnoegle, beskrivelse, opbygning, ophavsret, plan, supplement, retskilde, integrationsdata, virkning, facet_registrering_id) FROM stdin;
1	org_unit_address_type	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"org_unit_address_type\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	1
2	employee_address_type	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"employee_address_type\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	2
3	manager_address_type	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"manager_address_type\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3
4	address_property	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"address_property\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	4
5	engagement_job_function	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"engagement_job_function\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5
6	org_unit_type	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"org_unit_type\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	6
7	engagement_type	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"engagement_type\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	7
8	association_type	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"association_type\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	8
9	role_type	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"role_type\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	9
10	leave_type	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"leave_type\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	10
11	manager_type	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"manager_type\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	11
12	responsibility	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"responsibility\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	12
13	manager_level	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"manager_level\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	13
14	visibility	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"visibility\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	14
15	time_planning	\N	\N	\N	\N	\N	\N	{"Artificial import": "\\"time_planning\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	15
\.


--
-- Name: facet_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.facet_attr_egenskaber_id_seq', 15, true);


--
-- Name: facet_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.facet_registrering_id_seq', 15, true);


--
-- Data for Name: facet_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.facet_relation (id, facet_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
2	1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
3	2	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
4	2	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
5	3	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
6	3	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
7	4	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
8	4	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
9	5	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
10	5	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
11	6	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
12	6	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
13	7	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
14	7	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
15	8	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
16	8	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
17	9	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
18	9	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
19	10	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
20	10	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
21	11	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
22	11	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
23	12	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
24	12	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
25	13	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
26	13	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
27	14	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
28	14	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
29	15	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
30	15	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3ba4e044-4834-4913-9eaf-7247f094df58	\N	facettilhoerer	klassifikation
\.


--
-- Name: facet_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.facet_relation_id_seq', 30, true);


--
-- Data for Name: facet_tils_publiceret; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.facet_tils_publiceret (id, virkning, publiceret, facet_registrering_id) FROM stdin;
1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	1
2	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	2
3	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	3
4	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	4
5	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	5
6	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	6
7	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	7
8	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	8
9	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	9
10	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	10
11	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	11
12	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	12
13	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	13
14	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	14
15	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	15
\.


--
-- Name: facet_tils_publiceret_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.facet_tils_publiceret_id_seq', 15, true);


--
-- Data for Name: indsats; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.indsats (id) FROM stdin;
\.


--
-- Data for Name: indsats_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.indsats_registrering (id, indsats_id, registrering) FROM stdin;
\.


--
-- Data for Name: indsats_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.indsats_attr_egenskaber (id, brugervendtnoegle, beskrivelse, starttidspunkt, sluttidspunkt, integrationsdata, virkning, indsats_registrering_id) FROM stdin;
\.


--
-- Name: indsats_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.indsats_attr_egenskaber_id_seq', 1, false);


--
-- Name: indsats_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.indsats_registrering_id_seq', 1, false);


--
-- Data for Name: indsats_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.indsats_relation (id, indsats_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type, rel_index) FROM stdin;
\.


--
-- Name: indsats_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.indsats_relation_id_seq', 1, false);


--
-- Data for Name: indsats_tils_fremdrift; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.indsats_tils_fremdrift (id, virkning, fremdrift, indsats_registrering_id) FROM stdin;
\.


--
-- Name: indsats_tils_fremdrift_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.indsats_tils_fremdrift_id_seq', 1, false);


--
-- Data for Name: indsats_tils_publiceret; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.indsats_tils_publiceret (id, virkning, publiceret, indsats_registrering_id) FROM stdin;
\.


--
-- Name: indsats_tils_publiceret_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.indsats_tils_publiceret_id_seq', 1, false);


--
-- Data for Name: interessefaellesskab; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.interessefaellesskab (id) FROM stdin;
\.


--
-- Data for Name: interessefaellesskab_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.interessefaellesskab_registrering (id, interessefaellesskab_id, registrering) FROM stdin;
\.


--
-- Data for Name: interessefaellesskab_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.interessefaellesskab_attr_egenskaber (id, brugervendtnoegle, interessefaellesskabsnavn, interessefaellesskabstype, integrationsdata, virkning, interessefaellesskab_registrering_id) FROM stdin;
\.


--
-- Name: interessefaellesskab_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.interessefaellesskab_attr_egenskaber_id_seq', 1, false);


--
-- Name: interessefaellesskab_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.interessefaellesskab_registrering_id_seq', 1, false);


--
-- Data for Name: interessefaellesskab_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.interessefaellesskab_relation (id, interessefaellesskab_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
\.


--
-- Name: interessefaellesskab_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.interessefaellesskab_relation_id_seq', 1, false);


--
-- Data for Name: interessefaellesskab_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.interessefaellesskab_tils_gyldighed (id, virkning, gyldighed, interessefaellesskab_registrering_id) FROM stdin;
\.


--
-- Name: interessefaellesskab_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.interessefaellesskab_tils_gyldighed_id_seq', 1, false);


--
-- Data for Name: itsystem; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.itsystem (id) FROM stdin;
68746352-ef27-44e6-9bcc-30cbbaee4fb3
20b507cf-fdeb-4123-8da4-db4a15524398
ed1d88cd-89a8-4899-a26a-faf9393bcbb6
03120151-cd89-4fd6-9c1e-043803d90636
76015baa-c0e0-4fea-82c2-9941c68fa1cd
\.


--
-- Data for Name: itsystem_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.itsystem_registrering (id, itsystem_id, registrering) FROM stdin;
1	68746352-ef27-44e6-9bcc-30cbbaee4fb3	("[""2019-03-18 17:51:13.732392+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
2	20b507cf-fdeb-4123-8da4-db4a15524398	("[""2019-03-18 17:51:13.764411+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
3	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	("[""2019-03-18 17:51:13.788533+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
4	03120151-cd89-4fd6-9c1e-043803d90636	("[""2019-03-18 17:51:13.814377+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
5	76015baa-c0e0-4fea-82c2-9941c68fa1cd	("[""2019-03-18 17:51:13.837543+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
\.


--
-- Data for Name: itsystem_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.itsystem_attr_egenskaber (id, brugervendtnoegle, itsystemnavn, itsystemtype, konfigurationreference, integrationsdata, virkning, itsystem_registrering_id) FROM stdin;
1	Active Directory	Active Directory	\N	\N	{"Artificial import": "\\"Active Directory\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	1
2	SAP	SAP	\N	\N	{"Artificial import": "\\"SAP\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	2
3	Office365	Office365	\N	\N	{"Artificial import": "\\"Office365\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3
4	Plone	Plone	\N	\N	{"Artificial import": "\\"Plone\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	4
5	OpenDesk	OpenDesk	\N	\N	{"Artificial import": "\\"OpenDesk\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5
\.


--
-- Name: itsystem_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.itsystem_attr_egenskaber_id_seq', 5, true);


--
-- Name: itsystem_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.itsystem_registrering_id_seq', 5, true);


--
-- Data for Name: itsystem_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.itsystem_relation (id, itsystem_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
2	2	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
3	3	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
4	4	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
5	5	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
\.


--
-- Name: itsystem_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.itsystem_relation_id_seq', 5, true);


--
-- Data for Name: itsystem_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.itsystem_tils_gyldighed (id, virkning, gyldighed, itsystem_registrering_id) FROM stdin;
1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	1
2	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	2
3	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	3
4	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	4
5	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	5
\.


--
-- Name: itsystem_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.itsystem_tils_gyldighed_id_seq', 5, true);


--
-- Data for Name: klasse; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse (id) FROM stdin;
7bfbb207-85a3-40d8-97da-03ad7a92b2e2
0c7f0826-ec4a-4daf-b08e-d6b34f690cc9
4f5aad51-8c28-4c0d-9b17-a2a30df36849
86964252-7c92-4337-a59c-bd847865280b
f19417e6-1f70-442a-bfbf-2ad65397d84f
12f83ab4-fffd-4aac-8464-2830eacdb506
c10512c2-df7c-4e44-b83e-7cb0ea4c8379
166929d8-a994-4f73-b8f1-a6eae9f9889f
589dadde-f6a3-4ead-8dac-ba7252e5565c
ad5b6590-2db5-4dad-ad89-1027314cff16
8ef1618c-44aa-4226-b312-62411d9b57e7
d07ce76c-ed70-4b92-b419-84b948e17086
f66083c8-0fbb-4b15-adee-4ccf4b449b99
60a914dd-f35d-451e-b344-46d591558194
ddc55bb7-7f76-4ff2-9c12-abb385cf28c5
a825965e-da87-4317-a40b-80f8d33814cc
bc9f6541-1031-49ff-ab04-c1cad96a2871
b617b6e7-166f-4c30-8ead-aeb360febf0e
5b03a02c-a698-4c40-a530-d5578b142283
68ce5504-54ec-474f-8fed-2709442e0c9b
a47e0a34-cc21-4ea8-8d2b-5398b7884ac5
ecbe9c67-1b0a-4aba-8e50-67a92691fd61
893bc985-8872-4b5d-a68f-153c059d7e64
d4674f4d-0ee9-4bbc-b71d-97903afc3522
05c6f4e2-c628-4efc-b41c-65935977418a
06a6b95b-30a5-45d1-a180-389b9c4a6d0c
94c85f23-1983-4eec-a966-72e53d13a604
eea9ac5c-5df8-4ed6-be0d-40be3ad9701b
6d9a25e6-e942-4a3e-858b-ef3870742ce1
77c92a14-a82d-424b-8180-00e0c3f9019f
302a9818-452e-4aa7-8811-442f2b91486f
01f89ef8-0651-43c2-afda-e24f0d8fe05b
9f833d6c-3611-49fe-b155-71a7ba1602a2
91f65ddc-5eda-4b63-b7bc-506871c76181
861a977e-3490-4d73-b005-587af2532e1d
ea13a75a-2b7f-4b89-9ab4-dd7be5fcbd1e
8020a7b0-eae6-4ca8-8abe-1005d72abd88
b9f246ab-027e-4788-a152-290bc00afc2c
89418149-1ce2-41ca-bbb9-b8e0eb65a67c
594a2c7d-3880-4ef6-a0c0-f961f397293a
c76c6312-b44f-4b3c-8293-d5e92a612dda
41f70330-b724-47c1-b491-33a8a614a409
3d97a689-63af-4372-bbf4-91c5a3dd1952
80ee959a-00f2-484c-830f-c9e761b9026d
5c074e78-724f-45af-9b78-8daddad60d57
9b447ec7-81fb-46c8-8820-3447b8a93330
eb911cea-f1f1-4002-b584-f812022ebe39
78c57d61-9f08-46a8-89af-7ad3289326da
1da01235-4b00-4509-b408-34e858434dd6
1a2c92e2-44d4-4862-830c-c1a194578365
263f43f0-6863-4ad6-a125-15e929dc3475
9270ff78-e2f7-4b47-a229-7a6963469566
7c9b618a-17ae-47c6-8ec0-bdbf0ff16443
413a8b3b-1a55-4e28-a877-5088c68209ee
c6f516ed-57e7-4273-a4d3-67e21720ecd9
4cf55c21-406d-477f-8d9d-087f253c8709
75f24b4e-9dba-4d49-b1cf-7e8c358282ef
7104e05a-7566-43ac-a391-40291d1b4d8b
49f1996b-8ea1-4c91-93f8-f3bcc0068e5c
a506d035-7c4b-4dfa-92d7-1dd1eb9c36be
4f24c7f0-818d-415a-a5e2-6d1212bf2676
714972ef-addf-43d3-8dd9-f81cad5316a3
1a6c9e1a-0d2f-47c9-92ac-3779c77a7276
e206bbc4-812d-41ed-83f1-e64281be0d46
0f166acf-c117-405e-9e6d-b76d34250c9d
32c52c48-8110-4398-8f09-39758bff8eaa
4cb8e8a9-a495-4f01-b0df-141f67578614
9c71590e-d81b-460c-a2fe-b6ab69e4d604
cd4774a0-b0a5-47ed-962a-945b97ff26ad
d4f8fc78-6ada-444b-9ea1-9fd671f266b9
598c94ca-d6fa-40e6-88bb-69075397fd9a
781f2bb8-d165-4747-ab21-dd3dc613e5da
ed2d778b-afd7-4d68-8c75-ff6e86d6586e
0e09420f-ca1c-4422-a07b-8f1da2ed78a5
27e20f86-5c66-42c5-a4fb-36df770d3106
140039c6-8583-453d-b5be-77dd078a0c67
91db8130-12d7-4ff5-922d-14c6d7efffb7
61052dc4-1c62-428b-a703-7cd6f2876dba
706ae3a8-1976-4a1d-94c1-ab9b760bb635
fffdfd16-d429-4e4c-98f4-d6c0826262a3
5607fe9e-c152-4ad9-b0c2-0472fef9da2d
34dfe265-4f4d-477c-bd8c-068353085c0e
\.


--
-- Data for Name: klasse_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse_registrering (id, klasse_id, registrering) FROM stdin;
1	7bfbb207-85a3-40d8-97da-03ad7a92b2e2	("[""2019-03-18 17:51:11.681698+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
2	0c7f0826-ec4a-4daf-b08e-d6b34f690cc9	("[""2019-03-18 17:51:11.707942+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
3	4f5aad51-8c28-4c0d-9b17-a2a30df36849	("[""2019-03-18 17:51:11.729407+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
4	86964252-7c92-4337-a59c-bd847865280b	("[""2019-03-18 17:51:11.751378+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
5	f19417e6-1f70-442a-bfbf-2ad65397d84f	("[""2019-03-18 17:51:11.77325+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
6	12f83ab4-fffd-4aac-8464-2830eacdb506	("[""2019-03-18 17:51:11.795652+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
7	c10512c2-df7c-4e44-b83e-7cb0ea4c8379	("[""2019-03-18 17:51:11.818371+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
8	166929d8-a994-4f73-b8f1-a6eae9f9889f	("[""2019-03-18 17:51:11.840879+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
9	589dadde-f6a3-4ead-8dac-ba7252e5565c	("[""2019-03-18 17:51:11.866895+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
10	ad5b6590-2db5-4dad-ad89-1027314cff16	("[""2019-03-18 17:51:11.889412+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
11	8ef1618c-44aa-4226-b312-62411d9b57e7	("[""2019-03-18 17:51:11.91601+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
12	d07ce76c-ed70-4b92-b419-84b948e17086	("[""2019-03-18 17:51:11.937426+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
13	f66083c8-0fbb-4b15-adee-4ccf4b449b99	("[""2019-03-18 17:51:11.962724+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
14	60a914dd-f35d-451e-b344-46d591558194	("[""2019-03-18 17:51:11.983221+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
15	ddc55bb7-7f76-4ff2-9c12-abb385cf28c5	("[""2019-03-18 17:51:12.009706+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
16	a825965e-da87-4317-a40b-80f8d33814cc	("[""2019-03-18 17:51:12.029563+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
17	bc9f6541-1031-49ff-ab04-c1cad96a2871	("[""2019-03-18 17:51:12.056127+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
18	b617b6e7-166f-4c30-8ead-aeb360febf0e	("[""2019-03-18 17:51:12.077011+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
19	5b03a02c-a698-4c40-a530-d5578b142283	("[""2019-03-18 17:51:12.105518+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
20	68ce5504-54ec-474f-8fed-2709442e0c9b	("[""2019-03-18 17:51:12.125847+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
21	a47e0a34-cc21-4ea8-8d2b-5398b7884ac5	("[""2019-03-18 17:51:12.152264+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
22	ecbe9c67-1b0a-4aba-8e50-67a92691fd61	("[""2019-03-18 17:51:12.175164+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
23	893bc985-8872-4b5d-a68f-153c059d7e64	("[""2019-03-18 17:51:12.202739+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
24	d4674f4d-0ee9-4bbc-b71d-97903afc3522	("[""2019-03-18 17:51:12.225103+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
25	05c6f4e2-c628-4efc-b41c-65935977418a	("[""2019-03-18 17:51:12.250298+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
26	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	("[""2019-03-18 17:51:12.27276+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
27	94c85f23-1983-4eec-a966-72e53d13a604	("[""2019-03-18 17:51:12.297019+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
28	eea9ac5c-5df8-4ed6-be0d-40be3ad9701b	("[""2019-03-18 17:51:12.319893+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
29	6d9a25e6-e942-4a3e-858b-ef3870742ce1	("[""2019-03-18 17:51:12.341695+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
30	77c92a14-a82d-424b-8180-00e0c3f9019f	("[""2019-03-18 17:51:12.366838+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
31	302a9818-452e-4aa7-8811-442f2b91486f	("[""2019-03-18 17:51:12.389453+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
32	01f89ef8-0651-43c2-afda-e24f0d8fe05b	("[""2019-03-18 17:51:12.415108+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
33	9f833d6c-3611-49fe-b155-71a7ba1602a2	("[""2019-03-18 17:51:12.436885+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
34	91f65ddc-5eda-4b63-b7bc-506871c76181	("[""2019-03-18 17:51:12.463117+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
35	861a977e-3490-4d73-b005-587af2532e1d	("[""2019-03-18 17:51:12.48358+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
36	ea13a75a-2b7f-4b89-9ab4-dd7be5fcbd1e	("[""2019-03-18 17:51:12.511139+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
37	8020a7b0-eae6-4ca8-8abe-1005d72abd88	("[""2019-03-18 17:51:12.531801+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
38	b9f246ab-027e-4788-a152-290bc00afc2c	("[""2019-03-18 17:51:12.557148+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
39	89418149-1ce2-41ca-bbb9-b8e0eb65a67c	("[""2019-03-18 17:51:12.578486+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
40	594a2c7d-3880-4ef6-a0c0-f961f397293a	("[""2019-03-18 17:51:12.606223+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
41	c76c6312-b44f-4b3c-8293-d5e92a612dda	("[""2019-03-18 17:51:12.627617+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
42	41f70330-b724-47c1-b491-33a8a614a409	("[""2019-03-18 17:51:12.655778+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
43	3d97a689-63af-4372-bbf4-91c5a3dd1952	("[""2019-03-18 17:51:12.676885+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
44	80ee959a-00f2-484c-830f-c9e761b9026d	("[""2019-03-18 17:51:12.702145+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
45	5c074e78-724f-45af-9b78-8daddad60d57	("[""2019-03-18 17:51:12.724197+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
46	9b447ec7-81fb-46c8-8820-3447b8a93330	("[""2019-03-18 17:51:12.750773+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
47	eb911cea-f1f1-4002-b584-f812022ebe39	("[""2019-03-18 17:51:12.773196+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
48	78c57d61-9f08-46a8-89af-7ad3289326da	("[""2019-03-18 17:51:12.802655+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
49	1da01235-4b00-4509-b408-34e858434dd6	("[""2019-03-18 17:51:12.824131+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
50	1a2c92e2-44d4-4862-830c-c1a194578365	("[""2019-03-18 17:51:12.85249+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
51	263f43f0-6863-4ad6-a125-15e929dc3475	("[""2019-03-18 17:51:12.876394+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
52	9270ff78-e2f7-4b47-a229-7a6963469566	("[""2019-03-18 17:51:12.904813+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
53	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	("[""2019-03-18 17:51:12.925331+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
54	413a8b3b-1a55-4e28-a877-5088c68209ee	("[""2019-03-18 17:51:12.954953+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
55	c6f516ed-57e7-4273-a4d3-67e21720ecd9	("[""2019-03-18 17:51:12.97453+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
56	4cf55c21-406d-477f-8d9d-087f253c8709	("[""2019-03-18 17:51:13.001123+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
57	75f24b4e-9dba-4d49-b1cf-7e8c358282ef	("[""2019-03-18 17:51:13.022214+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
58	7104e05a-7566-43ac-a391-40291d1b4d8b	("[""2019-03-18 17:51:13.0508+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
59	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	("[""2019-03-18 17:51:13.071253+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
60	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	("[""2019-03-18 17:51:13.101393+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
61	4f24c7f0-818d-415a-a5e2-6d1212bf2676	("[""2019-03-18 17:51:13.123648+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
62	714972ef-addf-43d3-8dd9-f81cad5316a3	("[""2019-03-18 17:51:13.154357+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
63	1a6c9e1a-0d2f-47c9-92ac-3779c77a7276	("[""2019-03-18 17:51:13.177738+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
64	e206bbc4-812d-41ed-83f1-e64281be0d46	("[""2019-03-18 17:51:13.217008+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
65	0f166acf-c117-405e-9e6d-b76d34250c9d	("[""2019-03-18 17:51:13.240684+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
66	32c52c48-8110-4398-8f09-39758bff8eaa	("[""2019-03-18 17:51:13.269262+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
67	4cb8e8a9-a495-4f01-b0df-141f67578614	("[""2019-03-18 17:51:13.296751+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
68	9c71590e-d81b-460c-a2fe-b6ab69e4d604	("[""2019-03-18 17:51:13.324599+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
69	cd4774a0-b0a5-47ed-962a-945b97ff26ad	("[""2019-03-18 17:51:13.355475+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
70	d4f8fc78-6ada-444b-9ea1-9fd671f266b9	("[""2019-03-18 17:51:13.381993+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
71	598c94ca-d6fa-40e6-88bb-69075397fd9a	("[""2019-03-18 17:51:13.414661+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
72	781f2bb8-d165-4747-ab21-dd3dc613e5da	("[""2019-03-18 17:51:13.458214+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
73	ed2d778b-afd7-4d68-8c75-ff6e86d6586e	("[""2019-03-18 17:51:13.48002+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
74	0e09420f-ca1c-4422-a07b-8f1da2ed78a5	("[""2019-03-18 17:51:13.507358+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
75	27e20f86-5c66-42c5-a4fb-36df770d3106	("[""2019-03-18 17:51:13.52867+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
76	140039c6-8583-453d-b5be-77dd078a0c67	("[""2019-03-18 17:51:13.556517+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
77	91db8130-12d7-4ff5-922d-14c6d7efffb7	("[""2019-03-18 17:51:13.576772+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
78	61052dc4-1c62-428b-a703-7cd6f2876dba	("[""2019-03-18 17:51:13.605427+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
79	706ae3a8-1976-4a1d-94c1-ab9b760bb635	("[""2019-03-18 17:51:13.626396+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
80	fffdfd16-d429-4e4c-98f4-d6c0826262a3	("[""2019-03-18 17:51:13.654896+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
81	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	("[""2019-03-18 17:51:13.676518+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
82	34dfe265-4f4d-477c-bd8c-068353085c0e	("[""2019-03-18 17:51:13.704762+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
\.


--
-- Data for Name: klasse_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse_attr_egenskaber (id, brugervendtnoegle, beskrivelse, eksempel, omfang, titel, retskilde, aendringsnotat, integrationsdata, virkning, klasse_registrering_id) FROM stdin;
1	Udvikler	\N	\N	TEXT	Udvikler	\N	\N	{"Artificial import": "\\"Udvikler\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	1
2	Specialkonsulent	\N	\N	TEXT	Specialkonsulent	\N	\N	{"Artificial import": "\\"Specialkonsulent\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	2
3	Ergoterapeut	\N	\N	TEXT	Ergoterapeut	\N	\N	{"Artificial import": "\\"Ergoterapeut\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	3
4	Udviklingskonsulent	\N	\N	TEXT	Udviklingskonsulent	\N	\N	{"Artificial import": "\\"Udviklingskonsulent\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	4
5	Specialist	\N	\N	TEXT	Specialist	\N	\N	{"Artificial import": "\\"Specialist\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5
6	Jurist	\N	\N	TEXT	Jurist	\N	\N	{"Artificial import": "\\"Jurist\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	6
7	Personalekonsulent	\N	\N	TEXT	Personalekonsulent	\N	\N	{"Artificial import": "\\"Personalekonsulent\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	7
8	Lønkonsulent	\N	\N	TEXT	Lønkonsulent	\N	\N	{"Artificial import": "\\"L\\\\u00f8nkonsulent\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	8
9	Kontorelev	\N	\N	TEXT	Kontorelev	\N	\N	{"Artificial import": "\\"Kontorelev\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	9
10	Ressourcepædagog	\N	\N	TEXT	Ressourcepædagog	\N	\N	{"Artificial import": "\\"Ressourcep\\\\u00e6dagog\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	10
11	Pædagoisk vejleder	\N	\N	TEXT	Pædagoisk vejleder	\N	\N	{"Artificial import": "\\"P\\\\u00e6dagoisk vejleder\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	11
12	Skolepsykolog	\N	\N	TEXT	Skolepsykolog	\N	\N	{"Artificial import": "\\"Skolepsykolog\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	12
13	Støttepædagog	\N	\N	TEXT	Støttepædagog	\N	\N	{"Artificial import": "\\"St\\\\u00f8ttep\\\\u00e6dagog\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	13
14	Bogopsætter	\N	\N	TEXT	Bogopsætter	\N	\N	{"Artificial import": "\\"Bogops\\\\u00e6tter\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	14
15	Timelønnet lærer	\N	\N	TEXT	Timelønnet lærer	\N	\N	{"Artificial import": "\\"Timel\\\\u00f8nnet l\\\\u00e6rer\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	15
16	Pædagogmedhjælper	\N	\N	TEXT	Pædagogmedhjælper	\N	\N	{"Artificial import": "\\"P\\\\u00e6dagogmedhj\\\\u00e6lper\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	16
17	Teknisk Servicemedarb.	\N	\N	TEXT	Teknisk Servicemedarb.	\N	\N	{"Artificial import": "\\"Teknisk Servicemedarb.\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	17
18	Lærer/Overlærer	\N	\N	TEXT	Lærer/Overlærer	\N	\N	{"Artificial import": "\\"L\\\\u00e6rer/Overl\\\\u00e6rer\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	18
19	Formand	\N	\N	TEXT	Formand	\N	\N	{"Artificial import": "\\"Formand\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	19
20	Leder	\N	\N	TEXT	Leder	\N	\N	{"Artificial import": "\\"Leder\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	20
21	Medarbejder	\N	\N	TEXT	Medarbejder	\N	\N	{"Artificial import": "\\"Medarbejder\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	21
22	Næstformand	\N	\N	TEXT	Næstformand	\N	\N	{"Artificial import": "\\"N\\\\u00e6stformand\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	22
23	Projektleder	\N	\N	TEXT	Projektleder	\N	\N	{"Artificial import": "\\"Projektleder\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	23
24	Projektgruppemedlem	\N	\N	TEXT	Projektgruppemedlem	\N	\N	{"Artificial import": "\\"Projektgruppemedlem\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	24
25	Teammedarbejder	\N	\N	TEXT	Teammedarbejder	\N	\N	{"Artificial import": "\\"Teammedarbejder\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	25
26	Afdeling	\N	\N	TEXT	Afdeling	\N	\N	{"Artificial import": "\\"Afdeling\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	26
27	Institutionsafsnit	\N	\N	TEXT	Institutionsafsnit	\N	\N	{"Artificial import": "\\"Institutionsafsnit\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	27
28	Institution	\N	\N	TEXT	Institution	\N	\N	{"Artificial import": "\\"Institution\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	28
29	Fagligt center	\N	\N	TEXT	Fagligt center	\N	\N	{"Artificial import": "\\"Fagligt center\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	29
30	Direktørområde	\N	\N	TEXT	Direktørområde	\N	\N	{"Artificial import": "\\"Direkt\\\\u00f8romr\\\\u00e5de\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	30
31	Personale: ansættelse/afskedigelse	\N	\N	TEXT	Personale: ansættelse/afskedigelse	\N	\N	{"Artificial import": "\\"Personale: ans\\\\u00e6ttelse/afskedigelse\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	31
32	Beredskabsledelse	\N	\N	TEXT	Beredskabsledelse	\N	\N	{"Artificial import": "\\"Beredskabsledelse\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	32
33	Personale: øvrige administrative opgaver	\N	\N	TEXT	Personale: øvrige administrative opgaver	\N	\N	{"Artificial import": "\\"Personale: \\\\u00f8vrige administrative opgaver\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	33
34	Personale: Sygefravær	\N	\N	TEXT	Personale: Sygefravær	\N	\N	{"Artificial import": "\\"Personale: Sygefrav\\\\u00e6r\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	34
35	Ansvar for bygninger og arealer	\N	\N	TEXT	Ansvar for bygninger og arealer	\N	\N	{"Artificial import": "\\"Ansvar for bygninger og arealer\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	35
36	Personale: MUS-kompetence	\N	\N	TEXT	Personale: MUS-kompetence	\N	\N	{"Artificial import": "\\"Personale: MUS-kompetence\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	36
37	Direktør	\N	\N	TEXT	Direktør	\N	\N	{"Artificial import": "\\"Direkt\\\\u00f8r\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	37
38	Distriktsleder	\N	\N	TEXT	Distriktsleder	\N	\N	{"Artificial import": "\\"Distriktsleder\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	38
39	Beredskabschef	\N	\N	TEXT	Beredskabschef	\N	\N	{"Artificial import": "\\"Beredskabschef\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	39
40	Sekretariatschef	\N	\N	TEXT	Sekretariatschef	\N	\N	{"Artificial import": "\\"Sekretariatschef\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	40
41	Systemadministrator	\N	\N	TEXT	Systemadministrator	\N	\N	{"Artificial import": "\\"Systemadministrator\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	41
42	Områdeleder	\N	\N	TEXT	Områdeleder	\N	\N	{"Artificial import": "\\"Omr\\\\u00e5deleder\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	42
43	Centerchef	\N	\N	TEXT	Centerchef	\N	\N	{"Artificial import": "\\"Centerchef\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	43
44	Institutionsleder	\N	\N	TEXT	Institutionsleder	\N	\N	{"Artificial import": "\\"Institutionsleder\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	44
45	Tillidsrepræsentant	\N	\N	TEXT	Tillidsrepræsentant	\N	\N	{"Artificial import": "\\"Tillidsrepr\\\\u00e6sentant\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	45
46	Ergonomiambasadør	\N	\N	TEXT	Ergonomiambasadør	\N	\N	{"Artificial import": "\\"Ergonomiambasad\\\\u00f8r\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	46
47	Ansvarlig for sommerfest	\N	\N	TEXT	Ansvarlig for sommerfest	\N	\N	{"Artificial import": "\\"Ansvarlig for sommerfest\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	47
48	Barselsorlov	\N	\N	TEXT	Barselsorlov	\N	\N	{"Artificial import": "\\"Barselsorlov\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	48
49	Forældreorlov	\N	\N	TEXT	Forældreorlov	\N	\N	{"Artificial import": "\\"For\\\\u00e6ldreorlov\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	49
50	Orlov til pasning af syg pårørende	\N	\N	TEXT	Orlov til pasning af syg pårørende	\N	\N	{"Artificial import": "\\"Orlov til pasning af syg p\\\\u00e5r\\\\u00f8rende\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	50
51	AdressePostEmployee	\N	\N	DAR	Postadresse	\N	\N	{"Artificial import": "\\"AdressePostEmployee\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	51
52	PhoneEmployee	\N	\N	PHONE	Telefon	\N	\N	{"Artificial import": "\\"PhoneEmployee\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	52
53	LocationEmployee	\N	\N	TEXT	Lokation	\N	\N	{"Artificial import": "\\"LocationEmployee\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	53
54	EmailEmployee	\N	\N	EMAIL	Email	\N	\N	{"Artificial import": "\\"EmailEmployee\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	54
55	EmailManager	\N	\N	EMAIL	Email	\N	\N	{"Artificial import": "\\"EmailManager\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	55
56	TelefonManager	\N	\N	PHONE	Telefon	\N	\N	{"Artificial import": "\\"TelefonManager\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	56
57	AdressePostManager	\N	\N	DAR	Adresse	\N	\N	{"Artificial import": "\\"AdressePostManager\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	57
58	WebManager	\N	\N	TEXT	Webadresse	\N	\N	{"Artificial import": "\\"WebManager\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	58
59	AddressMailUnit	\N	\N	DAR	Postadresse	\N	\N	{"Artificial import": "\\"AddressMailUnit\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	59
60	AdressePostRetur	\N	\N	DAR	Returadresse	\N	\N	{"Artificial import": "\\"AdressePostRetur\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	60
61	AdresseHenvendelsessted	\N	\N	DAR	Henvendelsessted	\N	\N	{"Artificial import": "\\"AdresseHenvendelsessted\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	61
62	LocationUnit	\N	\N	TEXT	Lokation	\N	\N	{"Artificial import": "\\"LocationUnit\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	62
63	Skolekode	\N	\N	TEXT	Skolekode	\N	\N	{"Artificial import": "\\"Skolekode\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	63
64	Formålskode	\N	\N	TEXT	Formålskode	\N	\N	{"Artificial import": "\\"Form\\\\u00e5lskode\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	64
65	Afdelingskode	\N	\N	TEXT	Afdelingskode	\N	\N	{"Artificial import": "\\"Afdelingskode\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	65
66	EmailUnit	\N	\N	EMAIL	Email	\N	\N	{"Artificial import": "\\"EmailUnit\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	66
67	PhoneUnit	\N	\N	PHONE	Telefon	\N	\N	{"Artificial import": "\\"PhoneUnit\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	67
68	FaxUnit	\N	\N	PHONE	Fax	\N	\N	{"Artificial import": "\\"FaxUnit\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	68
69	EAN	\N	\N	EAN	EAN-nummer	\N	\N	{"Artificial import": "\\"EAN\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	69
70	WebUnit	\N	\N	WWW	Webadresse	\N	\N	{"Artificial import": "\\"WebUnit\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	70
71	p-nummer	\N	\N	PNUMBER	P-nummer	\N	\N	{"Artificial import": "\\"p-nummer\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	71
72	Niveau 1	\N	\N	TEXT	Niveau 1	\N	\N	{"Artificial import": "\\"Niveau 1\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	72
73	Niveau 2	\N	\N	TEXT	Niveau 2	\N	\N	{"Artificial import": "\\"Niveau 2\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	73
74	Niveau 3	\N	\N	TEXT	Niveau 3	\N	\N	{"Artificial import": "\\"Niveau 3\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	74
75	Niveau 4	\N	\N	TEXT	Niveau 4	\N	\N	{"Artificial import": "\\"Niveau 4\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	75
76	Arbejdstidsplaner	\N	\N	TEXT	Arbejdstidsplaner	\N	\N	{"Artificial import": "\\"Arbejdstidsplaner\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	76
77	Dannes ikke	\N	\N	TEXT	Dannes ikke	\N	\N	{"Artificial import": "\\"Dannes ikke\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	77
78	Tjenestetid	\N	\N	TEXT	Tjenestetid	\N	\N	{"Artificial import": "\\"Tjenestetid\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	78
79	Ansat	\N	\N	TEXT	Ansat	\N	\N	{"Artificial import": "\\"Ansat\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	79
80	Ekstern	\N	\N	PUBLIC	Må vises eksternt	\N	\N	{"Artificial import": "\\"Ekstern\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	80
81	Intern	\N	\N	INTERNAL	Må vises internt	\N	\N	{"Artificial import": "\\"Intern\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	81
82	Hemmelig	\N	\N	SECRET	Hemmelig	\N	\N	{"Artificial import": "\\"Hemmelig\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	82
\.


--
-- Name: klasse_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klasse_attr_egenskaber_id_seq', 82, true);


--
-- Data for Name: klasse_attr_egenskaber_soegeord; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse_attr_egenskaber_soegeord (id, soegeordidentifikator, beskrivelse, soegeordskategori, klasse_attr_egenskaber_id) FROM stdin;
\.


--
-- Name: klasse_attr_egenskaber_soegeord_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klasse_attr_egenskaber_soegeord_id_seq', 1, false);


--
-- Name: klasse_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klasse_registrering_id_seq', 82, true);


--
-- Data for Name: klasse_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse_relation (id, klasse_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
2	1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
3	2	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
4	2	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
5	3	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
6	3	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
7	4	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
8	4	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
9	5	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
10	5	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
11	6	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
12	6	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
13	7	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
14	7	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
15	8	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
16	8	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
17	9	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
18	9	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
19	10	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
20	10	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
21	11	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
22	11	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
23	12	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
24	12	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
25	13	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
26	13	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
27	14	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
28	14	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
29	15	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
30	15	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
31	16	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
32	16	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
33	17	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
34	17	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
35	18	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
36	18	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	5c5a0657-bb0c-44dc-9c9d-6c926342f23b	\N	facet	facet
37	19	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
38	19	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	46956d32-8c32-43a1-bda7-63f276d5de0c	\N	facet	facet
39	20	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
40	20	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	46956d32-8c32-43a1-bda7-63f276d5de0c	\N	facet	facet
41	21	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
42	21	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	46956d32-8c32-43a1-bda7-63f276d5de0c	\N	facet	facet
43	22	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
44	22	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	46956d32-8c32-43a1-bda7-63f276d5de0c	\N	facet	facet
45	23	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
46	23	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	46956d32-8c32-43a1-bda7-63f276d5de0c	\N	facet	facet
47	24	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
48	24	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	46956d32-8c32-43a1-bda7-63f276d5de0c	\N	facet	facet
49	25	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
50	25	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	46956d32-8c32-43a1-bda7-63f276d5de0c	\N	facet	facet
51	26	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
52	26	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	94aeb553-052d-448e-b542-9c8e25568d12	\N	facet	facet
53	27	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
54	27	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	94aeb553-052d-448e-b542-9c8e25568d12	\N	facet	facet
55	28	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
56	28	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	94aeb553-052d-448e-b542-9c8e25568d12	\N	facet	facet
57	29	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
58	29	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	94aeb553-052d-448e-b542-9c8e25568d12	\N	facet	facet
59	30	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
60	30	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	94aeb553-052d-448e-b542-9c8e25568d12	\N	facet	facet
61	31	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
62	31	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	2cd46025-4beb-4c5b-bed3-6f1a47da2426	\N	facet	facet
63	32	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
64	32	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	2cd46025-4beb-4c5b-bed3-6f1a47da2426	\N	facet	facet
65	33	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
66	33	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	2cd46025-4beb-4c5b-bed3-6f1a47da2426	\N	facet	facet
67	34	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
68	34	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	2cd46025-4beb-4c5b-bed3-6f1a47da2426	\N	facet	facet
69	35	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
70	35	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	2cd46025-4beb-4c5b-bed3-6f1a47da2426	\N	facet	facet
71	36	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
72	36	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	2cd46025-4beb-4c5b-bed3-6f1a47da2426	\N	facet	facet
73	37	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
74	37	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fbd6beb5-8e48-4bad-85fc-633a5aedd1d7	\N	facet	facet
75	38	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
76	38	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fbd6beb5-8e48-4bad-85fc-633a5aedd1d7	\N	facet	facet
77	39	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
78	39	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fbd6beb5-8e48-4bad-85fc-633a5aedd1d7	\N	facet	facet
79	40	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
80	40	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fbd6beb5-8e48-4bad-85fc-633a5aedd1d7	\N	facet	facet
81	41	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
82	41	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fbd6beb5-8e48-4bad-85fc-633a5aedd1d7	\N	facet	facet
83	42	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
84	42	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fbd6beb5-8e48-4bad-85fc-633a5aedd1d7	\N	facet	facet
85	43	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
86	43	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fbd6beb5-8e48-4bad-85fc-633a5aedd1d7	\N	facet	facet
87	44	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
88	44	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fbd6beb5-8e48-4bad-85fc-633a5aedd1d7	\N	facet	facet
89	45	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
90	45	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	dfe30744-2c5b-4ef3-943e-e5a0841f45ba	\N	facet	facet
91	46	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
92	46	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	dfe30744-2c5b-4ef3-943e-e5a0841f45ba	\N	facet	facet
93	47	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
94	47	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	dfe30744-2c5b-4ef3-943e-e5a0841f45ba	\N	facet	facet
95	48	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
96	48	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	af4f2585-22af-49a2-85f4-0c6642a8d341	\N	facet	facet
97	49	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
98	49	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	af4f2585-22af-49a2-85f4-0c6642a8d341	\N	facet	facet
99	50	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
100	50	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	af4f2585-22af-49a2-85f4-0c6642a8d341	\N	facet	facet
101	51	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
102	51	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fe958b8d-e6a0-45f6-b9f3-6be0982099d0	\N	facet	facet
103	52	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
104	52	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fe958b8d-e6a0-45f6-b9f3-6be0982099d0	\N	facet	facet
105	53	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
106	53	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fe958b8d-e6a0-45f6-b9f3-6be0982099d0	\N	facet	facet
107	54	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
108	54	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	fe958b8d-e6a0-45f6-b9f3-6be0982099d0	\N	facet	facet
109	55	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
110	55	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	67110d1c-902a-4229-b1f0-3c4d7bd3a2f6	\N	facet	facet
111	56	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
112	56	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	67110d1c-902a-4229-b1f0-3c4d7bd3a2f6	\N	facet	facet
113	57	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
114	57	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	67110d1c-902a-4229-b1f0-3c4d7bd3a2f6	\N	facet	facet
115	58	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
116	58	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	67110d1c-902a-4229-b1f0-3c4d7bd3a2f6	\N	facet	facet
117	59	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
118	59	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
119	60	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
120	60	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
121	61	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
122	61	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
123	62	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
124	62	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
125	63	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
126	63	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
127	64	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
128	64	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
129	65	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
130	65	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
131	66	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
132	66	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
133	67	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
134	67	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
135	68	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
136	68	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
137	69	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
138	69	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
139	70	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
140	70	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
141	71	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
142	71	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	cea235bb-9ea2-4154-87b1-13d2dba2b538	\N	facet	facet
143	72	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
144	72	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	914559f4-dadb-4ffb-89c2-d46f689f1d3a	\N	facet	facet
145	73	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
146	73	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	914559f4-dadb-4ffb-89c2-d46f689f1d3a	\N	facet	facet
147	74	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
148	74	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	914559f4-dadb-4ffb-89c2-d46f689f1d3a	\N	facet	facet
149	75	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
150	75	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	914559f4-dadb-4ffb-89c2-d46f689f1d3a	\N	facet	facet
151	76	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
152	76	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e26cd940-6856-4d55-a4d4-ff924d8e4a7e	\N	facet	facet
153	77	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
154	77	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e26cd940-6856-4d55-a4d4-ff924d8e4a7e	\N	facet	facet
155	78	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
156	78	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e26cd940-6856-4d55-a4d4-ff924d8e4a7e	\N	facet	facet
157	79	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
158	79	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	d9fddbef-64ac-4a27-a32a-439fb6442a3e	\N	facet	facet
159	80	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
160	80	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	ddb81cd2-87cd-4256-b99f-0a20312f2f67	\N	facet	facet
161	81	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
162	81	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	ddb81cd2-87cd-4256-b99f-0a20312f2f67	\N	facet	facet
163	82	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
164	82	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	ddb81cd2-87cd-4256-b99f-0a20312f2f67	\N	facet	facet
\.


--
-- Name: klasse_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klasse_relation_id_seq', 164, true);


--
-- Data for Name: klasse_tils_publiceret; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse_tils_publiceret (id, virkning, publiceret, klasse_registrering_id) FROM stdin;
1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	1
2	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	2
3	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	3
4	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	4
5	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	5
6	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	6
7	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	7
8	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	8
9	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	9
10	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	10
11	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	11
12	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	12
13	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	13
14	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	14
15	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	15
16	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	16
17	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	17
18	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	18
19	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	19
20	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	20
21	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	21
22	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	22
23	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	23
24	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	24
25	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	25
26	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	26
27	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	27
28	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	28
29	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	29
30	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	30
31	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	31
32	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	32
33	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	33
34	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	34
35	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	35
36	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	36
37	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	37
38	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	38
39	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	39
40	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	40
41	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	41
42	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	42
43	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	43
44	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	44
45	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	45
46	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	46
47	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	47
48	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	48
49	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	49
50	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	50
51	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	51
52	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	52
53	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	53
54	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	54
55	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	55
56	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	56
57	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	57
58	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	58
59	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	59
60	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	60
61	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	61
62	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	62
63	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	63
64	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	64
65	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	65
66	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	66
67	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	67
68	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	68
69	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	69
70	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	70
71	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	71
72	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	72
73	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	73
74	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	74
75	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	75
76	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	76
77	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	77
78	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	78
79	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	79
80	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	80
81	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	81
82	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	82
\.


--
-- Name: klasse_tils_publiceret_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klasse_tils_publiceret_id_seq', 82, true);


--
-- Data for Name: klassifikation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klassifikation (id) FROM stdin;
3ba4e044-4834-4913-9eaf-7247f094df58
\.


--
-- Data for Name: klassifikation_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klassifikation_registrering (id, klassifikation_id, registrering) FROM stdin;
1	3ba4e044-4834-4913-9eaf-7247f094df58	("[""2019-03-18 17:51:11.352726+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
\.


--
-- Data for Name: klassifikation_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klassifikation_attr_egenskaber (id, brugervendtnoegle, beskrivelse, kaldenavn, ophavsret, integrationsdata, virkning, klassifikation_registrering_id) FROM stdin;
1	Hjørring Kommune	umbrella	Hjørring Kommune	\N	{"Artificial import": "\\"Hj\\\\u00f8rring Kommune\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	1
\.


--
-- Name: klassifikation_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klassifikation_attr_egenskaber_id_seq', 1, true);


--
-- Name: klassifikation_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klassifikation_registrering_id_seq', 1, true);


--
-- Data for Name: klassifikation_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klassifikation_relation (id, klassifikation_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ansvarlig	organisation
2	1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	ejer	organisation
\.


--
-- Name: klassifikation_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klassifikation_relation_id_seq', 2, true);


--
-- Data for Name: klassifikation_tils_publiceret; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klassifikation_tils_publiceret (id, virkning, publiceret, klassifikation_registrering_id) FROM stdin;
1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	1
\.


--
-- Name: klassifikation_tils_publiceret_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klassifikation_tils_publiceret_id_seq', 1, true);


--
-- Data for Name: loghaendelse; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.loghaendelse (id) FROM stdin;
\.


--
-- Data for Name: loghaendelse_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.loghaendelse_registrering (id, loghaendelse_id, registrering) FROM stdin;
\.


--
-- Data for Name: loghaendelse_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.loghaendelse_attr_egenskaber (id, service, klasse, tidspunkt, operation, objekttype, returkode, returtekst, note, integrationsdata, virkning, loghaendelse_registrering_id) FROM stdin;
\.


--
-- Name: loghaendelse_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.loghaendelse_attr_egenskaber_id_seq', 1, false);


--
-- Name: loghaendelse_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.loghaendelse_registrering_id_seq', 1, false);


--
-- Data for Name: loghaendelse_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.loghaendelse_relation (id, loghaendelse_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
\.


--
-- Name: loghaendelse_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.loghaendelse_relation_id_seq', 1, false);


--
-- Data for Name: loghaendelse_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.loghaendelse_tils_gyldighed (id, virkning, gyldighed, loghaendelse_registrering_id) FROM stdin;
\.


--
-- Name: loghaendelse_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.loghaendelse_tils_gyldighed_id_seq', 1, false);


--
-- Data for Name: organisation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisation (id) FROM stdin;
e89f49ae-1521-4e2e-8adb-9572d159b77f
\.


--
-- Data for Name: organisation_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisation_registrering (id, organisation_id, registrering) FROM stdin;
1	e89f49ae-1521-4e2e-8adb-9572d159b77f	("[""2019-03-18 17:51:11.32231+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
\.


--
-- Data for Name: organisation_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisation_attr_egenskaber (id, brugervendtnoegle, organisationsnavn, integrationsdata, virkning, organisation_registrering_id) FROM stdin;
1	Hjørring Kommune	Hjørring Kommune	{"Artificial import": "\\"Hj\\\\u00f8rring Kommune\\"STOP"}	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	1
\.


--
-- Name: organisation_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisation_attr_egenskaber_id_seq', 1, true);


--
-- Name: organisation_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisation_registrering_id_seq', 1, true);


--
-- Data for Name: organisation_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisation_relation (id, organisation_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:kommune:0860	myndighed	\N
\.


--
-- Name: organisation_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisation_relation_id_seq', 1, true);


--
-- Data for Name: organisation_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisation_tils_gyldighed (id, virkning, gyldighed, organisation_registrering_id) FROM stdin;
1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	1
\.


--
-- Name: organisation_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisation_tils_gyldighed_id_seq', 1, true);


--
-- Data for Name: organisationenhed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationenhed (id) FROM stdin;
f06ee470-9f17-566f-acbe-e938112d46d9
b6c11152-0645-4712-a207-ba2c53b391ab
23a2ace2-52ca-458d-bead-d1a42080579f
7a8e45f7-4de0-44c8-990f-43c0565ee505
535ba446-d618-4e51-8dae-821d63e26560
9b7b3dde-16c9-4f88-87cc-e03aa5b4e709
d9f93150-f857-5197-bac0-d0182e165c4a
9723ddfb-a309-5b93-ace1-5b88c8336a66
95028aed-f341-57f9-b103-59f67e90cce6
81d20630-a126-577a-a47e-7a21155117d2
ff2afd49-0c26-556a-b01b-d2d6bd14a2af
b1b87a57-600b-5c1d-80aa-fe0ffd609d29
1da5de09-b1a8-5952-987d-04e07a3ffd50
5f03f259-598a-5a38-9cc1-36da20431f4b
f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92
485c8355-ac5e-57f1-b792-3dd5d1b1a0b4
81760628-a69b-584c-baf0-42d217442082
a726fbe8-32aa-55d0-a1c2-cb42ac13d42c
a6773531-6c0a-4c7b-b0e2-77992412b610
fb2d158f-114e-5f67-8365-2c520cf10b58
089ab2d1-d89f-586e-b8f2-46c17d7be9c8
578b004e-3fdf-54ec-a3ac-3d8a6dbd7635
832b9360-f294-5af2-a169-e12a4c7ad75e
759ffdf4-2fd0-5a9a-a1a4-3a0f8b6dc3f6
8cba51a7-44c7-5136-a842-cfdd9ff98f71
5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6
4aa42032-4f7b-5872-845d-8b5447e8573e
5f3973ef-a7a0-5270-900b-a80eab2ad6f9
c5d2f882-0112-5ffd-9071-6611ae8dda82
c73aa72a-8eb3-51f5-9b1e-cdece77c554a
4439ec5e-8daa-5d91-83d6-56874fb5b15b
cb33dd08-3948-501c-9e3f-1cef17f7094f
58b9cde5-6da2-59a8-aff6-0ec469c2da2a
d58c17a4-3b85-56be-8ffc-7a0be4ffd6da
9c64a7bc-b1ad-59c8-b6f1-ade9688dec0a
27c80741-19ae-5a0d-935e-b13d6d10e0c5
33264542-4103-5267-923e-a06661b342ef
d3d5b6d1-c3ef-51e6-8d29-632587912c09
\.


--
-- Data for Name: organisationenhed_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationenhed_registrering (id, organisationenhed_id, registrering) FROM stdin;
1	f06ee470-9f17-566f-acbe-e938112d46d9	("[""2019-03-18 17:51:13.931396+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
2	b6c11152-0645-4712-a207-ba2c53b391ab	("[""2019-03-18 17:51:14.5207+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
3	23a2ace2-52ca-458d-bead-d1a42080579f	("[""2019-03-18 17:51:14.862464+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
4	7a8e45f7-4de0-44c8-990f-43c0565ee505	("[""2019-03-18 17:51:15.193831+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
5	535ba446-d618-4e51-8dae-821d63e26560	("[""2019-03-18 17:51:15.714915+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
6	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	("[""2019-03-18 17:51:16.207808+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
7	d9f93150-f857-5197-bac0-d0182e165c4a	("[""2019-03-18 17:51:16.671177+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
8	9723ddfb-a309-5b93-ace1-5b88c8336a66	("[""2019-03-18 17:51:17.051577+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
9	95028aed-f341-57f9-b103-59f67e90cce6	("[""2019-03-18 17:51:17.616621+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
10	81d20630-a126-577a-a47e-7a21155117d2	("[""2019-03-18 17:51:17.950677+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
11	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	("[""2019-03-18 17:51:18.272576+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
12	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	("[""2019-03-18 17:51:18.655423+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
13	1da5de09-b1a8-5952-987d-04e07a3ffd50	("[""2019-03-18 17:51:18.985301+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
14	5f03f259-598a-5a38-9cc1-36da20431f4b	("[""2019-03-18 17:51:19.435825+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
15	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	("[""2019-03-18 17:51:19.854986+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
16	485c8355-ac5e-57f1-b792-3dd5d1b1a0b4	("[""2019-03-18 17:51:20.293464+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
17	81760628-a69b-584c-baf0-42d217442082	("[""2019-03-18 17:51:20.629314+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
18	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	("[""2019-03-18 17:51:21.008887+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
19	a6773531-6c0a-4c7b-b0e2-77992412b610	("[""2019-03-18 17:51:21.346489+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
20	fb2d158f-114e-5f67-8365-2c520cf10b58	("[""2019-03-18 17:51:21.785853+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
21	089ab2d1-d89f-586e-b8f2-46c17d7be9c8	("[""2019-03-18 17:51:22.130569+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
22	578b004e-3fdf-54ec-a3ac-3d8a6dbd7635	("[""2019-03-18 17:51:22.478992+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
23	832b9360-f294-5af2-a169-e12a4c7ad75e	("[""2019-03-18 17:51:22.840684+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
24	759ffdf4-2fd0-5a9a-a1a4-3a0f8b6dc3f6	("[""2019-03-18 17:51:23.27256+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
25	8cba51a7-44c7-5136-a842-cfdd9ff98f71	("[""2019-03-18 17:51:23.783236+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
26	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	("[""2019-03-18 17:51:24.180946+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
27	4aa42032-4f7b-5872-845d-8b5447e8573e	("[""2019-03-18 17:51:24.496796+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
28	5f3973ef-a7a0-5270-900b-a80eab2ad6f9	("[""2019-03-18 17:51:24.882055+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
29	c5d2f882-0112-5ffd-9071-6611ae8dda82	("[""2019-03-18 17:51:25.303078+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
30	c73aa72a-8eb3-51f5-9b1e-cdece77c554a	("[""2019-03-18 17:51:25.677135+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
31	4439ec5e-8daa-5d91-83d6-56874fb5b15b	("[""2019-03-18 17:51:26.294079+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
32	cb33dd08-3948-501c-9e3f-1cef17f7094f	("[""2019-03-18 17:51:26.710903+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
33	58b9cde5-6da2-59a8-aff6-0ec469c2da2a	("[""2019-03-18 17:51:27.065+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
34	d58c17a4-3b85-56be-8ffc-7a0be4ffd6da	("[""2019-03-18 17:51:27.440681+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
35	9c64a7bc-b1ad-59c8-b6f1-ade9688dec0a	("[""2019-03-18 17:51:27.764192+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
36	27c80741-19ae-5a0d-935e-b13d6d10e0c5	("[""2019-03-18 17:51:28.155774+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
37	33264542-4103-5267-923e-a06661b342ef	("[""2019-03-18 17:51:28.54709+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
38	d3d5b6d1-c3ef-51e6-8d29-632587912c09	("[""2019-03-18 17:51:28.886295+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
\.


--
-- Data for Name: organisationenhed_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationenhed_attr_egenskaber (id, brugervendtnoegle, enhedsnavn, integrationsdata, virkning, organisationenhed_registrering_id) FROM stdin;
1	Hjørring Kommune	Hjørring Kommune	{"Artificial import": "\\"root\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	1
2	Borgmesterens Afdeling	Borgmesterens Afdeling	{"Artificial import": "\\"b6c11152-0645-4712-a207-ba2c53b391ab\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	2
3	Teknik og Miljø	Teknik og Miljø	{"Artificial import": "\\"23a2ace2-52ca-458d-bead-d1a42080579f\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	3
4	Skole og Børn	Skole og Børn	{"Artificial import": "\\"7a8e45f7-4de0-44c8-990f-43c0565ee505\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4
5	Social Indsats	Social Indsats	{"Artificial import": "\\"535ba446-d618-4e51-8dae-821d63e26560\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5
6	IT-Support	IT-Support	{"Artificial import": "\\"9b7b3dde-16c9-4f88-87cc-e03aa5b4e709\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	6
7	Skoler og børnehaver	Skoler og børnehaver	{"Artificial import": "\\"d9f93150-f857-5197-bac0-d0182e165c4a\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7
8	Hirtshals skole	Hirtshals skole	{"Artificial import": "\\"9723ddfb-a309-5b93-ace1-5b88c8336a66\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	8
9	Løkken skole	Løkken skole	{"Artificial import": "\\"95028aed-f341-57f9-b103-59f67e90cce6\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9
10	Vrå skole	Vrå skole	{"Artificial import": "\\"81d20630-a126-577a-a47e-7a21155117d2\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	10
11	Hjørring skole	Hjørring skole	{"Artificial import": "\\"ff2afd49-0c26-556a-b01b-d2d6bd14a2af\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	11
12	Bindslev skole	Bindslev skole	{"Artificial import": "\\"b1b87a57-600b-5c1d-80aa-fe0ffd609d29\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	12
13	Sindal skole	Sindal skole	{"Artificial import": "\\"1da5de09-b1a8-5952-987d-04e07a3ffd50\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	13
14	Tårs skole	Tårs skole	{"Artificial import": "\\"5f03f259-598a-5a38-9cc1-36da20431f4b\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	14
15	Ålbæk skole	Ålbæk skole	{"Artificial import": "\\"f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	15
16	Jerslev J skole	Jerslev J skole	{"Artificial import": "\\"485c8355-ac5e-57f1-b792-3dd5d1b1a0b4\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	16
17	Frederikshavn skole	Frederikshavn skole	{"Artificial import": "\\"81760628-a69b-584c-baf0-42d217442082\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	17
18	Østervrå skole	Østervrå skole	{"Artificial import": "\\"a726fbe8-32aa-55d0-a1c2-cb42ac13d42c\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	18
19	Social og sundhed	Social og sundhed	{"Artificial import": "\\"a6773531-6c0a-4c7b-b0e2-77992412b610\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	19
20	Lønorganisation	Lønorganisation	{"Artificial import": "\\"extra_root\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	20
21	Borgmesterens Afdeling	Borgmesterens Afdeling	{"Artificial import": "\\"089ab2d1-d89f-586e-b8f2-46c17d7be9c8\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	21
22	Teknik og Miljø	Teknik og Miljø	{"Artificial import": "\\"578b004e-3fdf-54ec-a3ac-3d8a6dbd7635\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	22
23	Skole og Børn	Skole og Børn	{"Artificial import": "\\"832b9360-f294-5af2-a169-e12a4c7ad75e\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	23
24	Social Indsats	Social Indsats	{"Artificial import": "\\"759ffdf4-2fd0-5a9a-a1a4-3a0f8b6dc3f6\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	24
25	IT-Support	IT-Support	{"Artificial import": "\\"8cba51a7-44c7-5136-a842-cfdd9ff98f71\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	25
26	Skoler og børnehaver	Skoler og børnehaver	{"Artificial import": "\\"5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	26
27	Hirtshals skole	Hirtshals skole	{"Artificial import": "\\"4aa42032-4f7b-5872-845d-8b5447e8573e\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	27
28	Løkken skole	Løkken skole	{"Artificial import": "\\"5f3973ef-a7a0-5270-900b-a80eab2ad6f9\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	28
29	Vrå skole	Vrå skole	{"Artificial import": "\\"c5d2f882-0112-5ffd-9071-6611ae8dda82\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	29
30	Hjørring skole	Hjørring skole	{"Artificial import": "\\"c73aa72a-8eb3-51f5-9b1e-cdece77c554a\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	30
31	Bindslev skole	Bindslev skole	{"Artificial import": "\\"4439ec5e-8daa-5d91-83d6-56874fb5b15b\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	31
32	Sindal skole	Sindal skole	{"Artificial import": "\\"cb33dd08-3948-501c-9e3f-1cef17f7094f\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32
33	Tårs skole	Tårs skole	{"Artificial import": "\\"58b9cde5-6da2-59a8-aff6-0ec469c2da2a\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	33
34	Ålbæk skole	Ålbæk skole	{"Artificial import": "\\"d58c17a4-3b85-56be-8ffc-7a0be4ffd6da\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	34
35	Jerslev J skole	Jerslev J skole	{"Artificial import": "\\"9c64a7bc-b1ad-59c8-b6f1-ade9688dec0a\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	35
36	Frederikshavn skole	Frederikshavn skole	{"Artificial import": "\\"27c80741-19ae-5a0d-935e-b13d6d10e0c5\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	36
37	Østervrå skole	Østervrå skole	{"Artificial import": "\\"33264542-4103-5267-923e-a06661b342ef\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	37
38	Social og sundhed	Social og sundhed	{"Artificial import": "\\"d3d5b6d1-c3ef-51e6-8d29-632587912c09\\"STOP"}	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	38
\.


--
-- Name: organisationenhed_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationenhed_attr_egenskaber_id_seq', 38, true);


--
-- Name: organisationenhed_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationenhed_registrering_id_seq', 38, true);


--
-- Data for Name: organisationenhed_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationenhed_relation (id, organisationenhed_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
2	1	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
3	1	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	overordnet	\N
4	2	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
5	2	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
6	2	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	overordnet	\N
7	3	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
8	3	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
9	3	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	overordnet	\N
10	4	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
11	4	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
12	4	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	overordnet	\N
13	5	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
14	5	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
15	5	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	overordnet	\N
16	6	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
17	6	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
18	6	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	overordnet	\N
19	7	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
20	7	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
21	7	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	overordnet	\N
22	8	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
23	8	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
24	8	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
25	9	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
26	9	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
27	9	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
28	10	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
29	10	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
30	10	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
31	11	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
32	11	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
33	11	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
34	12	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
35	12	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
36	12	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
37	13	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
38	13	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
39	13	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
40	14	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
41	14	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
42	14	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
43	15	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
44	15	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
45	15	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
46	16	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
47	16	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
48	16	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
49	17	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
50	17	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
51	17	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
52	18	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
53	18	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
54	18	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	overordnet	\N
55	19	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
56	19	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
57	19	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	overordnet	\N
58	20	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
59	20	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
60	20	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	overordnet	\N
61	21	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
62	21	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
63	21	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	overordnet	\N
64	22	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
65	22	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
66	22	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	overordnet	\N
67	23	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
68	23	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
69	23	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	overordnet	\N
70	24	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
71	24	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
72	24	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	832b9360-f294-5af2-a169-e12a4c7ad75e	\N	overordnet	\N
73	25	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
74	25	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
75	25	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	832b9360-f294-5af2-a169-e12a4c7ad75e	\N	overordnet	\N
76	26	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
77	26	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
78	26	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	832b9360-f294-5af2-a169-e12a4c7ad75e	\N	overordnet	\N
79	27	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
80	27	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
81	27	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
82	28	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
83	28	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
84	28	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
85	29	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
86	29	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
87	29	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
88	30	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
89	30	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
90	30	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
91	31	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
92	31	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
93	31	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
94	32	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
95	32	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
96	32	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
97	33	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
98	33	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
99	33	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
100	34	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
101	34	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
102	34	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
103	35	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
104	35	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
105	35	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
106	36	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
107	36	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
108	36	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
109	37	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
110	37	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
111	37	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	overordnet	\N
112	38	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilhoerer	\N
113	38	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	06a6b95b-30a5-45d1-a180-389b9c4a6d0c	\N	enhedstype	\N
114	38	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	overordnet	\N
\.


--
-- Name: organisationenhed_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationenhed_relation_id_seq', 114, true);


--
-- Data for Name: organisationenhed_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationenhed_tils_gyldighed (id, virkning, gyldighed, organisationenhed_registrering_id) FROM stdin;
1	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	1
2	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	2
3	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	3
4	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	4
5	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	5
6	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	6
7	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	7
8	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	8
9	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	9
10	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	10
11	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	11
12	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	12
13	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	13
14	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	14
15	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	15
16	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	16
17	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	17
18	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	18
19	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	19
20	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	20
21	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	21
22	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	22
23	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	23
24	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	24
25	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	25
26	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	26
27	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	27
28	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	28
29	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	29
30	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	30
31	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	31
32	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	32
33	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	33
34	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	34
35	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	35
36	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	36
37	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	37
38	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	38
\.


--
-- Name: organisationenhed_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationenhed_tils_gyldighed_id_seq', 38, true);


--
-- Data for Name: organisationfunktion; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion (id) FROM stdin;
0af6436b-c697-4985-948b-52e7f6f22086
b2bb15be-4a64-4cdd-988c-3391ed0163fa
a9454e9c-8975-4022-a8d0-2161f020d7b8
ffbc8bff-da40-410c-9105-417493d6ee33
76adb1da-fd7a-43de-98dd-aa487b46e4b0
3a77f35c-77af-4648-88c3-175677fedf08
5b320ae8-e995-4fb1-b34c-09c1b264a90e
18f96f1e-019f-4f25-9c8a-edccb72a4e1a
e1859c92-a940-4614-abc3-919d8da132fb
732732c8-626c-4bce-88dc-b1d52332ca42
3bcb6494-99fc-41bb-83d5-30c62ed864c0
d27655f8-864a-4b3a-816a-8902145a308a
2afc7ba3-3b2e-40cf-87b5-100670845142
170c96a7-0d30-4a11-bc8d-94f193b4e231
dc64d6d8-6a8f-4844-a845-d62479e66283
148fe9d9-1ee8-4bae-a98a-868f63961668
6722a40c-0f5d-4184-9914-4cb26b84b1db
d0eb3ae2-3b81-43ab-832b-18f0c0020f0d
0c4fb6d2-8232-4c9e-aa5e-25b9002d892d
d8fad3a0-509d-413b-9079-f8717fdf9852
a85e8918-6b63-44ee-8295-b2ffab5d46c9
625e150e-3932-4101-a742-1efe5b86abbc
5e81071a-5d84-49fe-8f7f-4f65ab1d62eb
bcf651ba-d0eb-4e26-b86c-7a9504bd5cdd
4c530277-7e0e-4002-85b6-3cbd27d73ba2
fe43bef0-f08e-4022-be5f-67e9808b688d
519c0b85-2103-4ab8-aa9e-c27f88288e15
f4815eca-d4d3-4328-ad30-59f5c77732ee
e783a5b3-98e8-4cba-b3e6-38961a9fe657
2ad9b8bf-4af1-4830-b848-054b15293487
c34f791f-e871-4a42-9d8f-2b67618ac447
b747ae1c-3645-4e6b-9298-da189d738d08
d329c596-c362-412c-bf5b-3930bfc395d2
b060dba9-83fc-4cf7-a090-de499e78a2a8
75873e2b-023e-4383-b5b9-408f269312ad
a9c3eee1-5752-4182-bad5-8a18140ab5bf
ed4c6b04-0d08-4630-a412-242bec565921
3d2945b1-78c7-4ee5-9f15-28f0c0c47079
f7dabfa6-9e50-4bdf-a00b-b8899606dc93
b80984ad-e653-41d2-b81d-fed19453f183
c81178a2-5876-44c9-b55b-4fdd49e319c2
3f98e315-cf09-46da-9b2e-b9787722d192
518257e8-8bc4-4993-a099-bd27ef03347d
10f61a71-19f1-488a-8e45-7695af5f4c27
0971a873-69fb-48a7-8c3a-433d538f1d10
039d2acc-d211-4dac-8d44-4ff2889a98e6
ee2b3180-f4ed-435e-9269-5c2a17134a34
66650063-e6c0-4892-a21c-751002c53683
c7618f6d-ee45-4b14-9fe4-3f2f4adbf893
ab424e2b-0a72-4779-aba7-d5fd2dc265f2
3e3a096d-b083-4e79-832e-d5c742016dc3
3b966981-3c46-4c5a-8e7f-1d6b6b16ffa5
bc93375a-2e2d-4fad-a5d4-3f1405e3b579
b92efef7-8ffc-464f-afbe-b3b76f099e7b
6f1a4910-a68e-433b-a5a4-cf0e6ee9e804
07f18e27-c0db-47a2-a15e-b55c30998632
d0d4a083-39e1-4b74-96ab-21ca5314bd4a
f737ade5-511d-422c-92e1-0ac8f8607b1a
2239826c-31b5-4dda-aa62-6810b6354ee8
5e6b05ce-cb11-4cc9-b859-3878869efa83
252b0375-2e93-4612-8db1-e84a0148110a
69ece30e-7d11-4c3b-b21a-2bff9ba5aaa8
d8ec24e5-6541-4f33-b7c4-8e2496c62ca8
0a9cad06-1f24-4860-9eb2-fad38b9caebe
d6186ac7-7eb1-40e8-b4a5-06f045f6e9cb
dd7e9998-28bd-4592-8aaa-8ad338b059bc
b3278a69-c77d-464e-a22e-9ae14d07c879
faf11349-82fe-461d-bfeb-3b7466a0dff8
62d679c2-e828-45a9-a2ac-ec0460f61610
29e11fcf-ce9a-4522-8472-de4ce059490a
d7332ace-fd50-4454-a5e5-78cd28b3f3d9
9274cb1a-292b-43b0-8ebb-ad137dd71b6a
77879c51-2939-4112-9f34-dae06a50db85
496b846b-6e8e-403d-8603-63b86b876cac
cce291da-06b5-4ad4-a1a8-23c42aff4af8
dbe3fa1a-b437-4985-a6f7-ceccd9492f08
5b8692df-eead-4525-b791-1221c66a4f31
99e62499-d46d-4428-b903-f12701bf27fc
1dbb3d62-b88e-46bf-97f8-74727d809fdd
8d0eb868-95ae-4186-8fe0-d122b4a0305f
c7b2299f-48cc-4b8e-8b09-2a18fb35da00
1769d199-3ffa-47d1-bc73-254cc9f3ea68
bc317a7d-052e-469e-ba7a-35a55c8bb7b7
e0782979-9185-46dc-9c88-ac8c05a2a9ab
ba4ff8b4-de3c-4d85-a1f2-dd678b383e63
37a6ce8e-0bf7-4987-aea7-2aa7d99aeeb2
8d0b06a1-1f6e-48eb-ab76-8196bf91b440
12161200-098a-4d39-b9bf-6e9d582472af
b796a954-14fb-469e-babd-0e5055dd46e9
7020c63a-d599-4a31-9911-a2ccbbd953ec
7963ef60-a58f-43c6-94ac-5221c3b180d9
b075dd6e-27da-4a04-8960-aa2a1e15d52c
c2fdd28b-166a-43b5-a0d4-a41e53b62029
cd396ab7-e33a-4859-9252-76ca9e8ada6e
876bc518-d301-48f4-9104-0146e9521c79
463b7814-28c3-4b94-a6a4-a7839d58997a
f50c835b-40d5-4457-8c8e-7784f09f8546
e92d2386-ee17-4ce6-ab99-7a3b90cfc9c9
4c62bec6-e62b-4872-9f32-6fd027a2327e
1dc3b250-da09-45df-b227-ec0166277ffb
e25680d5-361e-450f-8eca-db5e0b88872a
82a62dbf-4f36-4534-9be6-9382c6d86203
323fe63c-d09e-4f2e-b67d-a79ea0d315f2
0f56abd8-c979-44b0-8ec1-85889c949cfc
e786d07e-24a8-4704-977c-7cd5b9325e43
e4cb8e1b-5fe5-430f-8359-ff88cea590d8
9e5db951-d6d9-4b31-8456-e5a67134ae12
a717b1c8-04c4-434a-9fae-ee1cbdd77c28
519f3d73-e0ad-4a60-bda3-4aecca1d2df6
c575ccd1-167f-4691-a823-76c68c80c090
d651a8e2-6311-4478-843f-966e29cf63c4
af6e7303-4474-4e12-8ea2-6b6e2de665fa
54013742-69c6-4d47-9194-223fbc7f4310
81c0873b-ec6a-4b16-bbbf-b6986b6e1b4f
35f97d04-e780-4b22-b68a-9ab07645cc13
0f851e29-85b1-4049-9c24-b798b63bf1f4
e9dffde6-55df-4929-bdfd-241cd0829271
07feb4f0-c56b-4926-9128-c53a7af26055
a83f3541-73d8-4b46-93cf-a1bf3716649b
507c1720-0801-433c-ae63-f263b9db6d0c
17ffe537-ba58-4983-8e5d-95617285a710
efa7430c-f237-446a-86b6-37b85158235f
59f22e73-57c3-4c82-afa2-3e1166c7f777
ef27991a-ad03-4edc-8be6-5ae133255312
2be07ef8-2ed5-49d1-b78e-efd3d6a3f72b
2acbb987-6a52-499d-ba27-7485221b6aef
cdbbe4c2-85d6-4526-aaa9-073a8145868d
7c68c16b-ec5a-4214-9d4f-6611abdb73d3
429ad454-c562-4b01-b270-ce89118357a8
33f87469-fdb6-4e91-ba16-3f5fa920c6fa
a060b581-c896-4dfb-bc9b-95e3a9a4a52a
a9c3c29c-3aab-4555-94fe-50e971a26488
5d45fbd5-09ee-4e1f-81f4-73fdee9dc089
dcfc63d0-ecdb-4d6f-86f4-5a412c8a6e48
4ab237ea-a198-4d23-969a-764a6e2cabc7
529b4a2a-619f-4f4a-8042-c41a708ce1d7
2326d246-c60f-4c55-9798-0ba84a660ca6
caa47fc3-682d-45e1-bd05-d72675c47d21
c29eb2af-83f4-4402-8c49-345e926a8836
967d73a6-bc47-4f76-ba7f-dce926cc8510
52756ea7-c840-46be-9cd9-d766b7fb2df0
a9f24e8e-ef6b-4155-af33-0cc5182f4fbd
5697d3d7-3ba0-412a-937b-9f8027d8f0cd
36e88a4e-40ae-4d86-9ea2-5174c107a90a
9581d1d9-3c53-4acd-874f-77007a888ee2
f65fa622-ac21-4489-a099-d05ba4964850
a1b70381-99bf-43ae-8f19-06f1ca22fcc9
c5e5625d-b282-4c87-94ea-38339a0bd366
4abf6482-cd06-4fde-a4bb-8bef69a31626
46e2a24e-a01f-4d65-ab44-bb117b9ea375
84e80d86-db39-4843-a877-0c8d84e15c90
7f0837fc-ad19-4505-99b9-236d2430ee5f
90388d7d-d180-494f-91b3-1cc20041cf1b
c4a22e31-6d29-4f81-90f7-d41100127cf0
a73cf013-4553-4667-a303-60c1ca7dbd9f
ef0696be-7ae1-44c0-92f6-d1e0e56439ef
54f07210-dc6b-4597-a12c-82bb80741de3
b3aecfb9-e782-457c-a944-dfb9107807f4
cfaf76d4-b34a-4f36-8cc6-2f65ec401777
9296d73f-1ea3-4690-be7a-0439d22e7b25
30c145b7-fb4a-48c3-a62f-2eb5b34dfc96
7c807936-9046-47a5-b64e-62305f363d25
be7de928-073f-4d2d-8db9-782f5eda3de5
be48406a-0559-4614-b326-878c18682ed4
3e495bf6-1ae1-4e3c-b574-1aaf51784e69
2ba62250-e56f-4d61-854c-bc3b803eaf4b
17d9ac72-a7a6-4da5-9727-5bd7d442e6d9
760f3b2e-45f3-409b-abd3-6743f27626bd
c7d5a36a-594a-4fe2-adea-59bbcf74fb75
62053fd0-6393-46e2-9130-a4e31dfd132a
7a9d0eb5-008e-4c6e-95e5-1dbb0726a322
02fffc1e-719a-43b5-9125-1c262ea566ab
6e7c5631-e6c7-470f-a232-08e7b9ac584d
cd27220a-39dd-4b7c-b281-4f447d3e931f
a7505f95-86e5-47b9-8675-2a7e73da3374
638e7f74-8413-4c50-b68e-659a50758899
d5ce829b-1455-43a1-8a0b-994a2f6d7c6c
dbd74308-4acf-497c-b86d-9ba06e967394
7ec9476f-5577-4c8f-9a13-df6e2e7ff168
e7a5ad26-57ed-41ef-bfe0-fe387ce3f3f3
78840711-2a45-48bd-abb9-247615e810a2
98828840-38bb-4ac2-ac96-e1b0fe5c3d11
346c7a2d-fdea-431f-a4d1-8cb08d6ef803
47f7a61e-ef13-4589-b8ec-f05efaa6dc8c
04723c84-f939-423f-a61b-bd746756ae5c
be76539c-d7d9-457f-b42c-f21e36e25e8a
08193cdc-67d8-4519-851b-5830a884cc0d
56e71b71-17e2-4532-be4c-8355a29ebc46
5f0ab40c-2902-4be1-8384-7e645799373c
9c4846bc-b7a3-4b23-9f03-2134cecbf5c9
b2c3ef60-b6b9-40bd-bfa1-0f0cb855dcdc
0040707c-22a0-4213-b056-80095adff4d4
e55e33c7-14ec-48fa-ae2d-8b70e93ce180
a01a7a0f-5228-446c-828e-cb8af9f14f39
4648b09b-45c1-4bf0-9836-8e5d6850d5db
c156adfa-a714-495f-8ba5-b14023d5cfd7
21c39797-c723-4e20-9d87-0baeda7212e3
e1b3b29e-2f7c-4d39-92be-5c6958d54a5c
e33267f5-7c74-4522-a99e-2103b9691812
436c97ac-214b-4c75-8db2-679f8f231024
764ed90a-0b04-4f58-bcbe-8a51beb62205
22e2b5f1-417f-44bd-95d4-e0d82cc2a108
31e684c9-bffe-482f-849b-5675aa01862e
ee1972d3-b235-4e6c-b077-6834b5123052
439775fd-76ca-429e-a4e9-eca2bb474097
bd6d9782-7bd2-40db-ac70-3f02163ba2b1
29dddad3-8fda-4a44-94e8-087ae5678c1b
331dd7a9-eee3-4cc9-98c0-c961fc0f49ad
e57d845b-152e-43d6-84b2-a45114352feb
c7306749-1404-4cbf-a7a1-23517d23625c
64e71ea3-9ee4-4460-b1af-5b1575fb2a69
3c003dcd-174d-4f7f-a6a8-ef2c69f2f0ac
af687487-3632-4d0b-8442-54b810d59484
5d5fd3cf-0d65-467c-846c-b97a5804e77e
feaabb96-e5e4-4c52-97d6-cb1690df99f3
d780c086-3dc7-4b86-9f69-20f760d75a6c
32a715bf-1e98-4c42-8a91-af6c5593fb0c
988e036c-4b07-44bb-8c42-e40c1f35fc76
1a3a3c49-266a-4c0f-88ab-83c03d1d148a
b244fb92-79b0-4a5f-8cde-abd88c24d5f4
7961bd27-b1c1-402c-b288-911f1d87ad77
8ccb287d-8d42-4a93-bc2e-2a304b27ec98
08f43fb5-48c1-47b0-9a64-ff0b322eeb61
b217f586-3bd7-4bef-9cc8-a2dbf8cbcd02
03c07011-49a7-4c60-8d53-0aabbb5c60e0
fe79c4c1-d2e1-48f0-ad98-846c57e05617
c5a9a25c-6a05-49ad-ab97-03b49080807c
a7e9b3b5-acd8-456b-9ded-ef2e02623551
343933a0-0af2-47ce-aeb7-a630d8d1c8f4
63d93d05-a71c-4e98-814d-895324cc5079
b0221d71-5fd4-4d37-ac96-978ff2a2584e
d685a963-d39a-45b1-be22-d0736f393b12
bc8d7387-1e62-4527-a992-37870d1c225b
3f199053-8438-453c-a61b-f7b76b0ff091
d19eb213-492e-4ca4-a572-c1f74e9cda57
855a79c4-88ab-4705-94e6-6f4e27782c6e
3fd0e2d5-02cb-47d1-94cb-1b683324a8b5
8e5dad7b-b0cf-4ea5-8e79-5305193a20df
4a9368c3-609c-49df-be49-2cd7d4f2d623
6710765d-21ca-4315-9065-9f5321d965ba
9c006190-a6e3-4917-8277-4b9e345521e0
a709f49e-0af2-4762-a3ec-daa1c148113f
7af0d850-271a-4a68-8858-cb8ec0f41cfa
85716ec9-058e-4b2e-8383-64bbbb36d4a9
307c56e7-0c58-4158-ac40-0db72607579a
898e01c0-5fc1-41ca-a2ad-530c5c886850
2206a01d-f388-42f4-a2a7-4626c1ae298a
bf392005-b539-4980-8701-b993b08ec7a2
2bb34779-f334-4bef-b18c-5e180b1145e3
4ce26c7e-3d35-4415-bfb2-56877c3a0e1b
a0ef86b6-274b-4eed-89c2-d31387114991
28dc863f-7023-4447-89a5-ee84a61758b1
8d8fb7a3-216c-4445-b690-27e44f038812
cab484ab-58f8-4404-8040-32d45bcaada2
2c49067c-7f19-4349-b81a-951a6bcf2507
c629775a-be9f-4033-b0ee-f295ae7f6f06
b6e0b844-310a-40f7-be0f-56da171a7fef
0fc5e796-6ca9-4d19-b3cd-c1ab437265b2
4746ae6a-2586-4c77-8ce2-25503907752b
6d5aa8c5-add2-4869-9585-3a402430ab1c
094243c7-8076-448f-95fe-76b3aebb780d
bfb716e1-c710-4e2d-a741-5225baaa0343
68776545-e8f4-4101-b87b-0d972ddef30a
4bc1b8b2-1670-4280-b022-fa585ae22a54
297fbdfb-23ca-4d20-a668-ebfea10af56e
535e687a-4a59-4c0f-9f2c-831b47b1f986
9b4dcb58-d1ea-4ba1-b626-3cb2ba6f590d
4f317790-7b23-4196-85a5-10454badec1f
1cb94851-7e40-43a3-b3f0-0420d40ac9f9
145c8c9f-58f4-4330-bd07-bfd55d662d02
5546cf24-0f07-4355-94e5-ef17695ae2e4
8dc22d1f-b012-4dc9-9813-72c8ef438419
0546113b-f75f-49cd-a806-fbd275df6862
cdf642df-f52b-4c50-985a-9b4e37e5d66f
b3eab4cd-c0e3-454f-b7e4-7eef49f601b0
6bacff47-9a47-4c44-8000-0d249887e0d3
d3fd168d-72ad-4341-ab9d-a0a4c6c8cd16
732f15de-0447-418f-94bd-9c7be187a908
5923c73d-5ba3-4947-a81f-16fb7b17b638
60fb673d-ff14-45dc-8470-930624cb3755
c07a054c-f5ca-4f23-b9d0-85b025dc93b4
982a8358-f9b4-474a-a40a-467c653a2215
c6535003-7079-4f97-b2b5-823991255dc1
310bdafa-b101-45ab-83ba-f139fa887bac
37b89fc4-64dd-4c57-8a3c-f07e0d5c1cd1
bbc51c27-1e23-4ce2-93e6-4aeeac530375
dc2b7293-245c-4669-ac4f-02def27ba670
cd44f85a-7b8b-41ee-8846-329ee3402ed5
aa7f251a-8401-4bdb-b9f2-75f3cca2bf82
1c80aa87-90bd-40f5-ba37-db97c849c171
dfb9135d-5212-4147-8a09-4efdb35b2081
4e74b325-8e38-4cf6-8618-0162acb01f8b
1538a49f-aac2-4641-adc6-f472561c211c
3d967f0e-4d32-4d04-93d6-d060f4f077e6
dfb5502b-352f-4502-90c9-41c55a37512d
74c48b26-c222-499b-bf2b-671881c8819a
615c07eb-502c-4837-b68c-dff2480c3bbc
80ca99e1-1add-4806-8782-9ac58ea54794
121cd0d2-59f4-48f7-99a9-e8e73e1ce815
47c9f266-cc0e-492e-97e4-d922d02c5cec
d8c9c1e5-aa0d-42e1-ae8f-2b9022d6a99d
c6d76039-204e-4f6e-8ffa-adb277d60571
0d746257-0c4f-4d0a-8aa2-8388d7656029
51cf4fd1-ef5f-45c0-9f1b-ce9e8bdfa215
81f53951-dabc-42ee-b1a7-91f0e57c5aa1
a3732137-a3c0-4a59-b1bb-67f532e09648
e4db92f9-73e7-4b51-89b2-d590deda6f55
6ab4d2de-c4a0-4efc-8961-0b0ec1c854b0
c5501129-6861-4aa5-8111-3a08e80019de
d58b7258-1c60-41f4-ba9f-e6106e9f8a0a
31d1647e-49b8-42f4-abc6-e9241aeb2668
73b1ffc7-b1f9-47f3-a4df-b997d3191db1
9acb200b-1b4f-4d47-ad53-a7e54e3e3098
713d2ffb-de4a-4f7e-90cc-9527a949653a
4c2c4d3c-110c-467d-a644-27e0d5c707bd
a3a47927-fe3b-4b95-8534-1a474d7c0c9d
4b6878c6-7b91-4e31-8da9-c6d16ecbbc72
4eb08260-01db-4573-98d2-2bdc12abe0b9
2337d27e-5057-42c7-b7f3-dbc05a7061d3
96e41147-f345-4124-a4d3-28c6633f190d
35731ee9-f8c8-4b48-b86f-338092dbfa9f
4847dc8a-db5a-4793-9762-d4a351598150
7dfb22f6-ef3c-4023-9d27-0f1226d703ab
53f83ba4-2c7f-4aca-8d09-81d432f66d00
24fd0191-cb4c-4925-b922-210cbae217ae
2570ea4f-7ee9-4880-af7c-4334c4ac63f9
48be9199-2810-4ee9-9e07-28c66246a199
8e5a1d40-55de-4f61-866c-6223f571a266
f86a5e1c-050f-4f8b-a031-f9a82e51d86b
f1581c1a-ae6c-47bb-b528-44aa6194e5fb
033b6c50-9176-4783-b4ba-cd24e25ace5c
ddbca8d8-87b1-4c54-9c3a-359613d56305
f5d52d9e-6fff-481a-8e6f-605d7080cc71
8abe95bd-51d4-4232-bb83-1b93b0b99fc6
9c00ed66-83b7-432d-9458-0fb164a536be
95e2cdbb-4c44-4ea8-9b6f-a47ba43354a7
81d32829-11e8-45a9-a83c-9a26003a5b50
fc02c4c9-9d61-464a-bca7-47e34a78acaf
adf8126c-f994-4a85-b56d-05088d61e4a7
057fe9ca-bb23-44e9-bb58-903c3f414617
3e2d1190-6bf5-4242-b500-f6e8c8fcda53
bafc0397-5231-40cd-b4c9-eb8e475fa3d7
fc4b7bf8-a6c2-462e-91c4-835a338ff653
dc082e95-d86a-4128-a96e-5859abb72e4d
7ed5afa1-00ae-4b9a-be02-fd714a7a273f
ce2e615e-f995-4e5c-8aea-7749b4019743
c9a769e4-695d-4b6c-9eb4-1da5705fbe6e
1ad699a6-4cf9-4a0b-8733-1326a6213b4f
9e6bd481-abbd-4f06-893d-d7ad55269b8a
ec5a69c6-d485-4e34-9c27-7ce2a28d60f4
8e78c287-b0ee-4754-9ce4-5c122dd0cc12
c93cbb7c-a6de-4e45-b313-2c8002ff1864
e23981db-2be0-4d5d-a100-d8f260e7f515
49801f11-38cb-4af9-9c7c-5428eed1d671
bf7651e7-5c80-45c5-959e-6cf7c32d967a
df3eaeb4-7631-46bc-b883-9d157e820d2a
e21d65e8-5da6-476c-8d17-bcf6ab24b126
260d4a19-142c-401e-a7c1-e664cb3ceeff
8ce225c1-26d6-4cac-b5d1-2fa4908b1556
e8189268-1711-4f84-83e7-dd5afca58298
54dea9b5-8e5b-4aaa-b45e-de3049360f35
c882d54d-f185-437b-9d64-c6e2a08cfd05
f63cb3dc-1c1d-45de-a69e-3d47c3be927a
0465128c-4ed7-4da0-b315-f3eaad6e2c64
338500b4-4bb8-4347-9d4b-fc4a21ea8225
9ab77d7e-f053-4247-ba07-5af407f67b12
3bfca148-60ad-45b5-a146-495f27ad09d1
dcb6152b-8572-47f9-9eff-caa85b19582b
c709134e-42bc-4211-ae28-a36707022646
8ab5989c-07df-4def-ab1e-ff3acee30b7c
2b683821-e03d-469a-a61b-172fb42eb845
ff79e983-3440-472e-87f6-7209e40e9b4c
5d9ee79f-3663-492f-832a-ab5a1f2f9fc7
2e206b0c-be59-40f8-bd3e-c16bd82873ee
d019d02c-2024-4760-9639-2af3c95608da
c9e2d62f-2b9d-4b1a-ba4e-27e8460bcbb7
0c4d9623-2826-42ad-af8f-bbae86aa4d86
ad65677e-1aed-41c3-9d4e-89e05a85ace5
79a88ad8-dae5-4a88-8a37-040b564a8031
55e54eeb-1495-454e-b18a-1f4deeff9ec5
54d406eb-4aed-4fd0-a7d1-da1ed18bc28f
418b2b4f-a2b0-4c2e-90c4-0608080ef52c
b8938cb0-82ec-405a-bf41-35667bdf4526
9c242516-ec2c-4e1d-a604-8bd74a1f51d2
2b3cf91e-6c52-4a34-8814-bf098ba1683d
bcadbd18-d69a-4d87-8938-c022fccb8fa6
3728c328-3dbc-4624-9abd-28a8aed0f75f
6e5937f0-276b-415e-ad6d-844d39330a5b
4fb2776a-0fea-4881-a249-910dc3168375
09f102c7-4df3-481e-a9c2-5a0b8e388b51
062362f3-44f0-462f-af2d-c1fb9e052f00
7780c4f1-68b9-4b9b-92ea-f600203cc290
b5a0882d-a45d-4004-be0c-1204191b83e4
a0531228-c7a2-48c2-a017-20d8d321ef52
502d2512-56b6-45d1-8766-3915ba48e476
3c5e87ad-7c96-4a33-ba30-a979f5544695
a2435035-38f8-4852-85b2-1f161b86d621
764cfd89-aab9-4023-a6fb-8b5720bd7811
1e665f2e-ba60-4da3-97ed-30012362ac81
c13903ba-2164-439c-8285-6123cfe859ad
d40ff9b8-e262-40b5-a062-b83d46b4d3e5
c56a35d0-899f-4041-8e9c-a1f0862c6c8e
ec88e050-093e-4a60-a902-56405da5c445
8b111e02-4a90-4d78-ac6a-6513e9181fe8
04434e17-a76b-47cc-bd81-0ae5d347591f
3c4df1f7-907d-40d5-9ea1-3014ac2f4099
45f69ef0-f612-4c80-ace8-8a52bfe03c68
99e3c87e-0d56-4161-96b6-ce9e4affd69f
631c36d5-d40f-41fb-8ce3-b4a44e2a4c1d
e1794985-4845-4f09-b807-0772e6bb5e94
1ba305ce-8715-408a-a444-579ce34465c6
bb21dd52-7eb8-4c25-a3cd-5c6bbafb75b2
3a00b39b-f8aa-4651-a93e-76657b9e4379
a0732504-b263-4e12-a30f-e83aaef55697
ec43a614-e895-4142-8e3b-fc5feaadd466
ecd0e09e-e4fa-4273-97a4-d67a0cae7744
edf11db2-2eab-416a-82d8-ee62c0fd446a
d8a936e5-caeb-4a9b-a3af-375ad253ce32
1b4f0c26-5643-44d4-92e1-1cc5be8f202a
0326836b-23ce-4311-83c3-cb0c260e136d
f911bbf7-5a94-441f-bf9e-1adf8d2a36e2
77075bd3-cb16-4231-96a4-5793a2d44ce7
7cf6ed26-715c-4d27-94ea-e4fae25b96b9
fe76785a-6796-4c69-9dad-2bf804ee560c
1062dc0c-6205-4d68-8d6e-714ef4334f6c
7c05c9fe-4a27-44fd-b361-4527b3f475d2
44a1616f-cf00-4092-855a-69eba2ac63a0
7863cc44-d192-42b2-b6ff-1fae09bfae13
10e9ca74-c578-4306-b4ce-8085b74f01b9
bf1c7108-1532-43ed-851b-1d5a3d782e67
4a19c870-40a6-44c9-83ad-f1c119a295df
d371da60-26d7-499a-b86d-84a509ef6d33
45efbd21-7290-4aa8-91fb-fd5f0c3cfc7b
dc356382-550c-44ec-bee6-5b0291e95761
052fc0d0-71f1-4686-b127-801261c2e6b6
bf6b09d9-100e-400b-8513-1a95c3d03c5e
e78ad8c5-c6c1-41f5-9f1e-59a915ddb796
0ad88710-0666-4e7d-b6e8-22dc02a12426
fdfd62ee-65a7-452d-8060-7dd1df0bf2e4
d4118f21-5d3a-4964-a70c-8281841d89dc
7763924c-1d4d-4d4d-9fc0-d7f0054e2e2a
a80f9329-415f-40aa-a91a-cb4fdf4ec2a7
318d1cce-8b70-401a-919a-6c524100c5a1
8167bc7f-2119-455b-83c3-6669e3867d7f
a4054184-b3ef-475b-944b-8d17e1b85e36
cf2b4464-c5dd-41a6-9f60-13b03d0f2e64
e5e24b08-dfb3-44b9-a528-17b05b8a1fc7
10cb5cc4-6b36-4cea-8573-85627aef2b71
ee56eddb-608f-4d9f-bbab-c4b8035d39ce
aeeab338-488f-467a-ba68-c0e3a3bb0f4f
a286d53b-0287-490e-a658-6853120d7b6c
6fd6ff6e-7b97-4ae9-b4de-7417935cf815
a73fb0e7-9605-484e-a43e-1ab0b574dd18
56e85f74-96b8-48a9-bc02-956d54409772
735d164e-8f7f-4e64-b0c8-33877970ac07
6c43688a-fd08-401e-9586-40b73f90b32d
d3094ca5-c684-4e4d-9995-5d2e8eb82db8
b842d99d-55c5-4317-9e76-448f4be70bf6
087bf6d7-87f2-47e3-a6cd-d214d0d3cd0a
f274a473-2d50-40d9-8454-5f13099d9dcf
1206bad8-00d3-456b-9301-8d20ad59339f
bf1f7af6-a5c2-45a8-a693-edd9f4f4a25b
2d5cfde2-353e-45d6-a9d8-fc73a5dacd73
0be0f856-fc8e-4eda-a9b1-5b227aa22431
fc9711de-c1ee-4e5c-b90d-8cc1565f17cf
7690b372-ff59-4cee-a5d0-37d851cbf275
28e2ec80-132e-4b9d-80df-17139669e58c
936f60d0-69ec-4368-b8db-b0bd0a03608c
96ddc0e4-3dc5-4d7c-8114-bb31958aa198
e03cf98f-33ae-46d1-89bf-09d195b60b27
b69a6887-9a37-478a-9838-1f4e0554fd3f
82c8aaf1-c54e-468f-802c-05113325bfa3
2db8bfd3-f2f0-4c3a-8e27-2b43af59ece5
9ef47d22-44b8-4be3-a219-a7025dffb829
dd739cdb-f0f7-453e-af98-6f7aa4913a4d
348da62f-f4bd-4372-87e4-fdbdc086b79c
eab2866c-0b7e-42a7-a018-19cd990e8745
9751d191-5ee3-43bd-93ba-ec73bc451039
1c00734f-5d62-4535-a3eb-23d97d923e1d
5e61aa72-a2b6-4828-9c80-578859d2a6fe
3b417eb4-9520-483a-8e0b-5634129fa439
06b15b46-ad85-4500-b871-f2627cbc2029
8db902c2-e3a0-4c75-92ef-2e614fc45392
8393c18b-7294-4cbd-8940-1513408963b9
05d27756-01a5-4522-8fa0-e835f7263b33
ddec011a-0c08-423e-8fda-371b5e87b092
03196ece-e0bc-4e50-95a4-7e716b7f8445
6a3845ba-8aaf-4298-9bbd-a602a9a847b5
9a1af9d5-ba66-4408-bf8b-47830146993e
8bd605bb-4fc8-42d0-a227-9f04c9c5a1ad
eebeb8ca-617c-4139-bc51-a9c9d35f83bb
2981b04c-0055-422f-b905-ac62df22006e
3053f9b9-f090-47bf-878e-7cee666892ed
98f4f007-0121-46af-8f35-fec6ff88af67
829f9eb5-8e03-4b74-a744-880016be5fc5
457f32f3-1312-40e2-9c5a-96e337652d80
b9fdd56c-7b41-4723-819f-387c623d7904
ea860fef-b7be-4472-b008-883c0b477e6e
8c15ffa3-0007-485f-ab3f-a3ec365b50c5
ac7a29b3-5108-4f72-8465-a64f2e4731f0
6aeb65f1-a19d-47e6-b8de-3c674fd1db3f
9c924c79-d38d-4fe0-b119-acb376bf094b
bf886fb8-88eb-4710-923b-9afbd8816373
843a75ba-0ed2-4a2f-9a95-acdf1b4e4cad
71a485e3-3e2b-4e3e-a324-fd193d26b06a
fe8b4f30-5e46-413f-bd3f-d56a3f6243db
48eddffb-9ba3-4ced-befe-7756e5fe3fb7
e7b0e1ce-2b0f-4778-9756-81fb326efb5f
bbe35033-a1bb-4329-9de0-0e309c646bb4
38e8341b-ba05-44c5-af66-f3944427799e
ac52f4c5-4355-4d7a-90ef-feb4fd993499
1cee0c9b-99b5-4d3d-b860-5746a397174e
e669466b-8322-475b-9d51-6a11b594b0ae
8beab5d6-e00a-44f7-bb01-02496e746138
903f448a-d0d0-41bc-9c7e-b847dd877f0f
22e7759b-5541-4782-87b5-ab6a4fb077b4
533c2c33-4d60-4f1b-9a55-b11cdc7370e4
25421e59-f821-401e-bc5b-bfc351edb450
3652d71a-9efb-485b-a655-7130ad2f088e
be9a372d-cbcb-4b25-b9f4-54e30cfdd533
8a723cb1-fb32-42a4-a6d2-d2d9ed06e27d
d3042c5e-85e7-4e29-9d29-b79ddcb61485
9965eeb8-6753-4997-85ab-6c5bcd5a6e91
9cd27883-fe1a-4116-8412-6fcec884c2a1
7a58216c-5dc7-44cf-bd1f-235203831985
0f6b66bf-aecf-4b8d-b6cf-7c0b1df1a6a3
c13b1283-99f3-43c1-a457-51ae7a572370
aa69de99-ab86-4099-96e0-611ffed5bcfa
fbd7a4f2-5562-45f6-9840-0dac1032542f
1d23ccc3-1c4e-4f34-ac95-fe3ac6eec0ea
\.


--
-- Data for Name: organisationfunktion_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion_registrering (id, organisationfunktion_id, registrering) FROM stdin;
1	0af6436b-c697-4985-948b-52e7f6f22086	("[""2019-03-18 17:51:14.360289+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
2	b2bb15be-4a64-4cdd-988c-3391ed0163fa	("[""2019-03-18 17:51:14.381867+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
3	a9454e9c-8975-4022-a8d0-2161f020d7b8	("[""2019-03-18 17:51:14.403683+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
4	ffbc8bff-da40-410c-9105-417493d6ee33	("[""2019-03-18 17:51:14.418163+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
5	76adb1da-fd7a-43de-98dd-aa487b46e4b0	("[""2019-03-18 17:51:14.432918+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
6	3a77f35c-77af-4648-88c3-175677fedf08	("[""2019-03-18 17:51:14.455064+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
7	5b320ae8-e995-4fb1-b34c-09c1b264a90e	("[""2019-03-18 17:51:14.469055+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
8	18f96f1e-019f-4f25-9c8a-edccb72a4e1a	("[""2019-03-18 17:51:14.747862+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
9	e1859c92-a940-4614-abc3-919d8da132fb	("[""2019-03-18 17:51:14.760989+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
10	732732c8-626c-4bce-88dc-b1d52332ca42	("[""2019-03-18 17:51:14.775053+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
11	3bcb6494-99fc-41bb-83d5-30c62ed864c0	("[""2019-03-18 17:51:14.789612+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
12	d27655f8-864a-4b3a-816a-8902145a308a	("[""2019-03-18 17:51:14.804092+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
13	2afc7ba3-3b2e-40cf-87b5-100670845142	("[""2019-03-18 17:51:14.817912+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
14	170c96a7-0d30-4a11-bc8d-94f193b4e231	("[""2019-03-18 17:51:15.071624+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
15	dc64d6d8-6a8f-4844-a845-d62479e66283	("[""2019-03-18 17:51:15.085778+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
16	148fe9d9-1ee8-4bae-a98a-868f63961668	("[""2019-03-18 17:51:15.102509+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
17	6722a40c-0f5d-4184-9914-4cb26b84b1db	("[""2019-03-18 17:51:15.117657+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
18	d0eb3ae2-3b81-43ab-832b-18f0c0020f0d	("[""2019-03-18 17:51:15.131684+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
19	0c4fb6d2-8232-4c9e-aa5e-25b9002d892d	("[""2019-03-18 17:51:15.147888+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
20	d8fad3a0-509d-413b-9079-f8717fdf9852	("[""2019-03-18 17:51:15.580861+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
21	a85e8918-6b63-44ee-8295-b2ffab5d46c9	("[""2019-03-18 17:51:15.600103+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
22	625e150e-3932-4101-a742-1efe5b86abbc	("[""2019-03-18 17:51:15.615384+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
23	5e81071a-5d84-49fe-8f7f-4f65ab1d62eb	("[""2019-03-18 17:51:15.629372+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
24	bcf651ba-d0eb-4e26-b86c-7a9504bd5cdd	("[""2019-03-18 17:51:15.647916+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
25	4c530277-7e0e-4002-85b6-3cbd27d73ba2	("[""2019-03-18 17:51:15.663237+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
26	fe43bef0-f08e-4022-be5f-67e9808b688d	("[""2019-03-18 17:51:16.05891+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
27	519c0b85-2103-4ab8-aa9e-c27f88288e15	("[""2019-03-18 17:51:16.07212+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
28	f4815eca-d4d3-4328-ad30-59f5c77732ee	("[""2019-03-18 17:51:16.086021+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
29	e783a5b3-98e8-4cba-b3e6-38961a9fe657	("[""2019-03-18 17:51:16.106681+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
30	2ad9b8bf-4af1-4830-b848-054b15293487	("[""2019-03-18 17:51:16.121241+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
31	c34f791f-e871-4a42-9d8f-2b67618ac447	("[""2019-03-18 17:51:16.13644+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
32	b747ae1c-3645-4e6b-9298-da189d738d08	("[""2019-03-18 17:51:16.156491+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
33	d329c596-c362-412c-bf5b-3930bfc395d2	("[""2019-03-18 17:51:16.510989+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
34	b060dba9-83fc-4cf7-a090-de499e78a2a8	("[""2019-03-18 17:51:16.524861+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
35	75873e2b-023e-4383-b5b9-408f269312ad	("[""2019-03-18 17:51:16.537748+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
36	a9c3eee1-5752-4182-bad5-8a18140ab5bf	("[""2019-03-18 17:51:16.553183+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
37	ed4c6b04-0d08-4630-a412-242bec565921	("[""2019-03-18 17:51:16.567738+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
38	3d2945b1-78c7-4ee5-9f15-28f0c0c47079	("[""2019-03-18 17:51:16.581418+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
39	f7dabfa6-9e50-4bdf-a00b-b8899606dc93	("[""2019-03-18 17:51:16.595889+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
40	b80984ad-e653-41d2-b81d-fed19453f183	("[""2019-03-18 17:51:16.922479+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
41	c81178a2-5876-44c9-b55b-4fdd49e319c2	("[""2019-03-18 17:51:16.938898+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
42	3f98e315-cf09-46da-9b2e-b9787722d192	("[""2019-03-18 17:51:16.955146+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
43	518257e8-8bc4-4993-a099-bd27ef03347d	("[""2019-03-18 17:51:16.970806+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
44	10f61a71-19f1-488a-8e45-7695af5f4c27	("[""2019-03-18 17:51:16.985722+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
45	0971a873-69fb-48a7-8c3a-433d538f1d10	("[""2019-03-18 17:51:17.003639+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
46	039d2acc-d211-4dac-8d44-4ff2889a98e6	("[""2019-03-18 17:51:17.483913+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
47	ee2b3180-f4ed-435e-9269-5c2a17134a34	("[""2019-03-18 17:51:17.498888+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
48	66650063-e6c0-4892-a21c-751002c53683	("[""2019-03-18 17:51:17.514853+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
49	c7618f6d-ee45-4b14-9fe4-3f2f4adbf893	("[""2019-03-18 17:51:17.527742+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
50	ab424e2b-0a72-4779-aba7-d5fd2dc265f2	("[""2019-03-18 17:51:17.542013+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
51	3e3a096d-b083-4e79-832e-d5c742016dc3	("[""2019-03-18 17:51:17.557054+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
52	3b966981-3c46-4c5a-8e7f-1d6b6b16ffa5	("[""2019-03-18 17:51:17.571652+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
53	bc93375a-2e2d-4fad-a5d4-3f1405e3b579	("[""2019-03-18 17:51:17.833179+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
54	b92efef7-8ffc-464f-afbe-b3b76f099e7b	("[""2019-03-18 17:51:17.847497+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
55	6f1a4910-a68e-433b-a5a4-cf0e6ee9e804	("[""2019-03-18 17:51:17.862214+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
56	07f18e27-c0db-47a2-a15e-b55c30998632	("[""2019-03-18 17:51:17.876248+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
57	d0d4a083-39e1-4b74-96ab-21ca5314bd4a	("[""2019-03-18 17:51:17.890561+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
58	f737ade5-511d-422c-92e1-0ac8f8607b1a	("[""2019-03-18 17:51:17.904856+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
59	2239826c-31b5-4dda-aa62-6810b6354ee8	("[""2019-03-18 17:51:18.154811+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
60	5e6b05ce-cb11-4cc9-b859-3878869efa83	("[""2019-03-18 17:51:18.16964+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
61	252b0375-2e93-4612-8db1-e84a0148110a	("[""2019-03-18 17:51:18.184458+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
62	69ece30e-7d11-4c3b-b21a-2bff9ba5aaa8	("[""2019-03-18 17:51:18.199218+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
63	d8ec24e5-6541-4f33-b7c4-8e2496c62ca8	("[""2019-03-18 17:51:18.214493+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
64	0a9cad06-1f24-4860-9eb2-fad38b9caebe	("[""2019-03-18 17:51:18.227425+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
65	d6186ac7-7eb1-40e8-b4a5-06f045f6e9cb	("[""2019-03-18 17:51:18.540196+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
66	dd7e9998-28bd-4592-8aaa-8ad338b059bc	("[""2019-03-18 17:51:18.553794+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
67	b3278a69-c77d-464e-a22e-9ae14d07c879	("[""2019-03-18 17:51:18.568694+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
68	faf11349-82fe-461d-bfeb-3b7466a0dff8	("[""2019-03-18 17:51:18.583488+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
69	62d679c2-e828-45a9-a2ac-ec0460f61610	("[""2019-03-18 17:51:18.59812+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
70	29e11fcf-ce9a-4522-8472-de4ce059490a	("[""2019-03-18 17:51:18.61243+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
71	d7332ace-fd50-4454-a5e5-78cd28b3f3d9	("[""2019-03-18 17:51:18.867811+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
72	9274cb1a-292b-43b0-8ebb-ad137dd71b6a	("[""2019-03-18 17:51:18.881491+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
73	77879c51-2939-4112-9f34-dae06a50db85	("[""2019-03-18 17:51:18.895756+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
74	496b846b-6e8e-403d-8603-63b86b876cac	("[""2019-03-18 17:51:18.90959+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
75	cce291da-06b5-4ad4-a1a8-23c42aff4af8	("[""2019-03-18 17:51:18.922754+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
76	dbe3fa1a-b437-4985-a6f7-ceccd9492f08	("[""2019-03-18 17:51:18.936092+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
77	5b8692df-eead-4525-b791-1221c66a4f31	("[""2019-03-18 17:51:19.295886+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
78	99e62499-d46d-4428-b903-f12701bf27fc	("[""2019-03-18 17:51:19.31188+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
79	1dbb3d62-b88e-46bf-97f8-74727d809fdd	("[""2019-03-18 17:51:19.32756+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
80	8d0eb868-95ae-4186-8fe0-d122b4a0305f	("[""2019-03-18 17:51:19.342787+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
81	c7b2299f-48cc-4b8e-8b09-2a18fb35da00	("[""2019-03-18 17:51:19.359776+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
82	1769d199-3ffa-47d1-bc73-254cc9f3ea68	("[""2019-03-18 17:51:19.374789+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
83	bc317a7d-052e-469e-ba7a-35a55c8bb7b7	("[""2019-03-18 17:51:19.390077+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
84	e0782979-9185-46dc-9c88-ac8c05a2a9ab	("[""2019-03-18 17:51:19.741278+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
85	ba4ff8b4-de3c-4d85-a1f2-dd678b383e63	("[""2019-03-18 17:51:19.754825+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
86	37a6ce8e-0bf7-4987-aea7-2aa7d99aeeb2	("[""2019-03-18 17:51:19.768802+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
87	8d0b06a1-1f6e-48eb-ab76-8196bf91b440	("[""2019-03-18 17:51:19.783434+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
88	12161200-098a-4d39-b9bf-6e9d582472af	("[""2019-03-18 17:51:19.797189+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
89	b796a954-14fb-469e-babd-0e5055dd46e9	("[""2019-03-18 17:51:19.810428+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
90	7020c63a-d599-4a31-9911-a2ccbbd953ec	("[""2019-03-18 17:51:20.156385+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
91	7963ef60-a58f-43c6-94ac-5221c3b180d9	("[""2019-03-18 17:51:20.17049+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
92	b075dd6e-27da-4a04-8960-aa2a1e15d52c	("[""2019-03-18 17:51:20.185698+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
93	c2fdd28b-166a-43b5-a0d4-a41e53b62029	("[""2019-03-18 17:51:20.201416+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
94	cd396ab7-e33a-4859-9252-76ca9e8ada6e	("[""2019-03-18 17:51:20.216366+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
95	876bc518-d301-48f4-9104-0146e9521c79	("[""2019-03-18 17:51:20.229921+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
96	463b7814-28c3-4b94-a6a4-a7839d58997a	("[""2019-03-18 17:51:20.244547+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
97	f50c835b-40d5-4457-8c8e-7784f09f8546	("[""2019-03-18 17:51:20.513694+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
98	e92d2386-ee17-4ce6-ab99-7a3b90cfc9c9	("[""2019-03-18 17:51:20.527155+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
99	4c62bec6-e62b-4872-9f32-6fd027a2327e	("[""2019-03-18 17:51:20.54125+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
100	1dc3b250-da09-45df-b227-ec0166277ffb	("[""2019-03-18 17:51:20.556555+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
101	e25680d5-361e-450f-8eca-db5e0b88872a	("[""2019-03-18 17:51:20.571095+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
102	82a62dbf-4f36-4534-9be6-9382c6d86203	("[""2019-03-18 17:51:20.585368+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
103	323fe63c-d09e-4f2e-b67d-a79ea0d315f2	("[""2019-03-18 17:51:20.877422+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
104	0f56abd8-c979-44b0-8ec1-85889c949cfc	("[""2019-03-18 17:51:20.891605+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
105	e786d07e-24a8-4704-977c-7cd5b9325e43	("[""2019-03-18 17:51:20.907182+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
106	e4cb8e1b-5fe5-430f-8359-ff88cea590d8	("[""2019-03-18 17:51:20.921935+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
107	9e5db951-d6d9-4b31-8456-e5a67134ae12	("[""2019-03-18 17:51:20.934971+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
108	a717b1c8-04c4-434a-9fae-ee1cbdd77c28	("[""2019-03-18 17:51:20.949309+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
109	519f3d73-e0ad-4a60-bda3-4aecca1d2df6	("[""2019-03-18 17:51:20.965841+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
110	c575ccd1-167f-4691-a823-76c68c80c090	("[""2019-03-18 17:51:21.228358+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
111	d651a8e2-6311-4478-843f-966e29cf63c4	("[""2019-03-18 17:51:21.242205+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
112	af6e7303-4474-4e12-8ea2-6b6e2de665fa	("[""2019-03-18 17:51:21.256307+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
113	54013742-69c6-4d47-9194-223fbc7f4310	("[""2019-03-18 17:51:21.269454+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
114	81c0873b-ec6a-4b16-bbbf-b6986b6e1b4f	("[""2019-03-18 17:51:21.284788+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
115	35f97d04-e780-4b22-b68a-9ab07645cc13	("[""2019-03-18 17:51:21.299432+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
116	0f851e29-85b1-4049-9c24-b798b63bf1f4	("[""2019-03-18 17:51:21.65984+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
117	e9dffde6-55df-4929-bdfd-241cd0829271	("[""2019-03-18 17:51:21.67316+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
118	07feb4f0-c56b-4926-9128-c53a7af26055	("[""2019-03-18 17:51:21.687474+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
119	a83f3541-73d8-4b46-93cf-a1bf3716649b	("[""2019-03-18 17:51:21.702323+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
120	507c1720-0801-433c-ae63-f263b9db6d0c	("[""2019-03-18 17:51:21.716628+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
121	17ffe537-ba58-4983-8e5d-95617285a710	("[""2019-03-18 17:51:21.730989+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
122	efa7430c-f237-446a-86b6-37b85158235f	("[""2019-03-18 17:51:22.003012+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
123	59f22e73-57c3-4c82-afa2-3e1166c7f777	("[""2019-03-18 17:51:22.017647+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
124	ef27991a-ad03-4edc-8be6-5ae133255312	("[""2019-03-18 17:51:22.032142+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
125	2be07ef8-2ed5-49d1-b78e-efd3d6a3f72b	("[""2019-03-18 17:51:22.046708+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
126	2acbb987-6a52-499d-ba27-7485221b6aef	("[""2019-03-18 17:51:22.060118+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
127	cdbbe4c2-85d6-4526-aaa9-073a8145868d	("[""2019-03-18 17:51:22.072926+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
128	7c68c16b-ec5a-4214-9d4f-6611abdb73d3	("[""2019-03-18 17:51:22.086985+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
129	429ad454-c562-4b01-b270-ce89118357a8	("[""2019-03-18 17:51:22.361689+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
130	33f87469-fdb6-4e91-ba16-3f5fa920c6fa	("[""2019-03-18 17:51:22.376576+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
131	a060b581-c896-4dfb-bc9b-95e3a9a4a52a	("[""2019-03-18 17:51:22.39085+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
132	a9c3c29c-3aab-4555-94fe-50e971a26488	("[""2019-03-18 17:51:22.405003+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
133	5d45fbd5-09ee-4e1f-81f4-73fdee9dc089	("[""2019-03-18 17:51:22.419289+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
134	dcfc63d0-ecdb-4d6f-86f4-5a412c8a6e48	("[""2019-03-18 17:51:22.433766+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
135	4ab237ea-a198-4d23-969a-764a6e2cabc7	("[""2019-03-18 17:51:22.706514+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
136	529b4a2a-619f-4f4a-8042-c41a708ce1d7	("[""2019-03-18 17:51:22.721615+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
137	2326d246-c60f-4c55-9798-0ba84a660ca6	("[""2019-03-18 17:51:22.736719+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
138	caa47fc3-682d-45e1-bd05-d72675c47d21	("[""2019-03-18 17:51:22.751946+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
139	c29eb2af-83f4-4402-8c49-345e926a8836	("[""2019-03-18 17:51:22.76608+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
140	967d73a6-bc47-4f76-ba7f-dce926cc8510	("[""2019-03-18 17:51:22.781707+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
141	52756ea7-c840-46be-9cd9-d766b7fb2df0	("[""2019-03-18 17:51:22.798233+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
142	a9f24e8e-ef6b-4155-af33-0cc5182f4fbd	("[""2019-03-18 17:51:23.154445+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
143	5697d3d7-3ba0-412a-937b-9f8027d8f0cd	("[""2019-03-18 17:51:23.168439+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
144	36e88a4e-40ae-4d86-9ea2-5174c107a90a	("[""2019-03-18 17:51:23.182802+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
145	9581d1d9-3c53-4acd-874f-77007a888ee2	("[""2019-03-18 17:51:23.198593+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
146	f65fa622-ac21-4489-a099-d05ba4964850	("[""2019-03-18 17:51:23.214278+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
147	a1b70381-99bf-43ae-8f19-06f1ca22fcc9	("[""2019-03-18 17:51:23.228571+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
148	c5e5625d-b282-4c87-94ea-38339a0bd366	("[""2019-03-18 17:51:23.664952+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
149	4abf6482-cd06-4fde-a4bb-8bef69a31626	("[""2019-03-18 17:51:23.679593+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
150	46e2a24e-a01f-4d65-ab44-bb117b9ea375	("[""2019-03-18 17:51:23.694536+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
151	84e80d86-db39-4843-a877-0c8d84e15c90	("[""2019-03-18 17:51:23.708874+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
152	7f0837fc-ad19-4505-99b9-236d2430ee5f	("[""2019-03-18 17:51:23.723806+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
153	90388d7d-d180-494f-91b3-1cc20041cf1b	("[""2019-03-18 17:51:23.738697+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
154	c4a22e31-6d29-4f81-90f7-d41100127cf0	("[""2019-03-18 17:51:24.065604+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
155	a73cf013-4553-4667-a303-60c1ca7dbd9f	("[""2019-03-18 17:51:24.07965+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
156	ef0696be-7ae1-44c0-92f6-d1e0e56439ef	("[""2019-03-18 17:51:24.093508+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
157	54f07210-dc6b-4597-a12c-82bb80741de3	("[""2019-03-18 17:51:24.107389+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
158	b3aecfb9-e782-457c-a944-dfb9107807f4	("[""2019-03-18 17:51:24.122893+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
159	cfaf76d4-b34a-4f36-8cc6-2f65ec401777	("[""2019-03-18 17:51:24.137807+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
160	9296d73f-1ea3-4690-be7a-0439d22e7b25	("[""2019-03-18 17:51:24.380077+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
161	30c145b7-fb4a-48c3-a62f-2eb5b34dfc96	("[""2019-03-18 17:51:24.394597+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
162	7c807936-9046-47a5-b64e-62305f363d25	("[""2019-03-18 17:51:24.409791+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
163	be7de928-073f-4d2d-8db9-782f5eda3de5	("[""2019-03-18 17:51:24.424223+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
164	be48406a-0559-4614-b326-878c18682ed4	("[""2019-03-18 17:51:24.438722+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
165	3e495bf6-1ae1-4e3c-b574-1aaf51784e69	("[""2019-03-18 17:51:24.453066+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
166	2ba62250-e56f-4d61-854c-bc3b803eaf4b	("[""2019-03-18 17:51:24.715888+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
167	17d9ac72-a7a6-4da5-9727-5bd7d442e6d9	("[""2019-03-18 17:51:24.729966+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
168	760f3b2e-45f3-409b-abd3-6743f27626bd	("[""2019-03-18 17:51:24.744702+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
169	c7d5a36a-594a-4fe2-adea-59bbcf74fb75	("[""2019-03-18 17:51:24.758987+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
170	62053fd0-6393-46e2-9130-a4e31dfd132a	("[""2019-03-18 17:51:24.773552+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
171	7a9d0eb5-008e-4c6e-95e5-1dbb0726a322	("[""2019-03-18 17:51:24.78837+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
172	02fffc1e-719a-43b5-9125-1c262ea566ab	("[""2019-03-18 17:51:24.802714+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
173	6e7c5631-e6c7-470f-a232-08e7b9ac584d	("[""2019-03-18 17:51:25.180558+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
174	cd27220a-39dd-4b7c-b281-4f447d3e931f	("[""2019-03-18 17:51:25.194408+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
175	a7505f95-86e5-47b9-8675-2a7e73da3374	("[""2019-03-18 17:51:25.20892+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
176	638e7f74-8413-4c50-b68e-659a50758899	("[""2019-03-18 17:51:25.223722+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
177	d5ce829b-1455-43a1-8a0b-994a2f6d7c6c	("[""2019-03-18 17:51:25.239451+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
178	dbd74308-4acf-497c-b86d-9ba06e967394	("[""2019-03-18 17:51:25.25621+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
179	7ec9476f-5577-4c8f-9a13-df6e2e7ff168	("[""2019-03-18 17:51:25.564357+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
180	e7a5ad26-57ed-41ef-bfe0-fe387ce3f3f3	("[""2019-03-18 17:51:25.578493+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
181	78840711-2a45-48bd-abb9-247615e810a2	("[""2019-03-18 17:51:25.592106+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
182	98828840-38bb-4ac2-ac96-e1b0fe5c3d11	("[""2019-03-18 17:51:25.605903+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
183	346c7a2d-fdea-431f-a4d1-8cb08d6ef803	("[""2019-03-18 17:51:25.62038+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
184	47f7a61e-ef13-4589-b8ec-f05efaa6dc8c	("[""2019-03-18 17:51:25.63472+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
185	04723c84-f939-423f-a61b-bd746756ae5c	("[""2019-03-18 17:51:26.177966+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
186	be76539c-d7d9-457f-b42c-f21e36e25e8a	("[""2019-03-18 17:51:26.193665+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
187	08193cdc-67d8-4519-851b-5830a884cc0d	("[""2019-03-18 17:51:26.207629+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
188	56e71b71-17e2-4532-be4c-8355a29ebc46	("[""2019-03-18 17:51:26.221456+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
189	5f0ab40c-2902-4be1-8384-7e645799373c	("[""2019-03-18 17:51:26.236635+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
190	9c4846bc-b7a3-4b23-9f03-2134cecbf5c9	("[""2019-03-18 17:51:26.251689+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
191	b2c3ef60-b6b9-40bd-bfa1-0f0cb855dcdc	("[""2019-03-18 17:51:26.583717+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
192	0040707c-22a0-4213-b056-80095adff4d4	("[""2019-03-18 17:51:26.598022+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
193	e55e33c7-14ec-48fa-ae2d-8b70e93ce180	("[""2019-03-18 17:51:26.613774+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
194	a01a7a0f-5228-446c-828e-cb8af9f14f39	("[""2019-03-18 17:51:26.628084+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
195	4648b09b-45c1-4bf0-9836-8e5d6850d5db	("[""2019-03-18 17:51:26.642283+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
196	c156adfa-a714-495f-8ba5-b14023d5cfd7	("[""2019-03-18 17:51:26.655904+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
197	21c39797-c723-4e20-9d87-0baeda7212e3	("[""2019-03-18 17:51:26.668198+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
198	e1b3b29e-2f7c-4d39-92be-5c6958d54a5c	("[""2019-03-18 17:51:26.939023+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
199	e33267f5-7c74-4522-a99e-2103b9691812	("[""2019-03-18 17:51:26.952414+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
200	436c97ac-214b-4c75-8db2-679f8f231024	("[""2019-03-18 17:51:26.967001+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
201	764ed90a-0b04-4f58-bcbe-8a51beb62205	("[""2019-03-18 17:51:26.981475+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
202	22e2b5f1-417f-44bd-95d4-e0d82cc2a108	("[""2019-03-18 17:51:26.994555+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
203	31e684c9-bffe-482f-849b-5675aa01862e	("[""2019-03-18 17:51:27.007863+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
204	ee1972d3-b235-4e6c-b077-6834b5123052	("[""2019-03-18 17:51:27.022676+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
205	439775fd-76ca-429e-a4e9-eca2bb474097	("[""2019-03-18 17:51:27.310338+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
206	bd6d9782-7bd2-40db-ac70-3f02163ba2b1	("[""2019-03-18 17:51:27.324758+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
207	29dddad3-8fda-4a44-94e8-087ae5678c1b	("[""2019-03-18 17:51:27.339419+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
208	331dd7a9-eee3-4cc9-98c0-c961fc0f49ad	("[""2019-03-18 17:51:27.355221+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
209	e57d845b-152e-43d6-84b2-a45114352feb	("[""2019-03-18 17:51:27.368703+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
210	c7306749-1404-4cbf-a7a1-23517d23625c	("[""2019-03-18 17:51:27.383678+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
211	64e71ea3-9ee4-4460-b1af-5b1575fb2a69	("[""2019-03-18 17:51:27.398517+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
212	3c003dcd-174d-4f7f-a6a8-ef2c69f2f0ac	("[""2019-03-18 17:51:27.650876+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
213	af687487-3632-4d0b-8442-54b810d59484	("[""2019-03-18 17:51:27.664068+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
214	5d5fd3cf-0d65-467c-846c-b97a5804e77e	("[""2019-03-18 17:51:27.677543+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
215	feaabb96-e5e4-4c52-97d6-cb1690df99f3	("[""2019-03-18 17:51:27.692329+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
216	d780c086-3dc7-4b86-9f69-20f760d75a6c	("[""2019-03-18 17:51:27.706966+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
217	32a715bf-1e98-4c42-8a91-af6c5593fb0c	("[""2019-03-18 17:51:27.720701+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
218	988e036c-4b07-44bb-8c42-e40c1f35fc76	("[""2019-03-18 17:51:28.041399+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
219	1a3a3c49-266a-4c0f-88ab-83c03d1d148a	("[""2019-03-18 17:51:28.055951+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
220	b244fb92-79b0-4a5f-8cde-abd88c24d5f4	("[""2019-03-18 17:51:28.071183+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
221	7961bd27-b1c1-402c-b288-911f1d87ad77	("[""2019-03-18 17:51:28.085289+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
222	8ccb287d-8d42-4a93-bc2e-2a304b27ec98	("[""2019-03-18 17:51:28.100032+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
223	08f43fb5-48c1-47b0-9a64-ff0b322eeb61	("[""2019-03-18 17:51:28.113842+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
224	b217f586-3bd7-4bef-9cc8-a2dbf8cbcd02	("[""2019-03-18 17:51:28.430367+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
225	03c07011-49a7-4c60-8d53-0aabbb5c60e0	("[""2019-03-18 17:51:28.444709+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
226	fe79c4c1-d2e1-48f0-ad98-846c57e05617	("[""2019-03-18 17:51:28.459684+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
227	c5a9a25c-6a05-49ad-ab97-03b49080807c	("[""2019-03-18 17:51:28.474842+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
228	a7e9b3b5-acd8-456b-9ded-ef2e02623551	("[""2019-03-18 17:51:28.488812+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
229	343933a0-0af2-47ce-aeb7-a630d8d1c8f4	("[""2019-03-18 17:51:28.503216+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
230	63d93d05-a71c-4e98-814d-895324cc5079	("[""2019-03-18 17:51:28.768339+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
231	b0221d71-5fd4-4d37-ac96-978ff2a2584e	("[""2019-03-18 17:51:28.782567+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
232	d685a963-d39a-45b1-be22-d0736f393b12	("[""2019-03-18 17:51:28.797406+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
233	bc8d7387-1e62-4527-a992-37870d1c225b	("[""2019-03-18 17:51:28.812477+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
234	3f199053-8438-453c-a61b-f7b76b0ff091	("[""2019-03-18 17:51:28.826056+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
235	d19eb213-492e-4ca4-a572-c1f74e9cda57	("[""2019-03-18 17:51:28.840173+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
236	855a79c4-88ab-4705-94e6-6f4e27782c6e	("[""2019-03-18 17:51:29.098079+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
237	3fd0e2d5-02cb-47d1-94cb-1b683324a8b5	("[""2019-03-18 17:51:29.111732+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
238	8e5dad7b-b0cf-4ea5-8e79-5305193a20df	("[""2019-03-18 17:51:29.125831+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
239	4a9368c3-609c-49df-be49-2cd7d4f2d623	("[""2019-03-18 17:51:29.140961+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
240	6710765d-21ca-4315-9065-9f5321d965ba	("[""2019-03-18 17:51:29.155326+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
241	9c006190-a6e3-4917-8277-4b9e345521e0	("[""2019-03-18 17:51:29.169035+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
242	a709f49e-0af2-4762-a3ec-daa1c148113f	("[""2019-03-18 17:51:29.662932+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
243	7af0d850-271a-4a68-8858-cb8ec0f41cfa	("[""2019-03-18 17:51:29.68183+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
244	85716ec9-058e-4b2e-8383-64bbbb36d4a9	("[""2019-03-18 17:51:29.69763+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
245	307c56e7-0c58-4158-ac40-0db72607579a	("[""2019-03-18 17:51:29.714928+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
246	898e01c0-5fc1-41ca-a2ad-530c5c886850	("[""2019-03-18 17:51:29.7332+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
247	2206a01d-f388-42f4-a2a7-4626c1ae298a	("[""2019-03-18 17:51:30.306443+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
248	bf392005-b539-4980-8701-b993b08ec7a2	("[""2019-03-18 17:51:30.323541+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
249	2bb34779-f334-4bef-b18c-5e180b1145e3	("[""2019-03-18 17:51:30.339099+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
250	4ce26c7e-3d35-4415-bfb2-56877c3a0e1b	("[""2019-03-18 17:51:30.354573+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
251	a0ef86b6-274b-4eed-89c2-d31387114991	("[""2019-03-18 17:51:30.371259+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
252	28dc863f-7023-4447-89a5-ee84a61758b1	("[""2019-03-18 17:51:30.388556+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
253	8d8fb7a3-216c-4445-b690-27e44f038812	("[""2019-03-18 17:51:30.404462+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
254	cab484ab-58f8-4404-8040-32d45bcaada2	("[""2019-03-18 17:51:30.908918+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
255	2c49067c-7f19-4349-b81a-951a6bcf2507	("[""2019-03-18 17:51:30.924772+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
256	c629775a-be9f-4033-b0ee-f295ae7f6f06	("[""2019-03-18 17:51:30.941089+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
257	b6e0b844-310a-40f7-be0f-56da171a7fef	("[""2019-03-18 17:51:30.956642+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
258	0fc5e796-6ca9-4d19-b3cd-c1ab437265b2	("[""2019-03-18 17:51:30.973061+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
259	4746ae6a-2586-4c77-8ce2-25503907752b	("[""2019-03-18 17:51:30.989284+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
260	6d5aa8c5-add2-4869-9585-3a402430ab1c	("[""2019-03-18 17:51:31.478839+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
261	094243c7-8076-448f-95fe-76b3aebb780d	("[""2019-03-18 17:51:31.501325+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
262	bfb716e1-c710-4e2d-a741-5225baaa0343	("[""2019-03-18 17:51:31.521157+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
263	68776545-e8f4-4101-b87b-0d972ddef30a	("[""2019-03-18 17:51:31.546107+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
264	4bc1b8b2-1670-4280-b022-fa585ae22a54	("[""2019-03-18 17:51:31.564124+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
265	297fbdfb-23ca-4d20-a668-ebfea10af56e	("[""2019-03-18 17:51:32.075596+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
266	535e687a-4a59-4c0f-9f2c-831b47b1f986	("[""2019-03-18 17:51:32.091432+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
267	9b4dcb58-d1ea-4ba1-b626-3cb2ba6f590d	("[""2019-03-18 17:51:32.107834+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
268	4f317790-7b23-4196-85a5-10454badec1f	("[""2019-03-18 17:51:32.122976+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
269	1cb94851-7e40-43a3-b3f0-0420d40ac9f9	("[""2019-03-18 17:51:32.138237+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
270	145c8c9f-58f4-4330-bd07-bfd55d662d02	("[""2019-03-18 17:51:32.155507+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
271	5546cf24-0f07-4355-94e5-ef17695ae2e4	("[""2019-03-18 17:51:32.628708+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
272	8dc22d1f-b012-4dc9-9813-72c8ef438419	("[""2019-03-18 17:51:32.644167+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
273	0546113b-f75f-49cd-a806-fbd275df6862	("[""2019-03-18 17:51:32.660225+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
274	cdf642df-f52b-4c50-985a-9b4e37e5d66f	("[""2019-03-18 17:51:32.675145+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
275	b3eab4cd-c0e3-454f-b7e4-7eef49f601b0	("[""2019-03-18 17:51:32.692831+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
276	6bacff47-9a47-4c44-8000-0d249887e0d3	("[""2019-03-18 17:51:33.22994+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
277	d3fd168d-72ad-4341-ab9d-a0a4c6c8cd16	("[""2019-03-18 17:51:33.246499+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
278	732f15de-0447-418f-94bd-9c7be187a908	("[""2019-03-18 17:51:33.262244+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
279	5923c73d-5ba3-4947-a81f-16fb7b17b638	("[""2019-03-18 17:51:33.280311+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
280	60fb673d-ff14-45dc-8470-930624cb3755	("[""2019-03-18 17:51:33.297565+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
281	c07a054c-f5ca-4f23-b9d0-85b025dc93b4	("[""2019-03-18 17:51:33.821141+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
282	982a8358-f9b4-474a-a40a-467c653a2215	("[""2019-03-18 17:51:33.83658+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
283	c6535003-7079-4f97-b2b5-823991255dc1	("[""2019-03-18 17:51:33.851978+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
284	310bdafa-b101-45ab-83ba-f139fa887bac	("[""2019-03-18 17:51:33.866419+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
285	37b89fc4-64dd-4c57-8a3c-f07e0d5c1cd1	("[""2019-03-18 17:51:33.881656+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
286	bbc51c27-1e23-4ce2-93e6-4aeeac530375	("[""2019-03-18 17:51:33.899001+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
287	dc2b7293-245c-4669-ac4f-02def27ba670	("[""2019-03-18 17:51:34.426283+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
288	cd44f85a-7b8b-41ee-8846-329ee3402ed5	("[""2019-03-18 17:51:34.441194+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
289	aa7f251a-8401-4bdb-b9f2-75f3cca2bf82	("[""2019-03-18 17:51:34.457277+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
290	1c80aa87-90bd-40f5-ba37-db97c849c171	("[""2019-03-18 17:51:34.472516+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
291	dfb9135d-5212-4147-8a09-4efdb35b2081	("[""2019-03-18 17:51:34.487185+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
292	4e74b325-8e38-4cf6-8618-0162acb01f8b	("[""2019-03-18 17:51:34.503926+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
293	1538a49f-aac2-4641-adc6-f472561c211c	("[""2019-03-18 17:51:35.090268+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
294	3d967f0e-4d32-4d04-93d6-d060f4f077e6	("[""2019-03-18 17:51:35.105028+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
295	dfb5502b-352f-4502-90c9-41c55a37512d	("[""2019-03-18 17:51:35.119171+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
296	74c48b26-c222-499b-bf2b-671881c8819a	("[""2019-03-18 17:51:35.132926+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
297	615c07eb-502c-4837-b68c-dff2480c3bbc	("[""2019-03-18 17:51:35.14767+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
298	80ca99e1-1add-4806-8782-9ac58ea54794	("[""2019-03-18 17:51:35.16291+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
299	121cd0d2-59f4-48f7-99a9-e8e73e1ce815	("[""2019-03-18 17:51:35.176987+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
300	47c9f266-cc0e-492e-97e4-d922d02c5cec	("[""2019-03-18 17:51:35.1914+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
301	d8c9c1e5-aa0d-42e1-ae8f-2b9022d6a99d	("[""2019-03-18 17:51:35.672859+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
302	c6d76039-204e-4f6e-8ffa-adb277d60571	("[""2019-03-18 17:51:35.687977+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
303	0d746257-0c4f-4d0a-8aa2-8388d7656029	("[""2019-03-18 17:51:35.702347+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
304	51cf4fd1-ef5f-45c0-9f1b-ce9e8bdfa215	("[""2019-03-18 17:51:35.716332+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
305	81f53951-dabc-42ee-b1a7-91f0e57c5aa1	("[""2019-03-18 17:51:35.730428+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
306	a3732137-a3c0-4a59-b1bb-67f532e09648	("[""2019-03-18 17:51:35.744482+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
307	e4db92f9-73e7-4b51-89b2-d590deda6f55	("[""2019-03-18 17:51:35.757732+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
308	6ab4d2de-c4a0-4efc-8961-0b0ec1c854b0	("[""2019-03-18 17:51:35.771326+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
309	c5501129-6861-4aa5-8111-3a08e80019de	("[""2019-03-18 17:51:36.229139+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
310	d58b7258-1c60-41f4-ba9f-e6106e9f8a0a	("[""2019-03-18 17:51:36.244189+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
311	31d1647e-49b8-42f4-abc6-e9241aeb2668	("[""2019-03-18 17:51:36.258981+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
312	73b1ffc7-b1f9-47f3-a4df-b997d3191db1	("[""2019-03-18 17:51:36.272711+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
313	9acb200b-1b4f-4d47-ad53-a7e54e3e3098	("[""2019-03-18 17:51:36.289304+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
314	713d2ffb-de4a-4f7e-90cc-9527a949653a	("[""2019-03-18 17:51:36.761461+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
315	4c2c4d3c-110c-467d-a644-27e0d5c707bd	("[""2019-03-18 17:51:36.775584+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
316	a3a47927-fe3b-4b95-8534-1a474d7c0c9d	("[""2019-03-18 17:51:36.791489+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
317	4b6878c6-7b91-4e31-8da9-c6d16ecbbc72	("[""2019-03-18 17:51:36.806943+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
318	4eb08260-01db-4573-98d2-2bdc12abe0b9	("[""2019-03-18 17:51:36.820811+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
319	2337d27e-5057-42c7-b7f3-dbc05a7061d3	("[""2019-03-18 17:51:36.836929+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
320	96e41147-f345-4124-a4d3-28c6633f190d	("[""2019-03-18 17:51:37.307688+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
321	35731ee9-f8c8-4b48-b86f-338092dbfa9f	("[""2019-03-18 17:51:37.321755+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
322	4847dc8a-db5a-4793-9762-d4a351598150	("[""2019-03-18 17:51:37.335515+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
323	7dfb22f6-ef3c-4023-9d27-0f1226d703ab	("[""2019-03-18 17:51:37.351188+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
324	53f83ba4-2c7f-4aca-8d09-81d432f66d00	("[""2019-03-18 17:51:37.366631+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
325	24fd0191-cb4c-4925-b922-210cbae217ae	("[""2019-03-18 17:51:37.381375+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
326	2570ea4f-7ee9-4880-af7c-4334c4ac63f9	("[""2019-03-18 17:51:37.844875+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
327	48be9199-2810-4ee9-9e07-28c66246a199	("[""2019-03-18 17:51:37.858327+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
328	8e5a1d40-55de-4f61-866c-6223f571a266	("[""2019-03-18 17:51:37.872578+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
329	f86a5e1c-050f-4f8b-a031-f9a82e51d86b	("[""2019-03-18 17:51:37.887564+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
330	f1581c1a-ae6c-47bb-b528-44aa6194e5fb	("[""2019-03-18 17:51:37.900936+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
331	033b6c50-9176-4783-b4ba-cd24e25ace5c	("[""2019-03-18 17:51:37.915168+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
332	ddbca8d8-87b1-4c54-9c3a-359613d56305	("[""2019-03-18 17:51:37.93024+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
333	f5d52d9e-6fff-481a-8e6f-605d7080cc71	("[""2019-03-18 17:51:38.393489+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
334	8abe95bd-51d4-4232-bb83-1b93b0b99fc6	("[""2019-03-18 17:51:38.408587+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
335	9c00ed66-83b7-432d-9458-0fb164a536be	("[""2019-03-18 17:51:38.424+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
336	95e2cdbb-4c44-4ea8-9b6f-a47ba43354a7	("[""2019-03-18 17:51:38.43929+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
337	81d32829-11e8-45a9-a83c-9a26003a5b50	("[""2019-03-18 17:51:38.453435+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
338	fc02c4c9-9d61-464a-bca7-47e34a78acaf	("[""2019-03-18 17:51:38.467162+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
339	adf8126c-f994-4a85-b56d-05088d61e4a7	("[""2019-03-18 17:51:38.902976+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
340	057fe9ca-bb23-44e9-bb58-903c3f414617	("[""2019-03-18 17:51:38.917973+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
341	3e2d1190-6bf5-4242-b500-f6e8c8fcda53	("[""2019-03-18 17:51:38.932648+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
342	bafc0397-5231-40cd-b4c9-eb8e475fa3d7	("[""2019-03-18 17:51:38.94606+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
343	fc4b7bf8-a6c2-462e-91c4-835a338ff653	("[""2019-03-18 17:51:38.960445+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
344	dc082e95-d86a-4128-a96e-5859abb72e4d	("[""2019-03-18 17:51:39.472985+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
345	7ed5afa1-00ae-4b9a-be02-fd714a7a273f	("[""2019-03-18 17:51:39.487934+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
346	ce2e615e-f995-4e5c-8aea-7749b4019743	("[""2019-03-18 17:51:39.50176+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
347	c9a769e4-695d-4b6c-9eb4-1da5705fbe6e	("[""2019-03-18 17:51:39.516622+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
348	1ad699a6-4cf9-4a0b-8733-1326a6213b4f	("[""2019-03-18 17:51:39.530881+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
349	9e6bd481-abbd-4f06-893d-d7ad55269b8a	("[""2019-03-18 17:51:39.545819+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
350	ec5a69c6-d485-4e34-9c27-7ce2a28d60f4	("[""2019-03-18 17:51:39.559579+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
351	8e78c287-b0ee-4754-9ce4-5c122dd0cc12	("[""2019-03-18 17:51:39.574918+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
352	c93cbb7c-a6de-4e45-b313-2c8002ff1864	("[""2019-03-18 17:51:40.107404+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
353	e23981db-2be0-4d5d-a100-d8f260e7f515	("[""2019-03-18 17:51:40.121045+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
354	49801f11-38cb-4af9-9c7c-5428eed1d671	("[""2019-03-18 17:51:40.135201+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
355	bf7651e7-5c80-45c5-959e-6cf7c32d967a	("[""2019-03-18 17:51:40.149597+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
356	df3eaeb4-7631-46bc-b883-9d157e820d2a	("[""2019-03-18 17:51:40.167111+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
357	e21d65e8-5da6-476c-8d17-bcf6ab24b126	("[""2019-03-18 17:51:40.628825+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
358	260d4a19-142c-401e-a7c1-e664cb3ceeff	("[""2019-03-18 17:51:40.642804+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
359	8ce225c1-26d6-4cac-b5d1-2fa4908b1556	("[""2019-03-18 17:51:40.658729+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
360	e8189268-1711-4f84-83e7-dd5afca58298	("[""2019-03-18 17:51:40.673957+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
361	54dea9b5-8e5b-4aaa-b45e-de3049360f35	("[""2019-03-18 17:51:40.687238+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
362	c882d54d-f185-437b-9d64-c6e2a08cfd05	("[""2019-03-18 17:51:40.700804+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
363	f63cb3dc-1c1d-45de-a69e-3d47c3be927a	("[""2019-03-18 17:51:41.220641+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
364	0465128c-4ed7-4da0-b315-f3eaad6e2c64	("[""2019-03-18 17:51:41.234966+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
365	338500b4-4bb8-4347-9d4b-fc4a21ea8225	("[""2019-03-18 17:51:41.250451+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
366	9ab77d7e-f053-4247-ba07-5af407f67b12	("[""2019-03-18 17:51:41.264054+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
367	3bfca148-60ad-45b5-a146-495f27ad09d1	("[""2019-03-18 17:51:41.278125+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
368	dcb6152b-8572-47f9-9eff-caa85b19582b	("[""2019-03-18 17:51:41.292986+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
369	c709134e-42bc-4211-ae28-a36707022646	("[""2019-03-18 17:51:41.306419+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
370	8ab5989c-07df-4def-ab1e-ff3acee30b7c	("[""2019-03-18 17:51:41.32106+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
371	2b683821-e03d-469a-a61b-172fb42eb845	("[""2019-03-18 17:51:41.781484+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
372	ff79e983-3440-472e-87f6-7209e40e9b4c	("[""2019-03-18 17:51:41.796377+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
373	5d9ee79f-3663-492f-832a-ab5a1f2f9fc7	("[""2019-03-18 17:51:41.811553+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
374	2e206b0c-be59-40f8-bd3e-c16bd82873ee	("[""2019-03-18 17:51:41.826725+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
375	d019d02c-2024-4760-9639-2af3c95608da	("[""2019-03-18 17:51:41.840521+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
376	c9e2d62f-2b9d-4b1a-ba4e-27e8460bcbb7	("[""2019-03-18 17:51:42.27756+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
377	0c4d9623-2826-42ad-af8f-bbae86aa4d86	("[""2019-03-18 17:51:42.292395+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
378	ad65677e-1aed-41c3-9d4e-89e05a85ace5	("[""2019-03-18 17:51:42.306717+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
379	79a88ad8-dae5-4a88-8a37-040b564a8031	("[""2019-03-18 17:51:42.321625+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
380	55e54eeb-1495-454e-b18a-1f4deeff9ec5	("[""2019-03-18 17:51:42.337343+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
381	54d406eb-4aed-4fd0-a7d1-da1ed18bc28f	("[""2019-03-18 17:51:42.805145+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
382	418b2b4f-a2b0-4c2e-90c4-0608080ef52c	("[""2019-03-18 17:51:42.819535+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
383	b8938cb0-82ec-405a-bf41-35667bdf4526	("[""2019-03-18 17:51:42.834289+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
384	9c242516-ec2c-4e1d-a604-8bd74a1f51d2	("[""2019-03-18 17:51:42.851158+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
385	2b3cf91e-6c52-4a34-8814-bf098ba1683d	("[""2019-03-18 17:51:42.869869+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
386	bcadbd18-d69a-4d87-8938-c022fccb8fa6	("[""2019-03-18 17:51:42.886169+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
387	3728c328-3dbc-4624-9abd-28a8aed0f75f	("[""2019-03-18 17:51:43.363545+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
388	6e5937f0-276b-415e-ad6d-844d39330a5b	("[""2019-03-18 17:51:43.391495+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
389	4fb2776a-0fea-4881-a249-910dc3168375	("[""2019-03-18 17:51:43.406627+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
390	09f102c7-4df3-481e-a9c2-5a0b8e388b51	("[""2019-03-18 17:51:43.422768+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
391	062362f3-44f0-462f-af2d-c1fb9e052f00	("[""2019-03-18 17:51:43.437291+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
392	7780c4f1-68b9-4b9b-92ea-f600203cc290	("[""2019-03-18 17:51:43.907234+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
393	b5a0882d-a45d-4004-be0c-1204191b83e4	("[""2019-03-18 17:51:43.92259+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
394	a0531228-c7a2-48c2-a017-20d8d321ef52	("[""2019-03-18 17:51:43.937989+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
395	502d2512-56b6-45d1-8766-3915ba48e476	("[""2019-03-18 17:51:43.952519+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
396	3c5e87ad-7c96-4a33-ba30-a979f5544695	("[""2019-03-18 17:51:43.966995+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
397	a2435035-38f8-4852-85b2-1f161b86d621	("[""2019-03-18 17:51:43.981421+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
398	764cfd89-aab9-4023-a6fb-8b5720bd7811	("[""2019-03-18 17:51:43.997841+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
399	1e665f2e-ba60-4da3-97ed-30012362ac81	("[""2019-03-18 17:51:44.442461+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
400	c13903ba-2164-439c-8285-6123cfe859ad	("[""2019-03-18 17:51:44.45594+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
401	d40ff9b8-e262-40b5-a062-b83d46b4d3e5	("[""2019-03-18 17:51:44.469019+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
402	c56a35d0-899f-4041-8e9c-a1f0862c6c8e	("[""2019-03-18 17:51:44.482959+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
403	ec88e050-093e-4a60-a902-56405da5c445	("[""2019-03-18 17:51:44.496803+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
404	8b111e02-4a90-4d78-ac6a-6513e9181fe8	("[""2019-03-18 17:51:44.509915+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
405	04434e17-a76b-47cc-bd81-0ae5d347591f	("[""2019-03-18 17:51:45.007358+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
406	3c4df1f7-907d-40d5-9ea1-3014ac2f4099	("[""2019-03-18 17:51:45.024792+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
407	45f69ef0-f612-4c80-ace8-8a52bfe03c68	("[""2019-03-18 17:51:45.040481+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
408	99e3c87e-0d56-4161-96b6-ce9e4affd69f	("[""2019-03-18 17:51:45.055507+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
409	631c36d5-d40f-41fb-8ce3-b4a44e2a4c1d	("[""2019-03-18 17:51:45.071265+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
410	e1794985-4845-4f09-b807-0772e6bb5e94	("[""2019-03-18 17:51:45.085738+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
411	1ba305ce-8715-408a-a444-579ce34465c6	("[""2019-03-18 17:51:45.100193+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
412	bb21dd52-7eb8-4c25-a3cd-5c6bbafb75b2	("[""2019-03-18 17:51:45.116261+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
413	3a00b39b-f8aa-4651-a93e-76657b9e4379	("[""2019-03-18 17:51:45.582119+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
414	a0732504-b263-4e12-a30f-e83aaef55697	("[""2019-03-18 17:51:45.596258+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
415	ec43a614-e895-4142-8e3b-fc5feaadd466	("[""2019-03-18 17:51:45.610083+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
416	ecd0e09e-e4fa-4273-97a4-d67a0cae7744	("[""2019-03-18 17:51:45.625111+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
417	edf11db2-2eab-416a-82d8-ee62c0fd446a	("[""2019-03-18 17:51:45.638541+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
418	d8a936e5-caeb-4a9b-a3af-375ad253ce32	("[""2019-03-18 17:51:45.65484+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
419	1b4f0c26-5643-44d4-92e1-1cc5be8f202a	("[""2019-03-18 17:51:46.119402+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
420	0326836b-23ce-4311-83c3-cb0c260e136d	("[""2019-03-18 17:51:46.133046+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
421	f911bbf7-5a94-441f-bf9e-1adf8d2a36e2	("[""2019-03-18 17:51:46.147971+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
422	77075bd3-cb16-4231-96a4-5793a2d44ce7	("[""2019-03-18 17:51:46.162089+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
423	7cf6ed26-715c-4d27-94ea-e4fae25b96b9	("[""2019-03-18 17:51:46.176348+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
424	fe76785a-6796-4c69-9dad-2bf804ee560c	("[""2019-03-18 17:51:46.191269+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
425	1062dc0c-6205-4d68-8d6e-714ef4334f6c	("[""2019-03-18 17:51:46.205653+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
426	7c05c9fe-4a27-44fd-b361-4527b3f475d2	("[""2019-03-18 17:51:46.671196+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
427	44a1616f-cf00-4092-855a-69eba2ac63a0	("[""2019-03-18 17:51:46.685603+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
428	7863cc44-d192-42b2-b6ff-1fae09bfae13	("[""2019-03-18 17:51:46.705026+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
429	10e9ca74-c578-4306-b4ce-8085b74f01b9	("[""2019-03-18 17:51:46.71902+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
430	bf1c7108-1532-43ed-851b-1d5a3d782e67	("[""2019-03-18 17:51:46.732856+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
431	4a19c870-40a6-44c9-83ad-f1c119a295df	("[""2019-03-18 17:51:46.747381+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
432	d371da60-26d7-499a-b86d-84a509ef6d33	("[""2019-03-18 17:51:46.761643+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
433	45efbd21-7290-4aa8-91fb-fd5f0c3cfc7b	("[""2019-03-18 17:51:47.229327+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
434	dc356382-550c-44ec-bee6-5b0291e95761	("[""2019-03-18 17:51:47.243289+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
435	052fc0d0-71f1-4686-b127-801261c2e6b6	("[""2019-03-18 17:51:47.258676+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
436	bf6b09d9-100e-400b-8513-1a95c3d03c5e	("[""2019-03-18 17:51:47.272892+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
437	e78ad8c5-c6c1-41f5-9f1e-59a915ddb796	("[""2019-03-18 17:51:47.288658+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
438	0ad88710-0666-4e7d-b6e8-22dc02a12426	("[""2019-03-18 17:51:47.303342+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
439	fdfd62ee-65a7-452d-8060-7dd1df0bf2e4	("[""2019-03-18 17:51:47.319123+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
440	d4118f21-5d3a-4964-a70c-8281841d89dc	("[""2019-03-18 17:51:47.789261+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
441	7763924c-1d4d-4d4d-9fc0-d7f0054e2e2a	("[""2019-03-18 17:51:47.803106+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
442	a80f9329-415f-40aa-a91a-cb4fdf4ec2a7	("[""2019-03-18 17:51:47.81842+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
443	318d1cce-8b70-401a-919a-6c524100c5a1	("[""2019-03-18 17:51:47.832906+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
444	8167bc7f-2119-455b-83c3-6669e3867d7f	("[""2019-03-18 17:51:47.846256+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
445	a4054184-b3ef-475b-944b-8d17e1b85e36	("[""2019-03-18 17:51:47.861087+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
446	cf2b4464-c5dd-41a6-9f60-13b03d0f2e64	("[""2019-03-18 17:51:47.875623+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
447	e5e24b08-dfb3-44b9-a528-17b05b8a1fc7	("[""2019-03-18 17:51:48.33426+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
448	10cb5cc4-6b36-4cea-8573-85627aef2b71	("[""2019-03-18 17:51:48.3502+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
449	ee56eddb-608f-4d9f-bbab-c4b8035d39ce	("[""2019-03-18 17:51:48.365049+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
450	aeeab338-488f-467a-ba68-c0e3a3bb0f4f	("[""2019-03-18 17:51:48.380888+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
451	a286d53b-0287-490e-a658-6853120d7b6c	("[""2019-03-18 17:51:48.395259+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
452	6fd6ff6e-7b97-4ae9-b4de-7417935cf815	("[""2019-03-18 17:51:48.409341+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
453	a73fb0e7-9605-484e-a43e-1ab0b574dd18	("[""2019-03-18 17:51:48.85169+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
454	56e85f74-96b8-48a9-bc02-956d54409772	("[""2019-03-18 17:51:48.866605+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
455	735d164e-8f7f-4e64-b0c8-33877970ac07	("[""2019-03-18 17:51:48.88107+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
456	6c43688a-fd08-401e-9586-40b73f90b32d	("[""2019-03-18 17:51:48.89562+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
457	d3094ca5-c684-4e4d-9995-5d2e8eb82db8	("[""2019-03-18 17:51:49.388569+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
458	b842d99d-55c5-4317-9e76-448f4be70bf6	("[""2019-03-18 17:51:49.406837+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
459	087bf6d7-87f2-47e3-a6cd-d214d0d3cd0a	("[""2019-03-18 17:51:49.421626+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
460	f274a473-2d50-40d9-8454-5f13099d9dcf	("[""2019-03-18 17:51:49.435585+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
461	1206bad8-00d3-456b-9301-8d20ad59339f	("[""2019-03-18 17:51:49.452276+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
462	bf1f7af6-a5c2-45a8-a693-edd9f4f4a25b	("[""2019-03-18 17:51:49.466683+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
463	2d5cfde2-353e-45d6-a9d8-fc73a5dacd73	("[""2019-03-18 17:51:49.483839+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
464	0be0f856-fc8e-4eda-a9b1-5b227aa22431	("[""2019-03-18 17:51:49.941136+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
465	fc9711de-c1ee-4e5c-b90d-8cc1565f17cf	("[""2019-03-18 17:51:49.955006+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
466	7690b372-ff59-4cee-a5d0-37d851cbf275	("[""2019-03-18 17:51:49.968682+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
467	28e2ec80-132e-4b9d-80df-17139669e58c	("[""2019-03-18 17:51:49.984867+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
468	936f60d0-69ec-4368-b8db-b0bd0a03608c	("[""2019-03-18 17:51:50.000072+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
469	96ddc0e4-3dc5-4d7c-8114-bb31958aa198	("[""2019-03-18 17:51:50.017702+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
470	e03cf98f-33ae-46d1-89bf-09d195b60b27	("[""2019-03-18 17:51:50.486095+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
471	b69a6887-9a37-478a-9838-1f4e0554fd3f	("[""2019-03-18 17:51:50.502035+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
472	82c8aaf1-c54e-468f-802c-05113325bfa3	("[""2019-03-18 17:51:50.517921+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
473	2db8bfd3-f2f0-4c3a-8e27-2b43af59ece5	("[""2019-03-18 17:51:50.535936+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
474	9ef47d22-44b8-4be3-a219-a7025dffb829	("[""2019-03-18 17:51:50.55211+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
475	dd739cdb-f0f7-453e-af98-6f7aa4913a4d	("[""2019-03-18 17:51:51.041502+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
476	348da62f-f4bd-4372-87e4-fdbdc086b79c	("[""2019-03-18 17:51:51.055156+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
477	eab2866c-0b7e-42a7-a018-19cd990e8745	("[""2019-03-18 17:51:51.069012+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
478	9751d191-5ee3-43bd-93ba-ec73bc451039	("[""2019-03-18 17:51:51.083026+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
479	1c00734f-5d62-4535-a3eb-23d97d923e1d	("[""2019-03-18 17:51:51.097876+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
480	5e61aa72-a2b6-4828-9c80-578859d2a6fe	("[""2019-03-18 17:51:51.112767+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
481	3b417eb4-9520-483a-8e0b-5634129fa439	("[""2019-03-18 17:51:51.129543+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
482	06b15b46-ad85-4500-b871-f2627cbc2029	("[""2019-03-18 17:51:51.592366+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
483	8db902c2-e3a0-4c75-92ef-2e614fc45392	("[""2019-03-18 17:51:51.606534+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
484	8393c18b-7294-4cbd-8940-1513408963b9	("[""2019-03-18 17:51:51.621025+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
485	05d27756-01a5-4522-8fa0-e835f7263b33	("[""2019-03-18 17:51:51.635696+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
486	ddec011a-0c08-423e-8fda-371b5e87b092	("[""2019-03-18 17:51:51.650033+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
487	03196ece-e0bc-4e50-95a4-7e716b7f8445	("[""2019-03-18 17:51:51.663517+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
488	6a3845ba-8aaf-4298-9bbd-a602a9a847b5	("[""2019-03-18 17:51:52.145199+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
489	9a1af9d5-ba66-4408-bf8b-47830146993e	("[""2019-03-18 17:51:52.160191+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
490	8bd605bb-4fc8-42d0-a227-9f04c9c5a1ad	("[""2019-03-18 17:51:52.175323+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
491	eebeb8ca-617c-4139-bc51-a9c9d35f83bb	("[""2019-03-18 17:51:52.189115+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
492	2981b04c-0055-422f-b905-ac62df22006e	("[""2019-03-18 17:51:52.203638+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
493	3053f9b9-f090-47bf-878e-7cee666892ed	("[""2019-03-18 17:51:52.218161+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
494	98f4f007-0121-46af-8f35-fec6ff88af67	("[""2019-03-18 17:51:52.231806+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
495	829f9eb5-8e03-4b74-a744-880016be5fc5	("[""2019-03-18 17:51:52.247171+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
496	457f32f3-1312-40e2-9c5a-96e337652d80	("[""2019-03-18 17:51:52.68066+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
497	b9fdd56c-7b41-4723-819f-387c623d7904	("[""2019-03-18 17:51:52.696121+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
498	ea860fef-b7be-4472-b008-883c0b477e6e	("[""2019-03-18 17:51:52.710267+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
499	8c15ffa3-0007-485f-ab3f-a3ec365b50c5	("[""2019-03-18 17:51:52.726036+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
500	ac7a29b3-5108-4f72-8465-a64f2e4731f0	("[""2019-03-18 17:51:52.740124+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
501	6aeb65f1-a19d-47e6-b8de-3c674fd1db3f	("[""2019-03-18 17:51:53.224773+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
502	9c924c79-d38d-4fe0-b119-acb376bf094b	("[""2019-03-18 17:51:53.239696+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
503	bf886fb8-88eb-4710-923b-9afbd8816373	("[""2019-03-18 17:51:53.255121+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
504	843a75ba-0ed2-4a2f-9a95-acdf1b4e4cad	("[""2019-03-18 17:51:53.270383+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
505	71a485e3-3e2b-4e3e-a324-fd193d26b06a	("[""2019-03-18 17:51:53.286156+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
506	fe8b4f30-5e46-413f-bd3f-d56a3f6243db	("[""2019-03-18 17:51:53.300709+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
507	48eddffb-9ba3-4ced-befe-7756e5fe3fb7	("[""2019-03-18 17:51:53.314347+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
508	e7b0e1ce-2b0f-4778-9756-81fb326efb5f	("[""2019-03-18 17:51:53.331428+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
509	bbe35033-a1bb-4329-9de0-0e309c646bb4	("[""2019-03-18 17:51:53.813507+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
510	38e8341b-ba05-44c5-af66-f3944427799e	("[""2019-03-18 17:51:53.827668+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
511	ac52f4c5-4355-4d7a-90ef-feb4fd993499	("[""2019-03-18 17:51:53.843403+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
512	1cee0c9b-99b5-4d3d-b860-5746a397174e	("[""2019-03-18 17:51:53.858523+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
513	e669466b-8322-475b-9d51-6a11b594b0ae	("[""2019-03-18 17:51:53.873699+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
514	8beab5d6-e00a-44f7-bb01-02496e746138	("[""2019-03-18 17:51:53.888996+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
515	903f448a-d0d0-41bc-9c7e-b847dd877f0f	("[""2019-03-18 17:51:53.906178+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
516	22e7759b-5541-4782-87b5-ab6a4fb077b4	("[""2019-03-18 17:51:54.381881+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
517	533c2c33-4d60-4f1b-9a55-b11cdc7370e4	("[""2019-03-18 17:51:54.396139+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
518	25421e59-f821-401e-bc5b-bfc351edb450	("[""2019-03-18 17:51:54.409979+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
519	3652d71a-9efb-485b-a655-7130ad2f088e	("[""2019-03-18 17:51:54.423772+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
520	be9a372d-cbcb-4b25-b9f4-54e30cfdd533	("[""2019-03-18 17:51:54.437072+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
521	8a723cb1-fb32-42a4-a6d2-d2d9ed06e27d	("[""2019-03-18 17:51:54.451045+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
522	d3042c5e-85e7-4e29-9d29-b79ddcb61485	("[""2019-03-18 17:51:54.467625+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
523	9965eeb8-6753-4997-85ab-6c5bcd5a6e91	("[""2019-03-18 17:51:54.964977+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
524	9cd27883-fe1a-4116-8412-6fcec884c2a1	("[""2019-03-18 17:51:54.980387+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
525	7a58216c-5dc7-44cf-bd1f-235203831985	("[""2019-03-18 17:51:54.995381+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
526	0f6b66bf-aecf-4b8d-b6cf-7c0b1df1a6a3	("[""2019-03-18 17:51:55.01112+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
527	c13b1283-99f3-43c1-a457-51ae7a572370	("[""2019-03-18 17:51:55.027456+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
528	aa69de99-ab86-4099-96e0-611ffed5bcfa	("[""2019-03-18 17:51:55.049352+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
529	fbd7a4f2-5562-45f6-9840-0dac1032542f	("[""2019-03-18 17:51:55.063868+01"",infinity)",Opstaaet,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
530	1d23ccc3-1c4e-4f34-ac95-fe3ac6eec0ea	("[""2019-03-18 17:51:55.080273+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Oprettet i MO")
\.


--
-- Data for Name: organisationfunktion_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion_attr_egenskaber (id, brugervendtnoegle, funktionsnavn, integrationsdata, virkning, organisationfunktion_registrering_id) FROM stdin;
1	Hjørringvej 371, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	1
2	Hjørringvej 371, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	2
3	Hjørringvej 371, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	3
4	info@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4
5	3218103075458	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5
6	4653558824	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	6
7	www.hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7
8	Søndergade 32D, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	8
9	Søndergade 32D, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9
10	Søndergade 32D, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	10
11	Borgmesterens_Afdeling@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	11
12	2165376605671	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	12
13	6437762214	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	13
14	Rødemøllevej 2, Mygdal, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	14
15	Rødemøllevej 2, Mygdal, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	15
16	Rødemøllevej 2, Mygdal, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	16
17	Teknik_og_Miljø@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	17
18	5350750122564	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	18
19	3050471608	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	19
20	Jernbanegade 5C, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	20
21	Jernbanegade 5B, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	21
22	Jernbanegade 5C, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	22
23	Skole_og_Børn@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	23
24	1274306278437	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	24
25	4115406076	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	25
26	Ørnevej 5, Furreby, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	26
27	Ørnevej 5, Furreby, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	27
28	Ørnevej 5, Furreby, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	28
29	Social_Indsats@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	29
30	8851082151745	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	30
31	3246175875	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	31
32	Bygning 18	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32
33	Erantisvej 4, Åbyen, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	33
34	Erantisvej 3, Åbyen, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	34
35	Erantisvej 4, Åbyen, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	35
36	IT-Support@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	36
37	5771402150873	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	37
38	5223645631	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	38
39	Bygning 14	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	39
40	Gadevænget 1, Hundelev, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	40
41	Gadevænget 1, Hundelev, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	41
42	Gadevænget 1, Hundelev, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	42
43	Skoler_og_børnehaver@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	43
44	7061806638260	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	44
45	2870620722	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	45
46	Søndergade 98, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	46
47	Søndergade 98, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	47
48	Søndergade 98, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	48
49	Hirtshals_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49
50	7452678516875	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	50
51	3812186457	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	51
52	Bygning 12	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	52
53	Nørrebro 16, 1. 3, 9881 Bindslev	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	53
54	Nørrebro 16, 1. 3, 9881 Bindslev	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	54
55	Nørrebro 16, 1. 3, 9881 Bindslev	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	55
56	Løkken_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	56
57	1701715645631	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	57
58	3383430245	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	58
59	Nygade 32, 9760 Vrå	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	59
60	Nygade 32, 9760 Vrå	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	60
61	Nygade 32, 9760 Vrå	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	61
62	Vrå_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	62
63	8047760787817	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	63
64	3486021253	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	64
65	Lærkestien 7, Furreby, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	65
66	Lærkestien 7, Furreby, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	66
67	Lærkestien 7, Furreby, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	67
68	Hjørring_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	68
69	4145364516030	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	69
70	2165015047	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	70
71	Marius Østergaardsvej 13, Tornby, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	71
72	Marius Østergaardsvej 13, Tornby, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	72
73	Marius Østergaardsvej 13, Tornby, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	73
74	Bindslev_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	74
75	7784600353664	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	75
76	7406840108	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	76
77	Baldersvej 2, 9870 Sindal	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	77
78	Baldersvej 2, 9870 Sindal	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	78
79	Baldersvej 2, 9870 Sindal	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	79
80	Sindal_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	80
81	7566517777540	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81
82	4758117533	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	82
83	Bygning 2	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	83
84	Erantisvej 21, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	84
85	Erantisvej 21, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	85
86	Erantisvej 21, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	86
87	Tårs_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	87
88	4712254653258	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	88
89	3601784246	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	89
90	Kornblomstvej 18, Tversted, 9881 Bindslev	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	90
91	Kornblomstvej 17, Tversted, 9881 Bindslev	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	91
92	Kornblomstvej 18, Tversted, 9881 Bindslev	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	92
93	Ålbæk_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	93
94	8257563878540	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	94
95	2452277631	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	95
96	Bygning 9	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	96
97	Elsagervej 10, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	97
98	Elsagervej 10, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	98
99	Elsagervej 10, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	99
100	Jerslev_J_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	100
101	8467411120832	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	101
102	2156770343	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	102
103	M Christensens Vej 56, Åsendrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	103
104	M Christensens Vej 56, Åsendrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	104
105	M Christensens Vej 56, Åsendrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	105
106	Frederikshavn_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	106
107	3460256107776	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	107
108	7842571326	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	108
109	Bygning 10	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	109
110	M Christensens Vej 50, Åsendrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	110
111	M Christensens Vej 50, Åsendrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	111
112	M Christensens Vej 50, Åsendrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	112
113	Østervrå_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	113
114	2841647807114	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	114
115	2004763507	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	115
116	Bjergevej 124, Ilbjerge, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	116
117	Bjergevej 124, Ilbjerge, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	117
118	Bjergevej 124, Ilbjerge, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	118
119	Social_og_sundhed@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	119
120	5518257836128	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	120
121	1371771152	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	121
122	Golfparken 58, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	122
123	Golfparken 58, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	123
124	Golfparken 58, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	124
125	info@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	125
126	6108444861761	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	126
127	6081870085	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	127
128	www.hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	128
129	Gl Byvej 1, Vidstrup, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	129
130	Gl Byvej 1, Vidstrup, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	130
131	Gl Byvej 1, Vidstrup, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	131
132	Borgmesterens_Afdeling@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	132
133	8051767870136	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	133
134	7375851080	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	134
135	Gammel Løkkensvej 5A, st. tv, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	135
136	Gammel Løkkensvej 5A, st. tv, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	136
137	Gammel Løkkensvej 5A, st. tv, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	137
138	Teknik_og_Miljø@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	138
139	8430000415430	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	139
140	3457323406	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	140
141	Bygning 11	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	141
142	Norgesgade 22, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	142
143	Norgesgade 22, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	143
144	Norgesgade 22, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	144
145	Skole_og_Børn@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	145
146	6665331688860	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	146
147	7816172235	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	147
148	Løkkensvej 708, Gølstrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	148
149	Løkkensvej 706, Gølstrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	149
150	Løkkensvej 708, Gølstrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	150
151	Social_Indsats@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	151
152	2533712583250	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	152
153	4334246831	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	153
154	Gl Skagensvej 3, Tversted, 9881 Bindslev	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	154
155	Gl Skolevej 17, Tornby, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	155
156	Gl Skagensvej 3, Tversted, 9881 Bindslev	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	156
157	IT-Support@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	157
158	6357240376816	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	158
159	6068155777	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	159
160	Kragevej 20, Tornby, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	160
161	Kragevej 20, Tornby, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	161
162	Kragevej 20, Tornby, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	162
163	Skoler_og_børnehaver@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	163
164	4551245384883	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	164
165	7684834157	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	165
166	Kærtoften 56, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	166
167	Kærtoften 56, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	167
168	Kærtoften 56, 9850 Hirtshals	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	168
169	Hirtshals_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	169
170	2266751346802	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	170
171	5306410511	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	171
172	Bygning 9	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	172
173	Havrenden 10A, Lønstrup, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	173
174	Havrenden 10A, Lønstrup, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	174
175	Havrenden 10A, Lønstrup, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	175
176	Løkken_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	176
177	1312835600764	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	177
178	6818802265	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	178
179	Blåklokkevej 8, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	179
180	Blåklokkevej 8, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	180
181	Blåklokkevej 8, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	181
182	Vrå_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	182
183	2854437052358	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	183
184	3357112718	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	184
185	Æblelunden 32, Hjørring, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	185
186	Æblelunden 44, Hjørring, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	186
187	Æblelunden 32, Hjørring, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	187
188	Hjørring_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	188
189	8661302174534	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	189
190	7030172082	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	190
191	Birkevej 3, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	191
192	Birkevej 2, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	192
193	Birkevej 3, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	193
194	Bindslev_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	194
195	7303458435654	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	195
196	2764825287	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	196
197	Bygning 6	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	197
198	Frederikshavnsvej 82, Hjørring, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	198
199	Frederikshavnsvej 82, Hjørring, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	199
200	Frederikshavnsvej 82, Hjørring, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	200
201	Sindal_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	201
202	5868341213670	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	202
203	7231473140	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	203
204	Bygning 8	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	204
205	Revlingrenden 41, Lønstrup, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	205
206	Revlingrenden 41, Lønstrup, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	206
207	Revlingrenden 41, Lønstrup, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	207
208	Tårs_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	208
209	3150337558066	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	209
210	2704758558	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	210
211	Bygning 7	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	211
212	Bispevænget 60, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	212
213	Bispevænget 60, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	213
214	Bispevænget 60, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	214
215	Ålbæk_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	215
216	2684114821727	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	216
217	4878144603	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	217
218	Niels Winthers Vej 25, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	218
219	Niels Winthers Vej 24, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	219
220	Niels Winthers Vej 25, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	220
221	Jerslev_J_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	221
222	6088022144266	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	222
223	8433775124	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	223
224	Hornfisken 38, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	224
225	Hornfisken 37, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	225
226	Hornfisken 38, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	226
227	Frederikshavn_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	227
228	3506437271812	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	228
229	3870615254	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	229
230	Rugvænget 6, Bjergby, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	230
231	Rugvænget 6, Bjergby, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	231
232	Rugvænget 6, Bjergby, 9800 Hjørring	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	232
233	Østervrå_skole@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	233
234	3315432416426	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	234
235	1180253422	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	235
236	Sælvej 3, Ulstrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	236
237	Sælvej 3, Ulstrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	237
238	Sælvej 3, Ulstrup, 9480 Løkken	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	238
239	Social_og_sundhed@hjorring.dk	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	239
240	4758124563253	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	240
241	6454348314	Adresse	\N	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	241
242	8d85368f-c30f-47b0-af5e-c0502217c0e1	Engagement	\N	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	242
243	Toftegade 44, 2., 9800 Hjørring	Adresse	\N	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	243
244	+4566310746	Adresse	\N	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	244
245	duncanh@hjorring.dk	Adresse	\N	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	245
246	80a8f362-be0a-447f-bfd1-9b251358cf58	Leder	\N	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	246
247	a40888ce-5417-4377-9b19-c47b2878db90	Engagement	\N	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	247
248	Kjulvej 15B, Asdal, 9850 Hirtshals	Adresse	\N	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	248
249	+4588645643	Adresse	\N	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	249
250	ellenc@hjorring.dk	Adresse	\N	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	250
251	EllenC	IT-system	\N	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	251
252	EllenC	IT-system	\N	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	252
253	2eee0491-5fd2-415f-912b-a193d521409c	Leder	\N	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	253
254	c739e436-90d8-4781-9c80-d4f6c9251b44	Engagement	\N	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	254
255	Bispensgade 103, 9800 Hjørring	Adresse	\N	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	255
256	+4541147434	Adresse	\N	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	256
257	annesofiej@hjorring.dk	Adresse	\N	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	257
258	AnnesofieJ	IT-system	\N	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	258
259	0bb0a6ce-3e89-47d2-9ecb-20858db3a3c8	Leder	\N	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	259
260	6d99a2f7-96c9-4eda-9d6d-02d2d62fd78d	Engagement	\N	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	260
261	Løkkensvej 742, Sdr Rubjerg, 9480 Løkken	Adresse	\N	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	261
262	+4578063177	Adresse	\N	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	262
263	annaf@hjorring.dk	Adresse	\N	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	263
264	Bygning 12	Adresse	\N	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	264
265	41a6125c-4cd9-49bd-a7e8-f91dc3667601	Engagement	\N	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	265
266	Dalvej 7, 9800 Hjørring	Adresse	\N	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	266
267	+4528632657	Adresse	\N	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	267
268	bentem@hjorring.dk	Adresse	\N	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	268
269	efa52e33-1b2e-4b06-999f-fb5af8fdefdb 535ba446-d618-4e51-8dae-821d63e26560 Tilknytning	Tilknytning	\N	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	269
270	efa52e33-1b2e-4b06-999f-fb5af8fdefdb 9b7b3dde-16c9-4f88-87cc-e03aa5b4e709 Rolle	Rolle	\N	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	270
271	90a7cbb2-2118-421a-9708-aa4948bba894	Engagement	\N	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	271
272	Svendsvej 4, st., 9760 Vrå	Adresse	\N	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	272
273	+4522813653	Adresse	\N	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	273
274	jørnp@hjorring.dk	Adresse	\N	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	274
275	1391f291-2b82-4708-a893-1b4d6fdc8805	Leder	\N	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	275
276	49116667-59d3-4028-b165-28a5a399292e	Engagement	\N	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	276
277	Vester Hedevej 172, Hjørring, 9800 Hjørring	Adresse	\N	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	277
278	+4585316638	Adresse	\N	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	278
279	robertg@hjorring.dk	Adresse	\N	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	279
280	608a3e4f-e9ac-49f1-8c64-efb1b2338cd4 b6c11152-0645-4712-a207-ba2c53b391ab Tilknytning	Tilknytning	\N	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	280
281	8fe5d220-c46c-40cb-9fd5-8fb043df6819	Engagement	\N	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	281
282	M Christensens Vej 87, Åsendrup, 9480 Løkken	Adresse	\N	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	282
283	+4547520380	Adresse	\N	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	283
284	brians@hjorring.dk	Adresse	\N	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	284
285	BrianS	IT-system	\N	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	285
286	a1b22509-e6ce-4dd0-bff6-eed185f590bf	Leder	\N	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	286
287	f189eec2-cdeb-47e2-a4d3-78a77b2f75d0	Engagement	\N	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	287
288	Vendiavej 2H, st., 9800 Hjørring	Adresse	\N	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	288
289	+4538213146	Adresse	\N	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	289
290	betinnaj@hjorring.dk	Adresse	\N	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	290
291	BetinnaJ	IT-system	\N	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	291
292	78bb9fd5-2c03-4d6a-9ea8-86f1a9c667f1 9723ddfb-a309-5b93-ace1-5b88c8336a66 Rolle	Rolle	\N	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	292
293	b6a8499e-6ae7-4e1a-9a69-228703acc3c4	Engagement	\N	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	293
294	Skallerupvej 466, Sønderlev, 9800 Hjørring	Adresse	\N	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	294
295	+4548040822	Adresse	\N	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	295
296	dorritj@hjorring.dk	Adresse	\N	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	296
297	Bygning 1	Adresse	\N	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	297
298	DorritJ	IT-system	\N	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	298
299	DorritJ	IT-system	\N	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	299
300	29fda44c-0e49-47d7-b68a-3cd6831095ba d9f93150-f857-5197-bac0-d0182e165c4a Tilknytning	Tilknytning	\N	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	300
301	bb22736f-15fa-429f-950b-f02655ef1653	Engagement	\N	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	301
302	Halsagerstien 15, 9800 Hjørring	Adresse	\N	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	302
303	+4543774361	Adresse	\N	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	303
304	hjalmarj@hjorring.dk	Adresse	\N	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	304
305	Bygning 3	Adresse	\N	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	305
306	HjalmarJ	IT-system	\N	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	306
307	HjalmarJ	IT-system	\N	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	307
308	1d41c22d-7796-4266-a07f-65c430593bfe b1b87a57-600b-5c1d-80aa-fe0ffd609d29 Tilknytning	Tilknytning	\N	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	308
309	99dda5b7-c54d-44d2-ba3e-7cee8edcbbc1	Engagement	\N	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	309
310	Grethesvej 5, 9800 Hjørring	Adresse	\N	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	310
311	+4582736564	Adresse	\N	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	311
312	peterb@hjorring.dk	Adresse	\N	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	312
313	1b744866-8319-40dd-9082-e5d72ca1ef1e	Leder	\N	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	313
314	f0bde86d-4776-446a-a113-ccbe78c9d638	Engagement	\N	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	314
315	Kragebakken 7, Tornby, 9850 Hirtshals	Adresse	\N	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	315
316	+4545553360	Adresse	\N	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	316
317	kirstens@hjorring.dk	Adresse	\N	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	317
318	KirstenS	IT-system	\N	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	318
319	d52fd265-7c44-4a31-a436-2fa289569fd2	Leder	\N	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	319
320	b990cc50-d6df-4318-b320-6a9b4b17211d	Engagement	\N	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	320
321	Svanelundsvej 2A, 1. th, 9800 Hjørring	Adresse	\N	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	321
322	+4518764043	Adresse	\N	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	322
323	marieb@hjorring.dk	Adresse	\N	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	323
324	MarieB	IT-system	\N	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	324
325	15a22fde-b7ae-424a-be74-f198ad00d915 81d20630-a126-577a-a47e-7a21155117d2 Rolle	Rolle	\N	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	325
326	4e1f8d25-162a-4dfb-bc3f-3ded44ca2023	Engagement	\N	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	326
327	Danmarksgade 47, 9870 Sindal	Adresse	\N	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	327
328	+4523387054	Adresse	\N	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	328
329	børgeb@hjorring.dk	Adresse	\N	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	329
330	BørgeB	IT-system	\N	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	330
331	BørgeB	IT-system	\N	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	331
332	bb84d7fa-bc05-4466-9051-d1c6208650ad ff2afd49-0c26-556a-b01b-d2d6bd14a2af Rolle	Rolle	\N	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	332
333	c59c4301-9310-4498-b5ab-7d33feb48705	Engagement	\N	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	333
334	Bastholm Møllevej 285, 9760 Vrå	Adresse	\N	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	334
335	+4566602653	Adresse	\N	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	335
336	olej@hjorring.dk	Adresse	\N	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	336
337	d8084037-6f9d-46ad-889a-0408aa6309a7 5f03f259-598a-5a38-9cc1-36da20431f4b Tilknytning	Tilknytning	\N	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	337
338	d8084037-6f9d-46ad-889a-0408aa6309a7 ff2afd49-0c26-556a-b01b-d2d6bd14a2af Rolle	Rolle	\N	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	338
339	e9931689-aad2-4ed0-a23a-66ab0623a8cb	Engagement	\N	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	339
340	Lønstrupvej 20F, 1. tv, Lønstrup, 9800 Hjørring	Adresse	\N	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	340
341	+4553351434	Adresse	\N	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	341
342	karenh@hjorring.dk	Adresse	\N	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	342
343	KarenH	IT-system	\N	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	343
344	e14129a6-058f-4e92-a7cf-346bc6e876ed	Engagement	\N	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	344
345	Svinkløvvej 20, Skallerup, 9800 Hjørring	Adresse	\N	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	345
346	+4530324740	Adresse	\N	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	346
347	gustavk@hjorring.dk	Adresse	\N	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	347
348	Bygning 7	Adresse	\N	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	348
349	GustavK	IT-system	\N	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	349
350	GustavK	IT-system	\N	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	350
351	43195cdb-7d44-4646-85b9-1b4d1079511d	Leder	\N	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	351
352	bd0112a2-c80a-40d8-a6fb-f4813f89156a	Engagement	\N	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	352
353	Skelbækvej 53, 9800 Hjørring	Adresse	\N	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	353
354	+4551712528	Adresse	\N	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	354
355	jensl@hjorring.dk	Adresse	\N	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	355
356	a2648403-eb89-42d8-be09-45a4ec294b98	Leder	\N	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	356
357	ae0780ac-404e-45aa-9eee-fd249b84eac2	Engagement	\N	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	357
358	Vendelbogade 28, 9480 Løkken	Adresse	\N	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	358
359	+4551580882	Adresse	\N	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	359
360	birgitteh@hjorring.dk	Adresse	\N	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	360
361	BirgitteH	IT-system	\N	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	361
362	f5e05fc2-a484-4fb5-95d3-d9ba89adc52e ff2afd49-0c26-556a-b01b-d2d6bd14a2af Tilknytning	Tilknytning	\N	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	362
363	e15bc6f1-1d6e-4c49-b846-3dcd61e556f2	Engagement	\N	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	363
364	Kildevej 11, 9800 Hjørring	Adresse	\N	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	364
365	+4512735824	Adresse	\N	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	365
366	evac@hjorring.dk	Adresse	\N	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	366
367	EvaC	IT-system	\N	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	367
368	EvaC	IT-system	\N	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	368
369	9ff61686-1144-457b-b735-bf1871379cca 5f03f259-598a-5a38-9cc1-36da20431f4b Tilknytning	Tilknytning	\N	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	369
370	9ff61686-1144-457b-b735-bf1871379cca b1b87a57-600b-5c1d-80aa-fe0ffd609d29 Rolle	Rolle	\N	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	370
371	76f63217-db57-4a3e-9027-6c96b63c18b9	Engagement	\N	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	371
372	Toftagervej 43, 9850 Hirtshals	Adresse	\N	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	372
373	+4542345584	Adresse	\N	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	373
374	gunnern@hjorring.dk	Adresse	\N	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	374
375	3187c0db-9b0d-4368-b756-de018f9b6ef9 a6773531-6c0a-4c7b-b0e2-77992412b610 Tilknytning	Tilknytning	\N	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	375
376	fb95f345-1aa1-4660-a9a1-46e63473c514	Engagement	\N	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	376
377	Tangen 2, Lønstrup, 9800 Hjørring	Adresse	\N	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	377
378	+4545526262	Adresse	\N	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	378
379	aagej@hjorring.dk	Adresse	\N	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	379
380	936cb72e-dc1a-49a3-a297-e97f2d480195 1da5de09-b1a8-5952-987d-04e07a3ffd50 Rolle	Rolle	\N	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	380
381	3dd089ed-4e21-40af-be03-e62ba94bfe0d	Engagement	\N	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	381
382	Valmuevej 8, 9800 Hjørring	Adresse	\N	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	382
383	+4562685287	Adresse	\N	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	383
384	flemmingl@hjorring.dk	Adresse	\N	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	384
385	FlemmingL	IT-system	\N	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	385
386	9ba24315-f2b8-472c-9e7f-cd5ac40208dd	Leder	\N	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	386
387	aad26829-1dba-47c9-bf48-b27dd3e01b1a	Engagement	\N	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	387
388	Torvegade 5, 9870 Sindal	Adresse	\N	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	388
389	+4571651038	Adresse	\N	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	389
390	poulan@hjorring.dk	Adresse	\N	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	390
391	PoulaN	IT-system	\N	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	391
392	e0a7fa4f-962f-4253-b5bc-6b617fd2feae	Engagement	\N	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	392
393	Solbakkevej 10, 1., 9800 Hjørring	Adresse	\N	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	393
394	+4542285244	Adresse	\N	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	394
395	egonj@hjorring.dk	Adresse	\N	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	395
396	EgonJ	IT-system	\N	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	396
397	EgonJ	IT-system	\N	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	397
398	314d75d1-b80d-46a8-92a9-5bc8e45b114b	Leder	\N	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	398
399	bd2fce70-a189-4747-996d-e14b42b2aa70	Engagement	\N	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	399
400	Delfinvej 11, Lyngby, 9480 Løkken	Adresse	\N	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	400
401	+4555110434	Adresse	\N	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	401
402	pouls@hjorring.dk	Adresse	\N	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	402
403	PoulS	IT-system	\N	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	403
404	PoulS	IT-system	\N	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	404
405	e0197c94-98f4-445b-8322-4c0219072005	Engagement	\N	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	405
406	Mimersvej 4, 9870 Sindal	Adresse	\N	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	406
407	+4548351417	Adresse	\N	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	407
408	marthineh@hjorring.dk	Adresse	\N	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	408
409	MarthineH	IT-system	\N	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	409
410	MarthineH	IT-system	\N	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	410
411	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55 9723ddfb-a309-5b93-ace1-5b88c8336a66 Tilknytning	Tilknytning	\N	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	411
412	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55 5f03f259-598a-5a38-9cc1-36da20431f4b Rolle	Rolle	\N	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	412
413	dab82495-931c-4e6e-8a82-30adeeb969ba	Engagement	\N	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	413
414	Idræts Alle 33, st. th, 9800 Hjørring	Adresse	\N	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	414
415	+4555335753	Adresse	\N	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	415
416	madsr@hjorring.dk	Adresse	\N	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	416
417	MadsR	IT-system	\N	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	417
418	75463379-8a94-4b12-8fc9-bb7b7c4b46a9	Leder	\N	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	418
419	2ea6f4cc-3646-4da3-85d3-471e851ee81a	Engagement	\N	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	419
420	Keravavej 37, st. th, 9800 Hjørring	Adresse	\N	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	420
421	+4566607282	Adresse	\N	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	421
422	annej@hjorring.dk	Adresse	\N	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	422
423	AnneJ	IT-system	\N	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	423
424	23768c40-05bf-4d0d-b263-495750673b31 f06ee470-9f17-566f-acbe-e938112d46d9 Tilknytning	Tilknytning	\N	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	424
425	23768c40-05bf-4d0d-b263-495750673b31 f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92 Rolle	Rolle	\N	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	425
426	b3285318-1e4f-478a-a81a-49427768e32d	Engagement	\N	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	426
427	Nørregade 2A, st., 9870 Sindal	Adresse	\N	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	427
428	+4554628754	Adresse	\N	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	428
429	michaelw@hjorring.dk	Adresse	\N	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	429
430	Bygning 16	Adresse	\N	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	430
431	MichaelW	IT-system	\N	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	431
432	MichaelW	IT-system	\N	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	432
433	dc753b6b-4e69-42ec-91e4-81af5074974a	Engagement	\N	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	433
434	M Christensens Vej 16, Åsendrup, 9480 Løkken	Adresse	\N	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	434
435	+4526543580	Adresse	\N	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	435
436	helgaj@hjorring.dk	Adresse	\N	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	436
437	Bygning 12	Adresse	\N	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	437
438	HelgaJ	IT-system	\N	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	438
439	038f13fb-5d0a-4207-a002-34c563196d62	Leder	\N	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	439
440	9b2667ad-255c-4447-8486-2d3c04d00c90	Engagement	\N	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	440
441	Peter Andersensvej 1, 9850 Hirtshals	Adresse	\N	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	441
442	+4511280236	Adresse	\N	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	442
443	antons@hjorring.dk	Adresse	\N	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	443
444	AntonS	IT-system	\N	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	444
445	AntonS	IT-system	\N	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	445
446	139b917c-7135-4c26-847c-e13c9f871c87 f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92 Tilknytning	Tilknytning	\N	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	446
447	2ace09e5-9a85-4c9b-ad1f-77b488730dc6	Engagement	\N	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	447
448	Øster Kjulvej 23, Asdal, 9850 Hirtshals	Adresse	\N	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	448
449	+4532864148	Adresse	\N	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	449
450	annah@hjorring.dk	Adresse	\N	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	450
451	AnnaH	IT-system	\N	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	451
452	c0e5f7cf-66c7-41d4-8dcb-6137da5d2343 81760628-a69b-584c-baf0-42d217442082 Rolle	Rolle	\N	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	452
453	0b1faf05-695f-475c-a359-e5af7c1ab1b9	Engagement	\N	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	453
454	Sdr Alle 61, 9760 Vrå	Adresse	\N	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	454
455	+4573122501	Adresse	\N	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	455
456	karenj@hjorring.dk	Adresse	\N	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	456
457	cd1a7662-87bc-44da-8a6d-13557d867c94	Engagement	\N	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	457
458	Lyngbyvej 239U, 1., Lyngby, 9480 Løkken	Adresse	\N	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	458
459	+4521126756	Adresse	\N	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	459
460	almal@hjorring.dk	Adresse	\N	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	460
461	AlmaL	IT-system	\N	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	461
462	AlmaL	IT-system	\N	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	462
463	0ae6abd9-4788-457c-a30d-14fe88ab9826	Leder	\N	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	463
464	11e39360-448e-4c50-b4f9-cd37dda71d41	Engagement	\N	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	464
465	Hæstrupvej 97, Hæstrup, 9800 Hjørring	Adresse	\N	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	465
466	+4526672316	Adresse	\N	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	466
467	valborgn@hjorring.dk	Adresse	\N	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	467
468	Bygning 3	Adresse	\N	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	468
469	ValborgN	IT-system	\N	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	469
470	94fc152a-8777-4a04-b24d-23620ab29213	Engagement	\N	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	470
471	Nørregade 38, 9480 Løkken	Adresse	\N	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	471
472	+4530320700	Adresse	\N	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	472
473	tinac@hjorring.dk	Adresse	\N	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	473
474	de47b9c8-283f-4ea9-9bdf-0795eb5d6a50 a726fbe8-32aa-55d0-a1c2-cb42ac13d42c Rolle	Rolle	\N	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	474
475	41469958-8679-4c0f-9f99-5ab6a1c4ebfb	Engagement	\N	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	475
476	Gl Hirtshalsvej 37, Vidstrup, 9800 Hjørring	Adresse	\N	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	476
477	+4553317160	Adresse	\N	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	477
478	miep@hjorring.dk	Adresse	\N	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	478
479	MieP	IT-system	\N	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	479
480	MieP	IT-system	\N	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	480
481	3552d75e-8697-490a-ab2e-5953a634f72c	Leder	\N	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	481
482	8d6d6f19-1694-4262-b5b4-0ab387b3effc	Engagement	\N	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	482
483	Capt Rottbølls Vej 30, 9800 Hjørring	Adresse	\N	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	483
484	+4566437087	Adresse	\N	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	484
485	bc@hjorring.dk	Adresse	\N	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	485
486	BC	IT-system	\N	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	486
487	ba02c1bc-dd1d-4b04-8f6b-a6093d27a85e a726fbe8-32aa-55d0-a1c2-cb42ac13d42c Rolle	Rolle	\N	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	487
488	82f21bd3-431d-4b9b-932f-9890eaa67331	Engagement	\N	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	488
489	Buen 4, 1., Hjørring, 9800 Hjørring	Adresse	\N	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	489
490	+4555806405	Adresse	\N	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	490
491	ryans@hjorring.dk	Adresse	\N	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	491
492	Bygning 3	Adresse	\N	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	492
493	RyanS	IT-system	\N	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	493
494	0d2d249d-83ca-40f1-ac89-be7e246e7541 f06ee470-9f17-566f-acbe-e938112d46d9 Tilknytning	Tilknytning	\N	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	494
495	0d2d249d-83ca-40f1-ac89-be7e246e7541 d9f93150-f857-5197-bac0-d0182e165c4a Rolle	Rolle	\N	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	495
496	f46c2bcd-92d9-4e61-a4fa-123e2d10e962	Engagement	\N	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	496
497	Sverigesvej 1A, 1. tv, 9800 Hjørring	Adresse	\N	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	497
498	+4575106836	Adresse	\N	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	498
499	pallec@hjorring.dk	Adresse	\N	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	499
500	PalleC	IT-system	\N	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	500
501	188abcd8-8fac-455e-94b1-c24a57927ec6	Engagement	\N	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	501
502	Kystvejen 10C, st. 109, 9850 Hirtshals	Adresse	\N	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	502
503	+4551248232	Adresse	\N	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	503
504	edithe@hjorring.dk	Adresse	\N	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	504
505	Bygning 7	Adresse	\N	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	505
506	EdithE	IT-system	\N	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	506
507	EdithE	IT-system	\N	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	507
508	06651994-2815-46a3-bcac-03a06baaa580	Leder	\N	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	508
509	64210343-3f04-4388-9885-1c2feaf6da77	Engagement	\N	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	509
510	Vellingshøjvej 361F, 9800 Hjørring	Adresse	\N	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	510
511	+4550116172	Adresse	\N	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	511
512	jelvap@hjorring.dk	Adresse	\N	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	512
513	JelvaP	IT-system	\N	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	513
514	JelvaP	IT-system	\N	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	514
515	b371790b-408a-49c6-8211-1170245262ad	Leder	\N	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	515
516	8052f6f4-bef4-472c-bbee-48784fadf32c	Engagement	\N	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	516
517	N C Jensensgade 8, 9850 Hirtshals	Adresse	\N	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	517
518	+4515524258	Adresse	\N	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	518
519	elsec@hjorring.dk	Adresse	\N	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	519
520	ElseC	IT-system	\N	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	520
521	ElseC	IT-system	\N	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	521
522	15b087ec-1a7a-4adb-86db-55e4150c96f5	Leder	\N	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	522
523	f7d8dca4-35d3-468b-82a6-50a515fbbd20	Engagement	\N	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	523
524	Tørholmsvej 110A, 9800 Hjørring	Adresse	\N	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	524
525	+4517087512	Adresse	\N	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	525
526	mieh@hjorring.dk	Adresse	\N	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	526
527	Bygning 7	Adresse	\N	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	527
528	MieH	IT-system	\N	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	528
529	MieH	IT-system	\N	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	529
530	83a7e8de-c336-43ea-a42c-27b710c4d3f1	Leder	\N	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	530
\.


--
-- Name: organisationfunktion_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationfunktion_attr_egenskaber_id_seq', 530, true);


--
-- Data for Name: organisationfunktion_attr_udvidelser; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion_attr_udvidelser (id, "primær", virkning, organisationfunktion_registrering_id) FROM stdin;
\.


--
-- Name: organisationfunktion_attr_udvidelser_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationfunktion_attr_udvidelser_id_seq', 1, false);


--
-- Name: organisationfunktion_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationfunktion_registrering_id_seq', 530, true);


--
-- Data for Name: organisationfunktion_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion_relation (id, organisationfunktion_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2	1	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
3	1	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
4	1	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-16a0-32b8-e044-0003ba298018	adresser	DAR
5	2	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
6	2	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
7	2	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
8	2	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-16a0-32b8-e044-0003ba298018	adresser	DAR
9	3	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
10	3	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
11	3	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
12	3	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-16a0-32b8-e044-0003ba298018	adresser	DAR
13	4	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
14	4	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
15	4	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
16	4	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:info@hjorring.dk	adresser	EMAIL
17	5	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
18	5	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
19	5	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
20	5	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:3218103075458	adresser	EAN
21	6	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
22	6	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
23	6	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
24	6	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:4653558824	adresser	PNUMBER
25	7	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
26	7	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
27	7	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d4f8fc78-6ada-444b-9ea1-9fd671f266b9	\N	organisatoriskfunktionstype	\N
28	7	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:www:www.hjorring.dk	adresser	WWW
29	8	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
30	8	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b6c11152-0645-4712-a207-ba2c53b391ab	\N	tilknyttedeenheder	\N
31	8	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
32	8	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-ab53-32b8-e044-0003ba298018	adresser	DAR
33	9	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
34	9	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b6c11152-0645-4712-a207-ba2c53b391ab	\N	tilknyttedeenheder	\N
35	9	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
36	9	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-ab53-32b8-e044-0003ba298018	adresser	DAR
37	10	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
38	10	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b6c11152-0645-4712-a207-ba2c53b391ab	\N	tilknyttedeenheder	\N
39	10	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
40	10	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-ab53-32b8-e044-0003ba298018	adresser	DAR
41	11	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
42	11	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b6c11152-0645-4712-a207-ba2c53b391ab	\N	tilknyttedeenheder	\N
43	11	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
44	11	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Borgmesterens_Afdeling@hjorring.dk	adresser	EMAIL
45	12	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
46	12	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b6c11152-0645-4712-a207-ba2c53b391ab	\N	tilknyttedeenheder	\N
47	12	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
48	12	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:2165376605671	adresser	EAN
49	13	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
50	13	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b6c11152-0645-4712-a207-ba2c53b391ab	\N	tilknyttedeenheder	\N
51	13	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
52	13	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:6437762214	adresser	PNUMBER
53	14	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
54	14	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	23a2ace2-52ca-458d-bead-d1a42080579f	\N	tilknyttedeenheder	\N
55	14	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
56	14	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-37e7-32b8-e044-0003ba298018	adresser	DAR
57	15	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
58	15	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	23a2ace2-52ca-458d-bead-d1a42080579f	\N	tilknyttedeenheder	\N
59	15	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
60	15	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-37e7-32b8-e044-0003ba298018	adresser	DAR
61	16	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
62	16	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	23a2ace2-52ca-458d-bead-d1a42080579f	\N	tilknyttedeenheder	\N
63	16	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
64	16	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-37e7-32b8-e044-0003ba298018	adresser	DAR
65	17	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
66	17	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	23a2ace2-52ca-458d-bead-d1a42080579f	\N	tilknyttedeenheder	\N
67	17	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
68	17	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Teknik_og_Miljø@hjorring.dk	adresser	EMAIL
69	18	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
70	18	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	23a2ace2-52ca-458d-bead-d1a42080579f	\N	tilknyttedeenheder	\N
71	18	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
72	18	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:5350750122564	adresser	EAN
73	19	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
74	19	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	23a2ace2-52ca-458d-bead-d1a42080579f	\N	tilknyttedeenheder	\N
75	19	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
76	19	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:3050471608	adresser	PNUMBER
77	20	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
78	20	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	tilknyttedeenheder	\N
79	20	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
80	20	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-20c8-32b8-e044-0003ba298018	adresser	DAR
81	21	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
82	21	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	tilknyttedeenheder	\N
83	21	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
84	21	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-20c7-32b8-e044-0003ba298018	adresser	DAR
85	22	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
86	22	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	tilknyttedeenheder	\N
87	22	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
88	22	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-20c8-32b8-e044-0003ba298018	adresser	DAR
89	23	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
90	23	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	tilknyttedeenheder	\N
91	23	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
92	23	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Skole_og_Børn@hjorring.dk	adresser	EMAIL
93	24	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
94	24	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	tilknyttedeenheder	\N
95	24	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
96	24	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:1274306278437	adresser	EAN
97	25	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
98	25	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	tilknyttedeenheder	\N
99	25	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
100	25	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:4115406076	adresser	PNUMBER
101	26	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
102	26	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
103	26	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
104	26	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-b0ae-32b8-e044-0003ba298018	adresser	DAR
105	27	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
106	27	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
107	27	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
108	27	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-b0ae-32b8-e044-0003ba298018	adresser	DAR
109	28	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
110	28	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
111	28	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
112	28	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-b0ae-32b8-e044-0003ba298018	adresser	DAR
113	29	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
114	29	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
115	29	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
116	29	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Social_Indsats@hjorring.dk	adresser	EMAIL
117	30	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
118	30	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
119	30	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
120	30	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:8851082151745	adresser	EAN
121	31	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
122	31	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
123	31	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
124	31	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:3246175875	adresser	PNUMBER
125	32	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
126	32	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
127	32	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
128	32	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%2018	adresser	TEXT
129	33	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
130	33	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
131	33	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
132	33	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-e22d-32b8-e044-0003ba298018	adresser	DAR
133	34	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
134	34	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
135	34	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
136	34	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-e22c-32b8-e044-0003ba298018	adresser	DAR
137	35	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
138	35	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
139	35	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
140	35	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-e22d-32b8-e044-0003ba298018	adresser	DAR
141	36	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
142	36	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
143	36	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
144	36	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:IT-Support@hjorring.dk	adresser	EMAIL
145	37	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
146	37	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
147	37	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
148	37	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:5771402150873	adresser	EAN
149	38	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
150	38	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
151	38	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
152	38	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:5223645631	adresser	PNUMBER
153	39	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
154	39	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
155	39	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
156	39	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%2014	adresser	TEXT
157	40	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
158	40	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
159	40	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
160	40	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-9cd4-32b8-e044-0003ba298018	adresser	DAR
161	41	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
162	41	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
163	41	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
164	41	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-9cd4-32b8-e044-0003ba298018	adresser	DAR
165	42	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
166	42	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
167	42	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
168	42	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-9cd4-32b8-e044-0003ba298018	adresser	DAR
169	43	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
170	43	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
171	43	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
172	43	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Skoler_og_børnehaver@hjorring.dk	adresser	EMAIL
173	44	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
174	44	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
175	44	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
176	44	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:7061806638260	adresser	EAN
177	45	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
178	45	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
179	45	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
180	45	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:2870620722	adresser	PNUMBER
181	46	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
182	46	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
183	46	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
184	46	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:3193a8a3-7747-4bb5-b498-34cd8a260a6a	adresser	DAR
185	47	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
186	47	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
187	47	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
188	47	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:3193a8a3-7747-4bb5-b498-34cd8a260a6a	adresser	DAR
189	48	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
190	48	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
191	48	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
192	48	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:3193a8a3-7747-4bb5-b498-34cd8a260a6a	adresser	DAR
193	49	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
194	49	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
195	49	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
196	49	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Hirtshals_skole@hjorring.dk	adresser	EMAIL
197	50	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
198	50	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
199	50	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
200	50	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:7452678516875	adresser	EAN
201	51	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
202	51	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
203	51	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
204	51	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:3812186457	adresser	PNUMBER
205	52	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
206	52	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
207	52	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
208	52	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%2012	adresser	TEXT
209	53	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
210	53	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	95028aed-f341-57f9-b103-59f67e90cce6	\N	tilknyttedeenheder	\N
211	53	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
212	53	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-f2f5-32b8-e044-0003ba298018	adresser	DAR
213	54	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
214	54	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	95028aed-f341-57f9-b103-59f67e90cce6	\N	tilknyttedeenheder	\N
215	54	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
216	54	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-f2f5-32b8-e044-0003ba298018	adresser	DAR
217	55	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
218	55	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	95028aed-f341-57f9-b103-59f67e90cce6	\N	tilknyttedeenheder	\N
219	55	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
220	55	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-f2f5-32b8-e044-0003ba298018	adresser	DAR
221	56	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
222	56	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	95028aed-f341-57f9-b103-59f67e90cce6	\N	tilknyttedeenheder	\N
223	56	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
224	56	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Løkken_skole@hjorring.dk	adresser	EMAIL
225	57	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
226	57	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	95028aed-f341-57f9-b103-59f67e90cce6	\N	tilknyttedeenheder	\N
227	57	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
228	57	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:1701715645631	adresser	EAN
229	58	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
230	58	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	95028aed-f341-57f9-b103-59f67e90cce6	\N	tilknyttedeenheder	\N
231	58	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
232	58	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:3383430245	adresser	PNUMBER
233	59	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
234	59	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81d20630-a126-577a-a47e-7a21155117d2	\N	tilknyttedeenheder	\N
235	59	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
236	59	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a624-32b8-e044-0003ba298018	adresser	DAR
237	60	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
238	60	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81d20630-a126-577a-a47e-7a21155117d2	\N	tilknyttedeenheder	\N
239	60	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
240	60	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a624-32b8-e044-0003ba298018	adresser	DAR
241	61	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
242	61	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81d20630-a126-577a-a47e-7a21155117d2	\N	tilknyttedeenheder	\N
243	61	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
244	61	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a624-32b8-e044-0003ba298018	adresser	DAR
245	62	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
246	62	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81d20630-a126-577a-a47e-7a21155117d2	\N	tilknyttedeenheder	\N
247	62	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
248	62	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Vrå_skole@hjorring.dk	adresser	EMAIL
249	63	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
250	63	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81d20630-a126-577a-a47e-7a21155117d2	\N	tilknyttedeenheder	\N
251	63	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
252	63	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:8047760787817	adresser	EAN
253	64	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
254	64	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81d20630-a126-577a-a47e-7a21155117d2	\N	tilknyttedeenheder	\N
255	64	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
256	64	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:3486021253	adresser	PNUMBER
257	65	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
258	65	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
259	65	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
260	65	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a2e2-32b8-e044-0003ba298018	adresser	DAR
261	66	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
262	66	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
263	66	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
264	66	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a2e2-32b8-e044-0003ba298018	adresser	DAR
265	67	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
266	67	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
267	67	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
268	67	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a2e2-32b8-e044-0003ba298018	adresser	DAR
269	68	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
270	68	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
271	68	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
272	68	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Hjørring_skole@hjorring.dk	adresser	EMAIL
273	69	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
274	69	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
275	69	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
276	69	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:4145364516030	adresser	EAN
277	70	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
278	70	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
279	70	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
280	70	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:2165015047	adresser	PNUMBER
281	71	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
282	71	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
283	71	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
284	71	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:16d19f5b-f649-16bd-e044-0003ba298018	adresser	DAR
285	72	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
286	72	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
287	72	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
288	72	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:16d19f5b-f649-16bd-e044-0003ba298018	adresser	DAR
289	73	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
290	73	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
291	73	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
292	73	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:16d19f5b-f649-16bd-e044-0003ba298018	adresser	DAR
293	74	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
294	74	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
295	74	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
296	74	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Bindslev_skole@hjorring.dk	adresser	EMAIL
297	75	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
298	75	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
299	75	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
300	75	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:7784600353664	adresser	EAN
301	76	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
302	76	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
303	76	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
304	76	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:7406840108	adresser	PNUMBER
305	77	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
306	77	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
307	77	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
308	77	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-1208-32b8-e044-0003ba298018	adresser	DAR
309	78	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
310	78	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
311	78	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
312	78	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-1208-32b8-e044-0003ba298018	adresser	DAR
313	79	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
314	79	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
315	79	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
316	79	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-1208-32b8-e044-0003ba298018	adresser	DAR
317	80	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
318	80	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
319	80	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
320	80	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Sindal_skole@hjorring.dk	adresser	EMAIL
321	81	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
322	81	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
323	81	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
324	81	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:7566517777540	adresser	EAN
325	82	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
326	82	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
327	82	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
328	82	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:4758117533	adresser	PNUMBER
329	83	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
330	83	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
331	83	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
332	83	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%202	adresser	TEXT
333	84	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
334	84	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
335	84	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
336	84	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-0ed8-32b8-e044-0003ba298018	adresser	DAR
337	85	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
338	85	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
339	85	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
340	85	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-0ed8-32b8-e044-0003ba298018	adresser	DAR
341	86	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
342	86	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
343	86	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
344	86	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-0ed8-32b8-e044-0003ba298018	adresser	DAR
345	87	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
346	87	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
347	87	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
348	87	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Tårs_skole@hjorring.dk	adresser	EMAIL
349	88	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
350	88	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
351	88	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
352	88	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:4712254653258	adresser	EAN
353	89	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
354	89	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
355	89	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
356	89	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:3601784246	adresser	PNUMBER
357	90	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
358	90	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
359	90	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
360	90	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-eac8-32b8-e044-0003ba298018	adresser	DAR
361	91	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
362	91	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
363	91	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
364	91	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-eac7-32b8-e044-0003ba298018	adresser	DAR
365	92	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
366	92	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
367	92	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
368	92	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-eac8-32b8-e044-0003ba298018	adresser	DAR
369	93	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
370	93	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
371	93	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
372	93	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Ålbæk_skole@hjorring.dk	adresser	EMAIL
373	94	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
374	94	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
375	94	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
376	94	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:8257563878540	adresser	EAN
377	95	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
378	95	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
379	95	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
380	95	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:2452277631	adresser	PNUMBER
381	96	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
382	96	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
383	96	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
384	96	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%209	adresser	TEXT
385	97	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
386	97	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	485c8355-ac5e-57f1-b792-3dd5d1b1a0b4	\N	tilknyttedeenheder	\N
387	97	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
388	97	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-0e30-32b8-e044-0003ba298018	adresser	DAR
389	98	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
390	98	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	485c8355-ac5e-57f1-b792-3dd5d1b1a0b4	\N	tilknyttedeenheder	\N
391	98	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
392	98	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-0e30-32b8-e044-0003ba298018	adresser	DAR
393	99	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
394	99	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	485c8355-ac5e-57f1-b792-3dd5d1b1a0b4	\N	tilknyttedeenheder	\N
395	99	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
396	99	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-0e30-32b8-e044-0003ba298018	adresser	DAR
397	100	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
398	100	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	485c8355-ac5e-57f1-b792-3dd5d1b1a0b4	\N	tilknyttedeenheder	\N
399	100	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
400	100	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Jerslev_J_skole@hjorring.dk	adresser	EMAIL
401	101	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
402	101	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	485c8355-ac5e-57f1-b792-3dd5d1b1a0b4	\N	tilknyttedeenheder	\N
403	101	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
404	101	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:8467411120832	adresser	EAN
405	102	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
406	102	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	485c8355-ac5e-57f1-b792-3dd5d1b1a0b4	\N	tilknyttedeenheder	\N
407	102	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
408	102	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:2156770343	adresser	PNUMBER
409	103	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
410	103	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
411	103	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
412	103	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a441-32b8-e044-0003ba298018	adresser	DAR
413	104	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
414	104	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
415	104	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
416	104	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a441-32b8-e044-0003ba298018	adresser	DAR
417	105	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
418	105	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
419	105	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
420	105	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a441-32b8-e044-0003ba298018	adresser	DAR
421	106	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
422	106	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
423	106	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
424	106	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Frederikshavn_skole@hjorring.dk	adresser	EMAIL
425	107	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
426	107	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
427	107	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
428	107	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:3460256107776	adresser	EAN
429	108	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
430	108	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
431	108	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
432	108	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:7842571326	adresser	PNUMBER
433	109	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
434	109	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
435	109	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
436	109	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%2010	adresser	TEXT
437	110	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
438	110	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
439	110	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
440	110	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a43b-32b8-e044-0003ba298018	adresser	DAR
441	111	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
442	111	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
443	111	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
444	111	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a43b-32b8-e044-0003ba298018	adresser	DAR
445	112	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
446	112	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
447	112	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
448	112	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a43b-32b8-e044-0003ba298018	adresser	DAR
449	113	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
450	113	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
451	113	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
452	113	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Østervrå_skole@hjorring.dk	adresser	EMAIL
453	114	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
454	114	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
455	114	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
456	114	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:2841647807114	adresser	EAN
457	115	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
458	115	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
459	115	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
460	115	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:2004763507	adresser	PNUMBER
461	116	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
462	116	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a6773531-6c0a-4c7b-b0e2-77992412b610	\N	tilknyttedeenheder	\N
463	116	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
464	116	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-1266-32b8-e044-0003ba298018	adresser	DAR
465	117	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
466	117	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a6773531-6c0a-4c7b-b0e2-77992412b610	\N	tilknyttedeenheder	\N
467	117	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
468	117	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-1266-32b8-e044-0003ba298018	adresser	DAR
469	118	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
470	118	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a6773531-6c0a-4c7b-b0e2-77992412b610	\N	tilknyttedeenheder	\N
471	118	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
472	118	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-1266-32b8-e044-0003ba298018	adresser	DAR
473	119	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
474	119	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a6773531-6c0a-4c7b-b0e2-77992412b610	\N	tilknyttedeenheder	\N
475	119	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
476	119	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Social_og_sundhed@hjorring.dk	adresser	EMAIL
477	120	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
478	120	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a6773531-6c0a-4c7b-b0e2-77992412b610	\N	tilknyttedeenheder	\N
479	120	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
480	120	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:5518257836128	adresser	EAN
481	121	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
482	121	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a6773531-6c0a-4c7b-b0e2-77992412b610	\N	tilknyttedeenheder	\N
483	121	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
484	121	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:1371771152	adresser	PNUMBER
485	122	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
486	122	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	tilknyttedeenheder	\N
487	122	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
557	140	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
488	122	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-1560-32b8-e044-0003ba298018	adresser	DAR
489	123	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
490	123	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	tilknyttedeenheder	\N
491	123	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
492	123	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-1560-32b8-e044-0003ba298018	adresser	DAR
493	124	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
494	124	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	tilknyttedeenheder	\N
495	124	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
496	124	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-1560-32b8-e044-0003ba298018	adresser	DAR
497	125	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
498	125	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	tilknyttedeenheder	\N
499	125	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
500	125	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:info@hjorring.dk	adresser	EMAIL
501	126	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
502	126	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	tilknyttedeenheder	\N
503	126	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
504	126	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:6108444861761	adresser	EAN
505	127	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
506	127	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	tilknyttedeenheder	\N
507	127	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
508	127	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:6081870085	adresser	PNUMBER
509	128	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
510	128	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	fb2d158f-114e-5f67-8365-2c520cf10b58	\N	tilknyttedeenheder	\N
511	128	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d4f8fc78-6ada-444b-9ea1-9fd671f266b9	\N	organisatoriskfunktionstype	\N
512	128	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:www:www.hjorring.dk	adresser	WWW
513	129	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
514	129	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	089ab2d1-d89f-586e-b8f2-46c17d7be9c8	\N	tilknyttedeenheder	\N
515	129	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
516	129	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-e42e-32b8-e044-0003ba298018	adresser	DAR
517	130	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
518	130	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	089ab2d1-d89f-586e-b8f2-46c17d7be9c8	\N	tilknyttedeenheder	\N
519	130	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
520	130	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-e42e-32b8-e044-0003ba298018	adresser	DAR
521	131	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
522	131	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	089ab2d1-d89f-586e-b8f2-46c17d7be9c8	\N	tilknyttedeenheder	\N
523	131	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
524	131	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-e42e-32b8-e044-0003ba298018	adresser	DAR
525	132	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
526	132	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	089ab2d1-d89f-586e-b8f2-46c17d7be9c8	\N	tilknyttedeenheder	\N
527	132	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
528	132	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Borgmesterens_Afdeling@hjorring.dk	adresser	EMAIL
529	133	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
530	133	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	089ab2d1-d89f-586e-b8f2-46c17d7be9c8	\N	tilknyttedeenheder	\N
531	133	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
532	133	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:8051767870136	adresser	EAN
533	134	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
534	134	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	089ab2d1-d89f-586e-b8f2-46c17d7be9c8	\N	tilknyttedeenheder	\N
535	134	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
536	134	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:7375851080	adresser	PNUMBER
537	135	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
538	135	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	578b004e-3fdf-54ec-a3ac-3d8a6dbd7635	\N	tilknyttedeenheder	\N
539	135	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
540	135	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-1492-32b8-e044-0003ba298018	adresser	DAR
541	136	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
542	136	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	578b004e-3fdf-54ec-a3ac-3d8a6dbd7635	\N	tilknyttedeenheder	\N
543	136	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
544	136	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-1492-32b8-e044-0003ba298018	adresser	DAR
545	137	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
546	137	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	578b004e-3fdf-54ec-a3ac-3d8a6dbd7635	\N	tilknyttedeenheder	\N
547	137	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
548	137	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-1492-32b8-e044-0003ba298018	adresser	DAR
549	138	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
550	138	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	578b004e-3fdf-54ec-a3ac-3d8a6dbd7635	\N	tilknyttedeenheder	\N
551	138	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
552	138	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Teknik_og_Miljø@hjorring.dk	adresser	EMAIL
553	139	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
554	139	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	578b004e-3fdf-54ec-a3ac-3d8a6dbd7635	\N	tilknyttedeenheder	\N
555	139	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
556	139	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:8430000415430	adresser	EAN
558	140	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	578b004e-3fdf-54ec-a3ac-3d8a6dbd7635	\N	tilknyttedeenheder	\N
559	140	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
560	140	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:3457323406	adresser	PNUMBER
561	141	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
562	141	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	578b004e-3fdf-54ec-a3ac-3d8a6dbd7635	\N	tilknyttedeenheder	\N
563	141	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
564	141	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%2011	adresser	TEXT
565	142	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
566	142	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	832b9360-f294-5af2-a169-e12a4c7ad75e	\N	tilknyttedeenheder	\N
567	142	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
568	142	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-f299-32b8-e044-0003ba298018	adresser	DAR
569	143	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
570	143	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	832b9360-f294-5af2-a169-e12a4c7ad75e	\N	tilknyttedeenheder	\N
571	143	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
572	143	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-f299-32b8-e044-0003ba298018	adresser	DAR
573	144	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
574	144	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	832b9360-f294-5af2-a169-e12a4c7ad75e	\N	tilknyttedeenheder	\N
575	144	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
576	144	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-f299-32b8-e044-0003ba298018	adresser	DAR
577	145	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
578	145	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	832b9360-f294-5af2-a169-e12a4c7ad75e	\N	tilknyttedeenheder	\N
579	145	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
580	145	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Skole_og_Børn@hjorring.dk	adresser	EMAIL
581	146	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
582	146	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	832b9360-f294-5af2-a169-e12a4c7ad75e	\N	tilknyttedeenheder	\N
583	146	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
584	146	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:6665331688860	adresser	EAN
585	147	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
586	147	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	832b9360-f294-5af2-a169-e12a4c7ad75e	\N	tilknyttedeenheder	\N
587	147	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
588	147	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:7816172235	adresser	PNUMBER
589	148	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
590	148	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	759ffdf4-2fd0-5a9a-a1a4-3a0f8b6dc3f6	\N	tilknyttedeenheder	\N
591	148	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
592	148	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:d9ec504d-824d-4d3b-9e75-18a07ed02549	adresser	DAR
593	149	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
594	149	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	759ffdf4-2fd0-5a9a-a1a4-3a0f8b6dc3f6	\N	tilknyttedeenheder	\N
595	149	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
596	149	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a344-32b8-e044-0003ba298018	adresser	DAR
597	150	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
598	150	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	759ffdf4-2fd0-5a9a-a1a4-3a0f8b6dc3f6	\N	tilknyttedeenheder	\N
599	150	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
600	150	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:d9ec504d-824d-4d3b-9e75-18a07ed02549	adresser	DAR
601	151	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
602	151	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	759ffdf4-2fd0-5a9a-a1a4-3a0f8b6dc3f6	\N	tilknyttedeenheder	\N
603	151	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
604	151	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Social_Indsats@hjorring.dk	adresser	EMAIL
605	152	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
606	152	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	759ffdf4-2fd0-5a9a-a1a4-3a0f8b6dc3f6	\N	tilknyttedeenheder	\N
607	152	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
608	152	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:2533712583250	adresser	EAN
609	153	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
610	153	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	759ffdf4-2fd0-5a9a-a1a4-3a0f8b6dc3f6	\N	tilknyttedeenheder	\N
611	153	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
612	153	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:4334246831	adresser	PNUMBER
613	154	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
614	154	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	8cba51a7-44c7-5136-a842-cfdd9ff98f71	\N	tilknyttedeenheder	\N
615	154	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
616	154	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-e4b4-32b8-e044-0003ba298018	adresser	DAR
617	155	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
618	155	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	8cba51a7-44c7-5136-a842-cfdd9ff98f71	\N	tilknyttedeenheder	\N
619	155	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
620	155	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:71366e7e-5f27-42d7-8d2c-5dd38a199731	adresser	DAR
621	156	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
622	156	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	8cba51a7-44c7-5136-a842-cfdd9ff98f71	\N	tilknyttedeenheder	\N
623	156	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
624	156	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-e4b4-32b8-e044-0003ba298018	adresser	DAR
625	157	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
626	157	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	8cba51a7-44c7-5136-a842-cfdd9ff98f71	\N	tilknyttedeenheder	\N
627	157	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
628	157	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:IT-Support@hjorring.dk	adresser	EMAIL
629	158	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
630	158	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	8cba51a7-44c7-5136-a842-cfdd9ff98f71	\N	tilknyttedeenheder	\N
631	158	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
632	158	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:6357240376816	adresser	EAN
633	159	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
634	159	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	8cba51a7-44c7-5136-a842-cfdd9ff98f71	\N	tilknyttedeenheder	\N
635	159	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
636	159	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:6068155777	adresser	PNUMBER
637	160	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
638	160	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	tilknyttedeenheder	\N
639	160	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
640	160	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-eb6d-32b8-e044-0003ba298018	adresser	DAR
641	161	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
642	161	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	tilknyttedeenheder	\N
643	161	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
644	161	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-eb6d-32b8-e044-0003ba298018	adresser	DAR
645	162	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
646	162	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	tilknyttedeenheder	\N
647	162	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
648	162	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-eb6d-32b8-e044-0003ba298018	adresser	DAR
649	163	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
650	163	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	tilknyttedeenheder	\N
651	163	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
652	163	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Skoler_og_børnehaver@hjorring.dk	adresser	EMAIL
653	164	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
654	164	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	tilknyttedeenheder	\N
655	164	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
656	164	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:4551245384883	adresser	EAN
657	165	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
658	165	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f9071b5-5f56-5e5f-b052-7c8e8f27c3b6	\N	tilknyttedeenheder	\N
659	165	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
660	165	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:7684834157	adresser	PNUMBER
661	166	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
662	166	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4aa42032-4f7b-5872-845d-8b5447e8573e	\N	tilknyttedeenheder	\N
663	166	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
664	166	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-ed2d-32b8-e044-0003ba298018	adresser	DAR
665	167	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
666	167	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4aa42032-4f7b-5872-845d-8b5447e8573e	\N	tilknyttedeenheder	\N
667	167	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
668	167	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-ed2d-32b8-e044-0003ba298018	adresser	DAR
669	168	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
670	168	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4aa42032-4f7b-5872-845d-8b5447e8573e	\N	tilknyttedeenheder	\N
671	168	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
672	168	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-ed2d-32b8-e044-0003ba298018	adresser	DAR
673	169	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
674	169	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4aa42032-4f7b-5872-845d-8b5447e8573e	\N	tilknyttedeenheder	\N
675	169	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
676	169	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Hirtshals_skole@hjorring.dk	adresser	EMAIL
677	170	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
678	170	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4aa42032-4f7b-5872-845d-8b5447e8573e	\N	tilknyttedeenheder	\N
679	170	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
680	170	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:2266751346802	adresser	EAN
681	171	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
682	171	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4aa42032-4f7b-5872-845d-8b5447e8573e	\N	tilknyttedeenheder	\N
683	171	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
684	171	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:5306410511	adresser	PNUMBER
685	172	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
686	172	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4aa42032-4f7b-5872-845d-8b5447e8573e	\N	tilknyttedeenheder	\N
687	172	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
688	172	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%209	adresser	TEXT
689	173	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
690	173	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f3973ef-a7a0-5270-900b-a80eab2ad6f9	\N	tilknyttedeenheder	\N
691	173	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
692	173	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-1a44-32b8-e044-0003ba298018	adresser	DAR
693	174	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
694	174	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f3973ef-a7a0-5270-900b-a80eab2ad6f9	\N	tilknyttedeenheder	\N
695	174	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
696	174	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-1a44-32b8-e044-0003ba298018	adresser	DAR
697	175	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
698	175	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f3973ef-a7a0-5270-900b-a80eab2ad6f9	\N	tilknyttedeenheder	\N
699	175	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
700	175	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-1a44-32b8-e044-0003ba298018	adresser	DAR
701	176	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
702	176	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f3973ef-a7a0-5270-900b-a80eab2ad6f9	\N	tilknyttedeenheder	\N
703	176	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
704	176	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Løkken_skole@hjorring.dk	adresser	EMAIL
705	177	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
706	177	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f3973ef-a7a0-5270-900b-a80eab2ad6f9	\N	tilknyttedeenheder	\N
707	177	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
708	177	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:1312835600764	adresser	EAN
709	178	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
710	178	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	5f3973ef-a7a0-5270-900b-a80eab2ad6f9	\N	tilknyttedeenheder	\N
711	178	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
712	178	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:6818802265	adresser	PNUMBER
713	179	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
714	179	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c5d2f882-0112-5ffd-9071-6611ae8dda82	\N	tilknyttedeenheder	\N
715	179	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
716	179	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-070e-32b8-e044-0003ba298018	adresser	DAR
717	180	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
718	180	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c5d2f882-0112-5ffd-9071-6611ae8dda82	\N	tilknyttedeenheder	\N
719	180	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
720	180	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-070e-32b8-e044-0003ba298018	adresser	DAR
721	181	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
722	181	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c5d2f882-0112-5ffd-9071-6611ae8dda82	\N	tilknyttedeenheder	\N
723	181	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
724	181	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-070e-32b8-e044-0003ba298018	adresser	DAR
725	182	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
726	182	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c5d2f882-0112-5ffd-9071-6611ae8dda82	\N	tilknyttedeenheder	\N
727	182	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
728	182	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Vrå_skole@hjorring.dk	adresser	EMAIL
729	183	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
730	183	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c5d2f882-0112-5ffd-9071-6611ae8dda82	\N	tilknyttedeenheder	\N
731	183	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
732	183	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:2854437052358	adresser	EAN
733	184	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
734	184	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c5d2f882-0112-5ffd-9071-6611ae8dda82	\N	tilknyttedeenheder	\N
735	184	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
736	184	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:3357112718	adresser	PNUMBER
737	185	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
738	185	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c73aa72a-8eb3-51f5-9b1e-cdece77c554a	\N	tilknyttedeenheder	\N
739	185	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
740	185	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:2c92335c-9979-42fb-8c40-5e9c2c9073cd	adresser	DAR
741	186	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
742	186	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c73aa72a-8eb3-51f5-9b1e-cdece77c554a	\N	tilknyttedeenheder	\N
743	186	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
744	186	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:2902dd9e-4287-411a-ba7f-c7c66025c62d	adresser	DAR
745	187	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
746	187	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c73aa72a-8eb3-51f5-9b1e-cdece77c554a	\N	tilknyttedeenheder	\N
747	187	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
748	187	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:2c92335c-9979-42fb-8c40-5e9c2c9073cd	adresser	DAR
749	188	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
750	188	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c73aa72a-8eb3-51f5-9b1e-cdece77c554a	\N	tilknyttedeenheder	\N
751	188	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
752	188	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Hjørring_skole@hjorring.dk	adresser	EMAIL
753	189	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
754	189	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c73aa72a-8eb3-51f5-9b1e-cdece77c554a	\N	tilknyttedeenheder	\N
755	189	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
756	189	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:8661302174534	adresser	EAN
757	190	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
758	190	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	c73aa72a-8eb3-51f5-9b1e-cdece77c554a	\N	tilknyttedeenheder	\N
759	190	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
760	190	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:7030172082	adresser	PNUMBER
761	191	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
762	191	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4439ec5e-8daa-5d91-83d6-56874fb5b15b	\N	tilknyttedeenheder	\N
763	191	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
764	191	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-03d0-32b8-e044-0003ba298018	adresser	DAR
765	192	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
766	192	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4439ec5e-8daa-5d91-83d6-56874fb5b15b	\N	tilknyttedeenheder	\N
767	192	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
768	192	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-03cf-32b8-e044-0003ba298018	adresser	DAR
769	193	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
770	193	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4439ec5e-8daa-5d91-83d6-56874fb5b15b	\N	tilknyttedeenheder	\N
771	193	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
772	193	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-03d0-32b8-e044-0003ba298018	adresser	DAR
773	194	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
774	194	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4439ec5e-8daa-5d91-83d6-56874fb5b15b	\N	tilknyttedeenheder	\N
775	194	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
776	194	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Bindslev_skole@hjorring.dk	adresser	EMAIL
777	195	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
778	195	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4439ec5e-8daa-5d91-83d6-56874fb5b15b	\N	tilknyttedeenheder	\N
779	195	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
780	195	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:7303458435654	adresser	EAN
781	196	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
782	196	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4439ec5e-8daa-5d91-83d6-56874fb5b15b	\N	tilknyttedeenheder	\N
783	196	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
784	196	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:2764825287	adresser	PNUMBER
785	197	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
786	197	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4439ec5e-8daa-5d91-83d6-56874fb5b15b	\N	tilknyttedeenheder	\N
787	197	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
788	197	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%206	adresser	TEXT
789	198	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
790	198	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cb33dd08-3948-501c-9e3f-1cef17f7094f	\N	tilknyttedeenheder	\N
791	198	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
792	198	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-11d3-32b8-e044-0003ba298018	adresser	DAR
793	199	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
794	199	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cb33dd08-3948-501c-9e3f-1cef17f7094f	\N	tilknyttedeenheder	\N
795	199	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
796	199	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-11d3-32b8-e044-0003ba298018	adresser	DAR
797	200	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
798	200	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cb33dd08-3948-501c-9e3f-1cef17f7094f	\N	tilknyttedeenheder	\N
799	200	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
800	200	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-11d3-32b8-e044-0003ba298018	adresser	DAR
801	201	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
802	201	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cb33dd08-3948-501c-9e3f-1cef17f7094f	\N	tilknyttedeenheder	\N
803	201	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
804	201	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Sindal_skole@hjorring.dk	adresser	EMAIL
805	202	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
806	202	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cb33dd08-3948-501c-9e3f-1cef17f7094f	\N	tilknyttedeenheder	\N
807	202	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
808	202	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:5868341213670	adresser	EAN
809	203	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
810	203	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cb33dd08-3948-501c-9e3f-1cef17f7094f	\N	tilknyttedeenheder	\N
811	203	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
812	203	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:7231473140	adresser	PNUMBER
813	204	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
814	204	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cb33dd08-3948-501c-9e3f-1cef17f7094f	\N	tilknyttedeenheder	\N
815	204	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
816	204	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%208	adresser	TEXT
817	205	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
818	205	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	58b9cde5-6da2-59a8-aff6-0ec469c2da2a	\N	tilknyttedeenheder	\N
819	205	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
820	205	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-36d6-32b8-e044-0003ba298018	adresser	DAR
821	206	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
822	206	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	58b9cde5-6da2-59a8-aff6-0ec469c2da2a	\N	tilknyttedeenheder	\N
823	206	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
824	206	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-36d6-32b8-e044-0003ba298018	adresser	DAR
825	207	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
826	207	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	58b9cde5-6da2-59a8-aff6-0ec469c2da2a	\N	tilknyttedeenheder	\N
827	207	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
828	207	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-36d6-32b8-e044-0003ba298018	adresser	DAR
829	208	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
830	208	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	58b9cde5-6da2-59a8-aff6-0ec469c2da2a	\N	tilknyttedeenheder	\N
831	208	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
832	208	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Tårs_skole@hjorring.dk	adresser	EMAIL
833	209	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
834	209	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	58b9cde5-6da2-59a8-aff6-0ec469c2da2a	\N	tilknyttedeenheder	\N
835	209	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
836	209	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:3150337558066	adresser	EAN
837	210	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
838	210	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	58b9cde5-6da2-59a8-aff6-0ec469c2da2a	\N	tilknyttedeenheder	\N
839	210	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
840	210	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:2704758558	adresser	PNUMBER
841	211	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
842	211	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	58b9cde5-6da2-59a8-aff6-0ec469c2da2a	\N	tilknyttedeenheder	\N
843	211	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	714972ef-addf-43d3-8dd9-f81cad5316a3	\N	organisatoriskfunktionstype	\N
844	211	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%207	adresser	TEXT
845	212	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
846	212	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d58c17a4-3b85-56be-8ffc-7a0be4ffd6da	\N	tilknyttedeenheder	\N
847	212	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
848	212	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-05d9-32b8-e044-0003ba298018	adresser	DAR
849	213	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
850	213	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d58c17a4-3b85-56be-8ffc-7a0be4ffd6da	\N	tilknyttedeenheder	\N
851	213	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
852	213	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-05d9-32b8-e044-0003ba298018	adresser	DAR
853	214	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
854	214	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d58c17a4-3b85-56be-8ffc-7a0be4ffd6da	\N	tilknyttedeenheder	\N
855	214	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
856	214	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-05d9-32b8-e044-0003ba298018	adresser	DAR
857	215	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
858	215	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d58c17a4-3b85-56be-8ffc-7a0be4ffd6da	\N	tilknyttedeenheder	\N
859	215	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
860	215	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Ålbæk_skole@hjorring.dk	adresser	EMAIL
861	216	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
862	216	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d58c17a4-3b85-56be-8ffc-7a0be4ffd6da	\N	tilknyttedeenheder	\N
863	216	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
864	216	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:2684114821727	adresser	EAN
865	217	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
866	217	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d58c17a4-3b85-56be-8ffc-7a0be4ffd6da	\N	tilknyttedeenheder	\N
867	217	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
868	217	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:4878144603	adresser	PNUMBER
869	218	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
870	218	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9c64a7bc-b1ad-59c8-b6f1-ade9688dec0a	\N	tilknyttedeenheder	\N
871	218	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
872	218	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-2fc8-32b8-e044-0003ba298018	adresser	DAR
873	219	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
874	219	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9c64a7bc-b1ad-59c8-b6f1-ade9688dec0a	\N	tilknyttedeenheder	\N
875	219	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
876	219	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-2fc7-32b8-e044-0003ba298018	adresser	DAR
877	220	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
878	220	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9c64a7bc-b1ad-59c8-b6f1-ade9688dec0a	\N	tilknyttedeenheder	\N
879	220	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
880	220	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-2fc8-32b8-e044-0003ba298018	adresser	DAR
881	221	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
882	221	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9c64a7bc-b1ad-59c8-b6f1-ade9688dec0a	\N	tilknyttedeenheder	\N
883	221	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
884	221	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Jerslev_J_skole@hjorring.dk	adresser	EMAIL
885	222	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
886	222	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9c64a7bc-b1ad-59c8-b6f1-ade9688dec0a	\N	tilknyttedeenheder	\N
887	222	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
888	222	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:6088022144266	adresser	EAN
889	223	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
890	223	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	9c64a7bc-b1ad-59c8-b6f1-ade9688dec0a	\N	tilknyttedeenheder	\N
891	223	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
892	223	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:8433775124	adresser	PNUMBER
893	224	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
894	224	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	27c80741-19ae-5a0d-935e-b13d6d10e0c5	\N	tilknyttedeenheder	\N
895	224	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
896	224	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:374230b7-2042-51c5-e044-0003ba298018	adresser	DAR
897	225	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
898	225	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	27c80741-19ae-5a0d-935e-b13d6d10e0c5	\N	tilknyttedeenheder	\N
899	225	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
900	225	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:374230b7-2041-51c5-e044-0003ba298018	adresser	DAR
901	226	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
902	226	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	27c80741-19ae-5a0d-935e-b13d6d10e0c5	\N	tilknyttedeenheder	\N
903	226	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
904	226	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:374230b7-2042-51c5-e044-0003ba298018	adresser	DAR
905	227	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
906	227	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	27c80741-19ae-5a0d-935e-b13d6d10e0c5	\N	tilknyttedeenheder	\N
907	227	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
908	227	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Frederikshavn_skole@hjorring.dk	adresser	EMAIL
909	228	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
910	228	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	27c80741-19ae-5a0d-935e-b13d6d10e0c5	\N	tilknyttedeenheder	\N
911	228	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
912	228	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:3506437271812	adresser	EAN
913	229	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
914	229	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	27c80741-19ae-5a0d-935e-b13d6d10e0c5	\N	tilknyttedeenheder	\N
915	229	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
916	229	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:3870615254	adresser	PNUMBER
917	230	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
918	230	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	33264542-4103-5267-923e-a06661b342ef	\N	tilknyttedeenheder	\N
919	230	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
920	230	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-378d-32b8-e044-0003ba298018	adresser	DAR
921	231	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
922	231	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	33264542-4103-5267-923e-a06661b342ef	\N	tilknyttedeenheder	\N
923	231	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
924	231	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-378d-32b8-e044-0003ba298018	adresser	DAR
925	232	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
926	232	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	33264542-4103-5267-923e-a06661b342ef	\N	tilknyttedeenheder	\N
927	232	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
928	232	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-378d-32b8-e044-0003ba298018	adresser	DAR
929	233	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
930	233	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	33264542-4103-5267-923e-a06661b342ef	\N	tilknyttedeenheder	\N
931	233	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
932	233	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Østervrå_skole@hjorring.dk	adresser	EMAIL
933	234	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
934	234	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	33264542-4103-5267-923e-a06661b342ef	\N	tilknyttedeenheder	\N
935	234	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
936	234	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:3315432416426	adresser	EAN
937	235	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
938	235	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	33264542-4103-5267-923e-a06661b342ef	\N	tilknyttedeenheder	\N
939	235	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
940	235	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:1180253422	adresser	PNUMBER
941	236	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
942	236	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d3d5b6d1-c3ef-51e6-8d29-632587912c09	\N	tilknyttedeenheder	\N
943	236	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	49f1996b-8ea1-4c91-93f8-f3bcc0068e5c	\N	organisatoriskfunktionstype	\N
944	236	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-ab05-32b8-e044-0003ba298018	adresser	DAR
945	237	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
946	237	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d3d5b6d1-c3ef-51e6-8d29-632587912c09	\N	tilknyttedeenheder	\N
947	237	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	4f24c7f0-818d-415a-a5e2-6d1212bf2676	\N	organisatoriskfunktionstype	\N
948	237	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-ab05-32b8-e044-0003ba298018	adresser	DAR
949	238	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
950	238	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d3d5b6d1-c3ef-51e6-8d29-632587912c09	\N	tilknyttedeenheder	\N
951	238	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	a506d035-7c4b-4dfa-92d7-1dd1eb9c36be	\N	organisatoriskfunktionstype	\N
952	238	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-ab05-32b8-e044-0003ba298018	adresser	DAR
953	239	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
954	239	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d3d5b6d1-c3ef-51e6-8d29-632587912c09	\N	tilknyttedeenheder	\N
955	239	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	32c52c48-8110-4398-8f09-39758bff8eaa	\N	organisatoriskfunktionstype	\N
956	239	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:Social_og_sundhed@hjorring.dk	adresser	EMAIL
957	240	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
958	240	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d3d5b6d1-c3ef-51e6-8d29-632587912c09	\N	tilknyttedeenheder	\N
959	240	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	cd4774a0-b0a5-47ed-962a-945b97ff26ad	\N	organisatoriskfunktionstype	\N
960	240	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:ean:4758124563253	adresser	EAN
961	241	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
962	241	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	d3d5b6d1-c3ef-51e6-8d29-632587912c09	\N	tilknyttedeenheder	\N
963	241	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	598c94ca-d6fa-40e6-88bb-69075397fd9a	\N	organisatoriskfunktionstype	\N
964	241	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cvr:produktionsenhed:6454348314	adresser	PNUMBER
965	242	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
966	242	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	0327b1cc-ad1a-47f2-aa14-e7278a92251f	\N	tilknyttedebrugere	\N
967	242	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	b6c11152-0645-4712-a207-ba2c53b391ab	\N	tilknyttedeenheder	\N
968	242	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
969	242	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	7bfbb207-85a3-40d8-97da-03ad7a92b2e2	\N	opgaver	\N
970	243	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
971	243	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	0327b1cc-ad1a-47f2-aa14-e7278a92251f	\N	tilknyttedebrugere	\N
972	243	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
973	243	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	\N	urn:dar:0a3f50c8-4781-32b8-e044-0003ba298018	adresser	DAR
974	244	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
975	244	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	0327b1cc-ad1a-47f2-aa14-e7278a92251f	\N	tilknyttedebrugere	\N
976	244	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
977	244	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
978	244	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	\N	urn:magenta.dk:telefon:+4566310746	adresser	PHONE
979	245	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
980	245	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	0327b1cc-ad1a-47f2-aa14-e7278a92251f	\N	tilknyttedebrugere	\N
981	245	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
982	245	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	\N	urn:mailto:duncanh@hjorring.dk	adresser	EMAIL
983	246	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
984	246	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	0327b1cc-ad1a-47f2-aa14-e7278a92251f	\N	tilknyttedebrugere	\N
985	246	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	b6c11152-0645-4712-a207-ba2c53b391ab	\N	tilknyttedeenheder	\N
986	246	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
987	246	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
988	246	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	91f65ddc-5eda-4b63-b7bc-506871c76181	\N	opgaver	lederansvar
989	246	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	ea13a75a-2b7f-4b89-9ab4-dd7be5fcbd1e	\N	opgaver	lederansvar
990	246	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
991	247	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
992	247	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	fe6583da-3f63-43af-aeaa-e3cca9a5071f	\N	tilknyttedebrugere	\N
993	247	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	23a2ace2-52ca-458d-bead-d1a42080579f	\N	tilknyttedeenheder	\N
994	247	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
995	247	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	166929d8-a994-4f73-b8f1-a6eae9f9889f	\N	opgaver	\N
996	248	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
997	248	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	fe6583da-3f63-43af-aeaa-e3cca9a5071f	\N	tilknyttedebrugere	\N
998	248	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
999	248	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-e9d8-32b8-e044-0003ba298018	adresser	DAR
1000	249	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1001	249	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	fe6583da-3f63-43af-aeaa-e3cca9a5071f	\N	tilknyttedebrugere	\N
1002	249	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1003	249	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1004	249	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4588645643	adresser	PHONE
1005	250	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1006	250	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	fe6583da-3f63-43af-aeaa-e3cca9a5071f	\N	tilknyttedebrugere	\N
1007	250	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1008	250	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:ellenc@hjorring.dk	adresser	EMAIL
1009	251	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1010	251	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	fe6583da-3f63-43af-aeaa-e3cca9a5071f	\N	tilknyttedebrugere	\N
1011	251	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
1012	252	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1013	252	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	fe6583da-3f63-43af-aeaa-e3cca9a5071f	\N	tilknyttedebrugere	\N
1014	252	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	76015baa-c0e0-4fea-82c2-9941c68fa1cd	\N	tilknyttedeitsystemer	\N
1015	253	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1016	253	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	fe6583da-3f63-43af-aeaa-e3cca9a5071f	\N	tilknyttedebrugere	\N
1017	253	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	23a2ace2-52ca-458d-bead-d1a42080579f	\N	tilknyttedeenheder	\N
1018	253	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1019	253	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1020	253	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	861a977e-3490-4d73-b005-587af2532e1d	\N	opgaver	lederansvar
1021	253	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	ea13a75a-2b7f-4b89-9ab4-dd7be5fcbd1e	\N	opgaver	lederansvar
1022	253	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1023	254	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1024	254	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	0133916a-4449-4885-9db4-cea379af2d71	\N	tilknyttedebrugere	\N
1025	254	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
1026	254	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1027	254	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	ddc55bb7-7f76-4ff2-9c12-abb385cf28c5	\N	opgaver	\N
1028	255	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1029	255	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	0133916a-4449-4885-9db4-cea379af2d71	\N	tilknyttedebrugere	\N
1030	255	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1031	255	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	\N	urn:dar:0a3f50c8-0540-32b8-e044-0003ba298018	adresser	DAR
1032	256	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1033	256	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	0133916a-4449-4885-9db4-cea379af2d71	\N	tilknyttedebrugere	\N
1034	256	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1035	256	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1036	256	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	\N	urn:magenta.dk:telefon:+4541147434	adresser	PHONE
1037	257	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1038	257	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	0133916a-4449-4885-9db4-cea379af2d71	\N	tilknyttedebrugere	\N
1039	257	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1040	257	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	\N	urn:mailto:annesofiej@hjorring.dk	adresser	EMAIL
1041	258	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1042	258	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	0133916a-4449-4885-9db4-cea379af2d71	\N	tilknyttedebrugere	\N
1043	258	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	\N	tilknyttedeitsystemer	\N
1044	259	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1045	259	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	0133916a-4449-4885-9db4-cea379af2d71	\N	tilknyttedebrugere	\N
1046	259	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
1047	259	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1048	259	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1049	259	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	91f65ddc-5eda-4b63-b7bc-506871c76181	\N	opgaver	lederansvar
1050	259	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	9f833d6c-3611-49fe-b155-71a7ba1602a2	\N	opgaver	lederansvar
1051	259	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1052	260	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1053	260	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	39c885cd-3bdb-4861-9316-4b8b8cd3c835	\N	tilknyttedebrugere	\N
1054	260	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
1055	260	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1056	260	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	589dadde-f6a3-4ead-8dac-ba7252e5565c	\N	opgaver	\N
1057	261	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1058	261	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	39c885cd-3bdb-4861-9316-4b8b8cd3c835	\N	tilknyttedebrugere	\N
1059	261	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1060	261	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a35f-32b8-e044-0003ba298018	adresser	DAR
1061	262	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1062	262	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	39c885cd-3bdb-4861-9316-4b8b8cd3c835	\N	tilknyttedebrugere	\N
1063	262	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1064	262	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1065	262	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4578063177	adresser	PHONE
1066	263	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1067	263	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	39c885cd-3bdb-4861-9316-4b8b8cd3c835	\N	tilknyttedebrugere	\N
1068	263	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1069	263	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:annaf@hjorring.dk	adresser	EMAIL
1070	264	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1071	264	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	39c885cd-3bdb-4861-9316-4b8b8cd3c835	\N	tilknyttedebrugere	\N
1072	264	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	\N	organisatoriskfunktionstype	\N
1073	264	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%2012	adresser	TEXT
1074	265	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1075	265	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	efa52e33-1b2e-4b06-999f-fb5af8fdefdb	\N	tilknyttedebrugere	\N
1076	265	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
1077	265	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1078	265	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	12f83ab4-fffd-4aac-8464-2830eacdb506	\N	opgaver	\N
1079	266	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1080	266	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	efa52e33-1b2e-4b06-999f-fb5af8fdefdb	\N	tilknyttedebrugere	\N
1081	266	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1082	266	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	\N	urn:dar:0a3f50c8-0bff-32b8-e044-0003ba298018	adresser	DAR
1083	267	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1084	267	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	efa52e33-1b2e-4b06-999f-fb5af8fdefdb	\N	tilknyttedebrugere	\N
1085	267	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1086	267	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
1087	267	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	\N	urn:magenta.dk:telefon:+4528632657	adresser	PHONE
1088	268	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1089	268	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	efa52e33-1b2e-4b06-999f-fb5af8fdefdb	\N	tilknyttedebrugere	\N
1090	268	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1091	268	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	\N	urn:mailto:bentem@hjorring.dk	adresser	EMAIL
1092	269	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1093	269	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	efa52e33-1b2e-4b06-999f-fb5af8fdefdb	\N	tilknyttedebrugere	\N
1094	269	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	535ba446-d618-4e51-8dae-821d63e26560	\N	tilknyttedeenheder	\N
1095	269	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	a47e0a34-cc21-4ea8-8d2b-5398b7884ac5	\N	organisatoriskfunktionstype	\N
1096	270	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1097	270	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	efa52e33-1b2e-4b06-999f-fb5af8fdefdb	\N	tilknyttedebrugere	\N
1098	270	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
1099	270	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	5c074e78-724f-45af-9b78-8daddad60d57	\N	organisatoriskfunktionstype	\N
1100	271	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1101	271	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	bd910c76-5658-453a-9a7b-ba056c7dd561	\N	tilknyttedebrugere	\N
1102	271	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
1103	271	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1104	271	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	0c7f0826-ec4a-4daf-b08e-d6b34f690cc9	\N	opgaver	\N
1105	272	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1106	272	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	bd910c76-5658-453a-9a7b-ba056c7dd561	\N	tilknyttedebrugere	\N
1107	272	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1108	272	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	\N	urn:dar:0a3f50c8-aaf0-32b8-e044-0003ba298018	adresser	DAR
1109	273	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1110	273	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	bd910c76-5658-453a-9a7b-ba056c7dd561	\N	tilknyttedebrugere	\N
1111	273	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1112	273	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1113	273	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	\N	urn:magenta.dk:telefon:+4522813653	adresser	PHONE
1114	274	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1115	274	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	bd910c76-5658-453a-9a7b-ba056c7dd561	\N	tilknyttedebrugere	\N
1116	274	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1117	274	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	\N	urn:mailto:jørnp@hjorring.dk	adresser	EMAIL
1118	275	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1119	275	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	bd910c76-5658-453a-9a7b-ba056c7dd561	\N	tilknyttedebrugere	\N
1120	275	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
1121	275	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1122	275	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1123	275	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	01f89ef8-0651-43c2-afda-e24f0d8fe05b	\N	opgaver	lederansvar
1124	275	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	91f65ddc-5eda-4b63-b7bc-506871c76181	\N	opgaver	lederansvar
1125	275	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1126	276	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1127	276	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	608a3e4f-e9ac-49f1-8c64-efb1b2338cd4	\N	tilknyttedebrugere	\N
1128	276	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	9b7b3dde-16c9-4f88-87cc-e03aa5b4e709	\N	tilknyttedeenheder	\N
1129	276	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1130	276	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	4f5aad51-8c28-4c0d-9b17-a2a30df36849	\N	opgaver	\N
1131	277	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1132	277	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	608a3e4f-e9ac-49f1-8c64-efb1b2338cd4	\N	tilknyttedebrugere	\N
1133	277	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1134	277	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-4eb5-32b8-e044-0003ba298018	adresser	DAR
1135	278	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1136	278	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	608a3e4f-e9ac-49f1-8c64-efb1b2338cd4	\N	tilknyttedebrugere	\N
1137	278	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1138	278	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1139	278	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4585316638	adresser	PHONE
1140	279	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1141	279	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	608a3e4f-e9ac-49f1-8c64-efb1b2338cd4	\N	tilknyttedebrugere	\N
1142	279	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1143	279	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:robertg@hjorring.dk	adresser	EMAIL
1144	280	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1145	280	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	608a3e4f-e9ac-49f1-8c64-efb1b2338cd4	\N	tilknyttedebrugere	\N
1146	280	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	b6c11152-0645-4712-a207-ba2c53b391ab	\N	tilknyttedeenheder	\N
1147	280	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	68ce5504-54ec-474f-8fed-2709442e0c9b	\N	organisatoriskfunktionstype	\N
1148	281	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1149	281	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	25044a31-e4eb-4725-8dff-0ff8f032ae53	\N	tilknyttedebrugere	\N
1150	281	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
1151	281	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1152	281	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	d07ce76c-ed70-4b92-b419-84b948e17086	\N	opgaver	\N
1153	282	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1154	282	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	25044a31-e4eb-4725-8dff-0ff8f032ae53	\N	tilknyttedebrugere	\N
1155	282	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1156	282	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a454-32b8-e044-0003ba298018	adresser	DAR
1157	283	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1158	283	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	25044a31-e4eb-4725-8dff-0ff8f032ae53	\N	tilknyttedebrugere	\N
1159	283	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1160	283	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
1161	283	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4547520380	adresser	PHONE
1162	284	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1163	284	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	25044a31-e4eb-4725-8dff-0ff8f032ae53	\N	tilknyttedebrugere	\N
1164	284	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1165	284	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:brians@hjorring.dk	adresser	EMAIL
1166	285	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1167	285	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	25044a31-e4eb-4725-8dff-0ff8f032ae53	\N	tilknyttedebrugere	\N
1168	285	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
1169	286	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1170	286	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	25044a31-e4eb-4725-8dff-0ff8f032ae53	\N	tilknyttedebrugere	\N
1171	286	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
1172	286	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1173	286	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1174	286	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	861a977e-3490-4d73-b005-587af2532e1d	\N	opgaver	lederansvar
1175	286	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	91f65ddc-5eda-4b63-b7bc-506871c76181	\N	opgaver	lederansvar
1176	286	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1177	287	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1178	287	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	78bb9fd5-2c03-4d6a-9ea8-86f1a9c667f1	\N	tilknyttedebrugere	\N
1179	287	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
1180	287	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1181	287	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	f19417e6-1f70-442a-bfbf-2ad65397d84f	\N	opgaver	\N
1182	288	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1183	288	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	78bb9fd5-2c03-4d6a-9ea8-86f1a9c667f1	\N	tilknyttedebrugere	\N
1184	288	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1185	288	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	\N	urn:dar:581bd17a-4336-44e1-a9ef-3fb3fb26fb53	adresser	DAR
1186	289	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1187	289	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	78bb9fd5-2c03-4d6a-9ea8-86f1a9c667f1	\N	tilknyttedebrugere	\N
1188	289	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1189	289	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1190	289	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	\N	urn:magenta.dk:telefon:+4538213146	adresser	PHONE
1191	290	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1192	290	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	78bb9fd5-2c03-4d6a-9ea8-86f1a9c667f1	\N	tilknyttedebrugere	\N
1193	290	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1194	290	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	\N	urn:mailto:betinnaj@hjorring.dk	adresser	EMAIL
1195	291	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1196	291	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	78bb9fd5-2c03-4d6a-9ea8-86f1a9c667f1	\N	tilknyttedebrugere	\N
1197	291	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	76015baa-c0e0-4fea-82c2-9941c68fa1cd	\N	tilknyttedeitsystemer	\N
1198	292	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1199	292	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	78bb9fd5-2c03-4d6a-9ea8-86f1a9c667f1	\N	tilknyttedebrugere	\N
1200	292	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
1201	292	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	9b447ec7-81fb-46c8-8820-3447b8a93330	\N	organisatoriskfunktionstype	\N
1202	293	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1203	293	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	29fda44c-0e49-47d7-b68a-3cd6831095ba	\N	tilknyttedebrugere	\N
1204	293	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	95028aed-f341-57f9-b103-59f67e90cce6	\N	tilknyttedeenheder	\N
1205	293	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1206	293	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	86964252-7c92-4337-a59c-bd847865280b	\N	opgaver	\N
1207	294	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1208	294	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	29fda44c-0e49-47d7-b68a-3cd6831095ba	\N	tilknyttedebrugere	\N
1209	294	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1210	294	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-3c24-32b8-e044-0003ba298018	adresser	DAR
1211	295	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1212	295	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	29fda44c-0e49-47d7-b68a-3cd6831095ba	\N	tilknyttedebrugere	\N
1213	295	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1214	295	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
1215	295	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4548040822	adresser	PHONE
1216	296	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1217	296	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	29fda44c-0e49-47d7-b68a-3cd6831095ba	\N	tilknyttedebrugere	\N
1218	296	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1219	296	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:dorritj@hjorring.dk	adresser	EMAIL
1220	297	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1221	297	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	29fda44c-0e49-47d7-b68a-3cd6831095ba	\N	tilknyttedebrugere	\N
1222	297	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	\N	organisatoriskfunktionstype	\N
1223	297	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%201	adresser	TEXT
1224	298	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1225	298	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	29fda44c-0e49-47d7-b68a-3cd6831095ba	\N	tilknyttedebrugere	\N
1226	298	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
1227	299	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1228	299	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	29fda44c-0e49-47d7-b68a-3cd6831095ba	\N	tilknyttedebrugere	\N
1229	299	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	20b507cf-fdeb-4123-8da4-db4a15524398	\N	tilknyttedeitsystemer	\N
1230	300	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1231	300	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	29fda44c-0e49-47d7-b68a-3cd6831095ba	\N	tilknyttedebrugere	\N
1232	300	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
1233	300	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	5b03a02c-a698-4c40-a530-d5578b142283	\N	organisatoriskfunktionstype	\N
1234	301	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1235	301	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	1d41c22d-7796-4266-a07f-65c430593bfe	\N	tilknyttedebrugere	\N
1236	301	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	95028aed-f341-57f9-b103-59f67e90cce6	\N	tilknyttedeenheder	\N
1237	301	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1238	301	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	f66083c8-0fbb-4b15-adee-4ccf4b449b99	\N	opgaver	\N
1239	302	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1240	302	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	1d41c22d-7796-4266-a07f-65c430593bfe	\N	tilknyttedebrugere	\N
1241	302	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1242	302	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-189b-32b8-e044-0003ba298018	adresser	DAR
1243	303	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1244	303	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	1d41c22d-7796-4266-a07f-65c430593bfe	\N	tilknyttedebrugere	\N
1245	303	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1246	303	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1247	303	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4543774361	adresser	PHONE
1248	304	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1249	304	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	1d41c22d-7796-4266-a07f-65c430593bfe	\N	tilknyttedebrugere	\N
1250	304	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1251	304	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:hjalmarj@hjorring.dk	adresser	EMAIL
1252	305	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1253	305	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	1d41c22d-7796-4266-a07f-65c430593bfe	\N	tilknyttedebrugere	\N
1254	305	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	\N	organisatoriskfunktionstype	\N
1255	305	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%203	adresser	TEXT
1256	306	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1257	306	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	1d41c22d-7796-4266-a07f-65c430593bfe	\N	tilknyttedebrugere	\N
1258	306	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	20b507cf-fdeb-4123-8da4-db4a15524398	\N	tilknyttedeitsystemer	\N
1259	307	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1260	307	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	1d41c22d-7796-4266-a07f-65c430593bfe	\N	tilknyttedebrugere	\N
1261	307	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	76015baa-c0e0-4fea-82c2-9941c68fa1cd	\N	tilknyttedeitsystemer	\N
1262	308	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1263	308	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	1d41c22d-7796-4266-a07f-65c430593bfe	\N	tilknyttedebrugere	\N
1264	308	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
1265	308	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	a47e0a34-cc21-4ea8-8d2b-5398b7884ac5	\N	organisatoriskfunktionstype	\N
1266	309	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1267	309	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	8d5b5521-9bff-46ab-aa91-44fd671ede6d	\N	tilknyttedebrugere	\N
1268	309	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	95028aed-f341-57f9-b103-59f67e90cce6	\N	tilknyttedeenheder	\N
1269	309	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1270	309	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	7bfbb207-85a3-40d8-97da-03ad7a92b2e2	\N	opgaver	\N
1271	310	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1272	310	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	8d5b5521-9bff-46ab-aa91-44fd671ede6d	\N	tilknyttedebrugere	\N
1273	310	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1274	310	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	\N	urn:dar:0a3f50c8-1593-32b8-e044-0003ba298018	adresser	DAR
1275	311	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1276	311	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	8d5b5521-9bff-46ab-aa91-44fd671ede6d	\N	tilknyttedebrugere	\N
1277	311	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1278	311	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1279	311	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	\N	urn:magenta.dk:telefon:+4582736564	adresser	PHONE
1280	312	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1281	312	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	8d5b5521-9bff-46ab-aa91-44fd671ede6d	\N	tilknyttedebrugere	\N
1282	312	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1283	312	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	\N	urn:mailto:peterb@hjorring.dk	adresser	EMAIL
1284	313	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1285	313	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	8d5b5521-9bff-46ab-aa91-44fd671ede6d	\N	tilknyttedebrugere	\N
1286	313	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	95028aed-f341-57f9-b103-59f67e90cce6	\N	tilknyttedeenheder	\N
1287	313	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1288	313	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1289	313	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	861a977e-3490-4d73-b005-587af2532e1d	\N	opgaver	lederansvar
1290	313	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	9f833d6c-3611-49fe-b155-71a7ba1602a2	\N	opgaver	lederansvar
1291	313	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1292	314	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1293	314	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	958aee35-13d5-49d5-98f2-348cd590d600	\N	tilknyttedebrugere	\N
1294	314	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	81d20630-a126-577a-a47e-7a21155117d2	\N	tilknyttedeenheder	\N
1295	314	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1296	314	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	166929d8-a994-4f73-b8f1-a6eae9f9889f	\N	opgaver	\N
1297	315	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1298	315	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	958aee35-13d5-49d5-98f2-348cd590d600	\N	tilknyttedebrugere	\N
1299	315	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1300	315	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	\N	urn:dar:0a3f50c7-eae5-32b8-e044-0003ba298018	adresser	DAR
1301	316	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1302	316	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	958aee35-13d5-49d5-98f2-348cd590d600	\N	tilknyttedebrugere	\N
1303	316	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1304	316	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1305	316	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4545553360	adresser	PHONE
1306	317	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1307	317	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	958aee35-13d5-49d5-98f2-348cd590d600	\N	tilknyttedebrugere	\N
1308	317	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1309	317	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:kirstens@hjorring.dk	adresser	EMAIL
1310	318	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1311	318	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	958aee35-13d5-49d5-98f2-348cd590d600	\N	tilknyttedebrugere	\N
1312	318	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	\N	tilknyttedeitsystemer	\N
1313	319	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1314	319	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	958aee35-13d5-49d5-98f2-348cd590d600	\N	tilknyttedebrugere	\N
1315	319	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	81d20630-a126-577a-a47e-7a21155117d2	\N	tilknyttedeenheder	\N
1316	319	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1317	319	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1318	319	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	ea13a75a-2b7f-4b89-9ab4-dd7be5fcbd1e	\N	opgaver	lederansvar
1319	319	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	9f833d6c-3611-49fe-b155-71a7ba1602a2	\N	opgaver	lederansvar
1320	319	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1321	320	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1322	320	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	15a22fde-b7ae-424a-be74-f198ad00d915	\N	tilknyttedebrugere	\N
1323	320	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	81d20630-a126-577a-a47e-7a21155117d2	\N	tilknyttedeenheder	\N
1324	320	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1325	320	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	bc9f6541-1031-49ff-ab04-c1cad96a2871	\N	opgaver	\N
1326	321	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1327	321	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	15a22fde-b7ae-424a-be74-f198ad00d915	\N	tilknyttedebrugere	\N
1328	321	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1329	321	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	\N	urn:dar:2b3d6b24-c84b-29a6-e044-0003ba298018	adresser	DAR
1330	322	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1331	322	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	15a22fde-b7ae-424a-be74-f198ad00d915	\N	tilknyttedebrugere	\N
1332	322	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1333	322	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
1334	322	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4518764043	adresser	PHONE
1335	323	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1336	323	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	15a22fde-b7ae-424a-be74-f198ad00d915	\N	tilknyttedebrugere	\N
1337	323	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1338	323	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:marieb@hjorring.dk	adresser	EMAIL
1339	324	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1340	324	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	15a22fde-b7ae-424a-be74-f198ad00d915	\N	tilknyttedebrugere	\N
1341	324	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	20b507cf-fdeb-4123-8da4-db4a15524398	\N	tilknyttedeitsystemer	\N
1342	325	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1343	325	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	15a22fde-b7ae-424a-be74-f198ad00d915	\N	tilknyttedebrugere	\N
1344	325	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	81d20630-a126-577a-a47e-7a21155117d2	\N	tilknyttedeenheder	\N
1345	325	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	5c074e78-724f-45af-9b78-8daddad60d57	\N	organisatoriskfunktionstype	\N
1346	326	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1347	326	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	bb84d7fa-bc05-4466-9051-d1c6208650ad	\N	tilknyttedebrugere	\N
1348	326	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
1349	326	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1350	326	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	7bfbb207-85a3-40d8-97da-03ad7a92b2e2	\N	opgaver	\N
1351	327	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1352	327	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	bb84d7fa-bc05-4466-9051-d1c6208650ad	\N	tilknyttedebrugere	\N
1353	327	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1354	327	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	\N	urn:dar:0a3f50c9-13a5-32b8-e044-0003ba298018	adresser	DAR
1355	328	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1356	328	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	bb84d7fa-bc05-4466-9051-d1c6208650ad	\N	tilknyttedebrugere	\N
1357	328	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1358	328	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1359	328	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4523387054	adresser	PHONE
1360	329	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1361	329	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	bb84d7fa-bc05-4466-9051-d1c6208650ad	\N	tilknyttedebrugere	\N
1362	329	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1363	329	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:børgeb@hjorring.dk	adresser	EMAIL
1364	330	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1365	330	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	bb84d7fa-bc05-4466-9051-d1c6208650ad	\N	tilknyttedebrugere	\N
1366	330	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	76015baa-c0e0-4fea-82c2-9941c68fa1cd	\N	tilknyttedeitsystemer	\N
1367	331	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1368	331	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	bb84d7fa-bc05-4466-9051-d1c6208650ad	\N	tilknyttedebrugere	\N
1369	331	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
1370	332	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1371	332	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	bb84d7fa-bc05-4466-9051-d1c6208650ad	\N	tilknyttedebrugere	\N
1372	332	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
1373	332	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	5c074e78-724f-45af-9b78-8daddad60d57	\N	organisatoriskfunktionstype	\N
1374	333	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1375	333	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	d8084037-6f9d-46ad-889a-0408aa6309a7	\N	tilknyttedebrugere	\N
1376	333	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
1377	333	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1378	333	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	f19417e6-1f70-442a-bfbf-2ad65397d84f	\N	opgaver	\N
1379	334	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1380	334	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	d8084037-6f9d-46ad-889a-0408aa6309a7	\N	tilknyttedebrugere	\N
1381	334	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1382	334	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	\N	urn:dar:0a3f50c8-037d-32b8-e044-0003ba298018	adresser	DAR
1383	335	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1384	335	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	d8084037-6f9d-46ad-889a-0408aa6309a7	\N	tilknyttedebrugere	\N
1385	335	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1386	335	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1387	335	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	\N	urn:magenta.dk:telefon:+4566602653	adresser	PHONE
1388	336	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1389	336	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	d8084037-6f9d-46ad-889a-0408aa6309a7	\N	tilknyttedebrugere	\N
1390	336	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1391	336	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	\N	urn:mailto:olej@hjorring.dk	adresser	EMAIL
1392	337	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1393	337	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	d8084037-6f9d-46ad-889a-0408aa6309a7	\N	tilknyttedebrugere	\N
1394	337	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
1395	337	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	68ce5504-54ec-474f-8fed-2709442e0c9b	\N	organisatoriskfunktionstype	\N
1396	338	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1397	338	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	d8084037-6f9d-46ad-889a-0408aa6309a7	\N	tilknyttedebrugere	\N
1398	338	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
1399	338	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	5c074e78-724f-45af-9b78-8daddad60d57	\N	organisatoriskfunktionstype	\N
1400	339	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1401	339	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	e4b34d8c-d824-4bca-a955-c08bd547742c	\N	tilknyttedebrugere	\N
1402	339	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
1403	339	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1404	339	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	f66083c8-0fbb-4b15-adee-4ccf4b449b99	\N	opgaver	\N
1405	340	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1406	340	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	e4b34d8c-d824-4bca-a955-c08bd547742c	\N	tilknyttedebrugere	\N
1407	340	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1408	340	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	\N	urn:dar:0a3f50c8-2c7c-32b8-e044-0003ba298018	adresser	DAR
1409	341	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1410	341	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	e4b34d8c-d824-4bca-a955-c08bd547742c	\N	tilknyttedebrugere	\N
1411	341	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1412	341	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1413	341	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4553351434	adresser	PHONE
1414	342	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1415	342	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	e4b34d8c-d824-4bca-a955-c08bd547742c	\N	tilknyttedebrugere	\N
1416	342	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1417	342	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:karenh@hjorring.dk	adresser	EMAIL
1418	343	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1419	343	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	e4b34d8c-d824-4bca-a955-c08bd547742c	\N	tilknyttedebrugere	\N
1420	343	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	\N	tilknyttedeitsystemer	\N
1421	344	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1422	344	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	d3fff832-5740-451d-ac2d-5fcbb4a1822f	\N	tilknyttedebrugere	\N
1423	344	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
1424	344	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1425	344	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	4f5aad51-8c28-4c0d-9b17-a2a30df36849	\N	opgaver	\N
1426	345	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1427	345	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	d3fff832-5740-451d-ac2d-5fcbb4a1822f	\N	tilknyttedebrugere	\N
1428	345	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1429	345	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	\N	urn:dar:ad28a57c-42f7-4665-9f62-4f86162f5c6c	adresser	DAR
1430	346	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1431	346	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	d3fff832-5740-451d-ac2d-5fcbb4a1822f	\N	tilknyttedebrugere	\N
1432	346	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1433	346	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1434	346	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	\N	urn:magenta.dk:telefon:+4530324740	adresser	PHONE
1435	347	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1436	347	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	d3fff832-5740-451d-ac2d-5fcbb4a1822f	\N	tilknyttedebrugere	\N
1437	347	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1438	347	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	\N	urn:mailto:gustavk@hjorring.dk	adresser	EMAIL
1439	348	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1440	348	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	d3fff832-5740-451d-ac2d-5fcbb4a1822f	\N	tilknyttedebrugere	\N
1441	348	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	\N	organisatoriskfunktionstype	\N
1442	348	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	\N	urn:text:%42ygning%207	adresser	TEXT
1443	349	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1444	349	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	d3fff832-5740-451d-ac2d-5fcbb4a1822f	\N	tilknyttedebrugere	\N
1445	349	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
1446	350	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1447	350	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	d3fff832-5740-451d-ac2d-5fcbb4a1822f	\N	tilknyttedebrugere	\N
1448	350	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	\N	tilknyttedeitsystemer	\N
1449	351	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1450	351	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	d3fff832-5740-451d-ac2d-5fcbb4a1822f	\N	tilknyttedebrugere	\N
1451	351	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
1452	351	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1453	351	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1454	351	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	ea13a75a-2b7f-4b89-9ab4-dd7be5fcbd1e	\N	opgaver	lederansvar
1455	351	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	9f833d6c-3611-49fe-b155-71a7ba1602a2	\N	opgaver	lederansvar
1456	351	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1457	352	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1458	352	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	b15a3d56-2a60-48b5-9b4a-2d459b829fd0	\N	tilknyttedebrugere	\N
1459	352	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
1460	352	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1461	352	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	b617b6e7-166f-4c30-8ead-aeb360febf0e	\N	opgaver	\N
1462	353	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1463	353	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	b15a3d56-2a60-48b5-9b4a-2d459b829fd0	\N	tilknyttedebrugere	\N
1464	353	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1465	353	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-3c9e-32b8-e044-0003ba298018	adresser	DAR
1466	354	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1467	354	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	b15a3d56-2a60-48b5-9b4a-2d459b829fd0	\N	tilknyttedebrugere	\N
1468	354	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1469	354	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
1470	354	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4551712528	adresser	PHONE
1471	355	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1472	355	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	b15a3d56-2a60-48b5-9b4a-2d459b829fd0	\N	tilknyttedebrugere	\N
1473	355	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1474	355	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:jensl@hjorring.dk	adresser	EMAIL
1475	356	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1476	356	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	b15a3d56-2a60-48b5-9b4a-2d459b829fd0	\N	tilknyttedebrugere	\N
1477	356	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
1478	356	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1479	356	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1480	356	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	9f833d6c-3611-49fe-b155-71a7ba1602a2	\N	opgaver	lederansvar
1481	356	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	861a977e-3490-4d73-b005-587af2532e1d	\N	opgaver	lederansvar
1482	356	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1483	357	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1484	357	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	f5e05fc2-a484-4fb5-95d3-d9ba89adc52e	\N	tilknyttedebrugere	\N
1485	357	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
1486	357	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1487	357	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	ddc55bb7-7f76-4ff2-9c12-abb385cf28c5	\N	opgaver	\N
1488	358	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1489	358	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	f5e05fc2-a484-4fb5-95d3-d9ba89adc52e	\N	tilknyttedebrugere	\N
1490	358	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1491	358	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-add7-32b8-e044-0003ba298018	adresser	DAR
1492	359	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1493	359	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	f5e05fc2-a484-4fb5-95d3-d9ba89adc52e	\N	tilknyttedebrugere	\N
1494	359	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1495	359	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1496	359	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4551580882	adresser	PHONE
1497	360	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1498	360	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	f5e05fc2-a484-4fb5-95d3-d9ba89adc52e	\N	tilknyttedebrugere	\N
1499	360	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1500	360	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:birgitteh@hjorring.dk	adresser	EMAIL
1501	361	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1502	361	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	f5e05fc2-a484-4fb5-95d3-d9ba89adc52e	\N	tilknyttedebrugere	\N
1503	361	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	76015baa-c0e0-4fea-82c2-9941c68fa1cd	\N	tilknyttedeitsystemer	\N
1504	362	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1505	362	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	f5e05fc2-a484-4fb5-95d3-d9ba89adc52e	\N	tilknyttedebrugere	\N
1506	362	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	ff2afd49-0c26-556a-b01b-d2d6bd14a2af	\N	tilknyttedeenheder	\N
1507	362	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	5b03a02c-a698-4c40-a530-d5578b142283	\N	organisatoriskfunktionstype	\N
1508	363	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1509	363	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	9ff61686-1144-457b-b735-bf1871379cca	\N	tilknyttedebrugere	\N
1510	363	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
1511	363	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1512	363	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	4f5aad51-8c28-4c0d-9b17-a2a30df36849	\N	opgaver	\N
1513	364	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1514	364	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	9ff61686-1144-457b-b735-bf1871379cca	\N	tilknyttedebrugere	\N
1515	364	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1516	364	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	\N	urn:dar:0a3f50c8-234f-32b8-e044-0003ba298018	adresser	DAR
1517	365	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1518	365	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	9ff61686-1144-457b-b735-bf1871379cca	\N	tilknyttedebrugere	\N
1519	365	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1520	365	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1521	365	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4512735824	adresser	PHONE
1522	366	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1523	366	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	9ff61686-1144-457b-b735-bf1871379cca	\N	tilknyttedebrugere	\N
1524	366	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1525	366	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:evac@hjorring.dk	adresser	EMAIL
1526	367	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1527	367	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	9ff61686-1144-457b-b735-bf1871379cca	\N	tilknyttedebrugere	\N
1528	367	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	68746352-ef27-44e6-9bcc-30cbbaee4fb3	\N	tilknyttedeitsystemer	\N
1529	368	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1530	368	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	9ff61686-1144-457b-b735-bf1871379cca	\N	tilknyttedebrugere	\N
1531	368	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
1532	369	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1533	369	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	9ff61686-1144-457b-b735-bf1871379cca	\N	tilknyttedebrugere	\N
1534	369	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
1535	369	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	68ce5504-54ec-474f-8fed-2709442e0c9b	\N	organisatoriskfunktionstype	\N
1536	370	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1537	370	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	9ff61686-1144-457b-b735-bf1871379cca	\N	tilknyttedebrugere	\N
1538	370	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	b1b87a57-600b-5c1d-80aa-fe0ffd609d29	\N	tilknyttedeenheder	\N
1539	370	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	eb911cea-f1f1-4002-b584-f812022ebe39	\N	organisatoriskfunktionstype	\N
1540	371	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1541	371	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	3187c0db-9b0d-4368-b756-de018f9b6ef9	\N	tilknyttedebrugere	\N
1542	371	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
1543	371	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1544	371	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	12f83ab4-fffd-4aac-8464-2830eacdb506	\N	opgaver	\N
1545	372	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1546	372	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	3187c0db-9b0d-4368-b756-de018f9b6ef9	\N	tilknyttedebrugere	\N
1547	372	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1548	372	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	\N	urn:dar:0a3f50c7-fd14-32b8-e044-0003ba298018	adresser	DAR
1549	373	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1550	373	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	3187c0db-9b0d-4368-b756-de018f9b6ef9	\N	tilknyttedebrugere	\N
1551	373	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1552	373	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
1553	373	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4542345584	adresser	PHONE
1554	374	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1555	374	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	3187c0db-9b0d-4368-b756-de018f9b6ef9	\N	tilknyttedebrugere	\N
1556	374	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1557	374	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:gunnern@hjorring.dk	adresser	EMAIL
1558	375	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1559	375	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	3187c0db-9b0d-4368-b756-de018f9b6ef9	\N	tilknyttedebrugere	\N
1560	375	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	a6773531-6c0a-4c7b-b0e2-77992412b610	\N	tilknyttedeenheder	\N
1561	375	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	893bc985-8872-4b5d-a68f-153c059d7e64	\N	organisatoriskfunktionstype	\N
1562	376	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1563	376	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	936cb72e-dc1a-49a3-a297-e97f2d480195	\N	tilknyttedebrugere	\N
1564	376	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
1565	376	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1566	376	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	0c7f0826-ec4a-4daf-b08e-d6b34f690cc9	\N	opgaver	\N
1567	377	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1568	377	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	936cb72e-dc1a-49a3-a297-e97f2d480195	\N	tilknyttedebrugere	\N
1569	377	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1570	377	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	\N	urn:dar:0a3f50c8-45a0-32b8-e044-0003ba298018	adresser	DAR
1571	378	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1572	378	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	936cb72e-dc1a-49a3-a297-e97f2d480195	\N	tilknyttedebrugere	\N
1573	378	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1574	378	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
1575	378	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4545526262	adresser	PHONE
1576	379	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1577	379	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	936cb72e-dc1a-49a3-a297-e97f2d480195	\N	tilknyttedebrugere	\N
1578	379	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1579	379	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:aagej@hjorring.dk	adresser	EMAIL
1580	380	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1581	380	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	936cb72e-dc1a-49a3-a297-e97f2d480195	\N	tilknyttedebrugere	\N
1582	380	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
1583	380	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	eb911cea-f1f1-4002-b584-f812022ebe39	\N	organisatoriskfunktionstype	\N
1584	381	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1585	381	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	38793c9c-3b30-4a3a-a63b-4894d943d2bc	\N	tilknyttedebrugere	\N
1586	381	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
1587	381	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1588	381	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	ddc55bb7-7f76-4ff2-9c12-abb385cf28c5	\N	opgaver	\N
1589	382	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1590	382	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	38793c9c-3b30-4a3a-a63b-4894d943d2bc	\N	tilknyttedebrugere	\N
1591	382	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1592	382	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-4bd9-32b8-e044-0003ba298018	adresser	DAR
1593	383	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1594	383	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	38793c9c-3b30-4a3a-a63b-4894d943d2bc	\N	tilknyttedebrugere	\N
1595	383	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1596	383	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
1597	383	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4562685287	adresser	PHONE
1598	384	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1599	384	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	38793c9c-3b30-4a3a-a63b-4894d943d2bc	\N	tilknyttedebrugere	\N
1600	384	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1601	384	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:flemmingl@hjorring.dk	adresser	EMAIL
1602	385	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1603	385	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	38793c9c-3b30-4a3a-a63b-4894d943d2bc	\N	tilknyttedebrugere	\N
1604	385	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	76015baa-c0e0-4fea-82c2-9941c68fa1cd	\N	tilknyttedeitsystemer	\N
1605	386	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1606	386	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	38793c9c-3b30-4a3a-a63b-4894d943d2bc	\N	tilknyttedebrugere	\N
1607	386	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
1608	386	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1609	386	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1610	386	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	91f65ddc-5eda-4b63-b7bc-506871c76181	\N	opgaver	lederansvar
1611	386	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	861a977e-3490-4d73-b005-587af2532e1d	\N	opgaver	lederansvar
1612	386	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1613	387	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1614	387	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	5aee93fb-ce29-4518-98e0-643e4932c329	\N	tilknyttedebrugere	\N
1615	387	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	1da5de09-b1a8-5952-987d-04e07a3ffd50	\N	tilknyttedeenheder	\N
1616	387	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1617	387	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	d07ce76c-ed70-4b92-b419-84b948e17086	\N	opgaver	\N
1618	388	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1619	388	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	5aee93fb-ce29-4518-98e0-643e4932c329	\N	tilknyttedebrugere	\N
1620	388	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1621	388	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-1fd8-32b8-e044-0003ba298018	adresser	DAR
1622	389	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1623	389	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	5aee93fb-ce29-4518-98e0-643e4932c329	\N	tilknyttedebrugere	\N
1624	389	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1625	389	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1626	389	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4571651038	adresser	PHONE
1627	390	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1628	390	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	5aee93fb-ce29-4518-98e0-643e4932c329	\N	tilknyttedebrugere	\N
1629	390	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1630	390	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:poulan@hjorring.dk	adresser	EMAIL
1631	391	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1632	391	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	5aee93fb-ce29-4518-98e0-643e4932c329	\N	tilknyttedebrugere	\N
1633	391	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
1634	392	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1635	392	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	6b222d46-3260-4479-955c-d485eb16acca	\N	tilknyttedebrugere	\N
1636	392	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
1637	392	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1638	392	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	60a914dd-f35d-451e-b344-46d591558194	\N	opgaver	\N
1639	393	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1640	393	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	6b222d46-3260-4479-955c-d485eb16acca	\N	tilknyttedebrugere	\N
1641	393	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1642	393	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-3fbd-32b8-e044-0003ba298018	adresser	DAR
1643	394	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1644	394	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	6b222d46-3260-4479-955c-d485eb16acca	\N	tilknyttedebrugere	\N
1645	394	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1646	394	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1647	394	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4542285244	adresser	PHONE
1648	395	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1649	395	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	6b222d46-3260-4479-955c-d485eb16acca	\N	tilknyttedebrugere	\N
1650	395	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1651	395	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:egonj@hjorring.dk	adresser	EMAIL
1652	396	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1653	396	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	6b222d46-3260-4479-955c-d485eb16acca	\N	tilknyttedebrugere	\N
1654	396	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	\N	tilknyttedeitsystemer	\N
1655	397	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1656	397	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	6b222d46-3260-4479-955c-d485eb16acca	\N	tilknyttedebrugere	\N
1657	397	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	20b507cf-fdeb-4123-8da4-db4a15524398	\N	tilknyttedeitsystemer	\N
1658	398	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1659	398	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	6b222d46-3260-4479-955c-d485eb16acca	\N	tilknyttedebrugere	\N
1660	398	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
1661	398	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1662	398	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1663	398	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	9f833d6c-3611-49fe-b155-71a7ba1602a2	\N	opgaver	lederansvar
1664	398	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	861a977e-3490-4d73-b005-587af2532e1d	\N	opgaver	lederansvar
1665	398	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1666	399	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1667	399	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	3c45c707-9ae0-41fc-af91-b94f69e28a56	\N	tilknyttedebrugere	\N
1668	399	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
1669	399	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1670	399	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	12f83ab4-fffd-4aac-8464-2830eacdb506	\N	opgaver	\N
1671	400	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1672	400	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	3c45c707-9ae0-41fc-af91-b94f69e28a56	\N	tilknyttedebrugere	\N
1673	400	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1674	400	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-9b12-32b8-e044-0003ba298018	adresser	DAR
1675	401	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1676	401	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	3c45c707-9ae0-41fc-af91-b94f69e28a56	\N	tilknyttedebrugere	\N
1677	401	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1678	401	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1679	401	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4555110434	adresser	PHONE
1680	402	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1681	402	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	3c45c707-9ae0-41fc-af91-b94f69e28a56	\N	tilknyttedebrugere	\N
1682	402	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1683	402	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:pouls@hjorring.dk	adresser	EMAIL
1684	403	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1685	403	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	3c45c707-9ae0-41fc-af91-b94f69e28a56	\N	tilknyttedebrugere	\N
1686	403	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
1687	404	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1688	404	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	3c45c707-9ae0-41fc-af91-b94f69e28a56	\N	tilknyttedebrugere	\N
1689	404	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	68746352-ef27-44e6-9bcc-30cbbaee4fb3	\N	tilknyttedeitsystemer	\N
1690	405	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1691	405	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55	\N	tilknyttedebrugere	\N
1692	405	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
1693	405	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1694	405	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	ad5b6590-2db5-4dad-ad89-1027314cff16	\N	opgaver	\N
1695	406	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1696	406	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55	\N	tilknyttedebrugere	\N
1697	406	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1698	406	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	\N	urn:dar:0a3f50c9-19c1-32b8-e044-0003ba298018	adresser	DAR
1699	407	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1700	407	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55	\N	tilknyttedebrugere	\N
1701	407	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1702	407	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1703	407	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4548351417	adresser	PHONE
1704	408	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1705	408	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55	\N	tilknyttedebrugere	\N
1706	408	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1707	408	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:marthineh@hjorring.dk	adresser	EMAIL
1708	409	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1709	409	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55	\N	tilknyttedebrugere	\N
1710	409	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	\N	tilknyttedeitsystemer	\N
1711	410	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1712	410	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55	\N	tilknyttedebrugere	\N
1713	410	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	20b507cf-fdeb-4123-8da4-db4a15524398	\N	tilknyttedeitsystemer	\N
1714	411	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1715	411	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55	\N	tilknyttedebrugere	\N
1716	411	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	9723ddfb-a309-5b93-ace1-5b88c8336a66	\N	tilknyttedeenheder	\N
1717	411	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	68ce5504-54ec-474f-8fed-2709442e0c9b	\N	organisatoriskfunktionstype	\N
1718	412	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1719	412	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	6e23d4e9-b7b6-4d54-8eba-b1fe83ea0c55	\N	tilknyttedebrugere	\N
1720	412	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	5f03f259-598a-5a38-9cc1-36da20431f4b	\N	tilknyttedeenheder	\N
1721	412	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	eb911cea-f1f1-4002-b584-f812022ebe39	\N	organisatoriskfunktionstype	\N
1722	413	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1723	413	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	419e5157-6173-4b36-967d-17a5556c1279	\N	tilknyttedebrugere	\N
1724	413	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
1725	413	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1726	413	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	ad5b6590-2db5-4dad-ad89-1027314cff16	\N	opgaver	\N
1727	414	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1728	414	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	419e5157-6173-4b36-967d-17a5556c1279	\N	tilknyttedebrugere	\N
1729	414	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1730	414	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	\N	urn:dar:0a3f50c8-1ebe-32b8-e044-0003ba298018	adresser	DAR
1731	415	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1732	415	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	419e5157-6173-4b36-967d-17a5556c1279	\N	tilknyttedebrugere	\N
1733	415	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1734	415	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
1735	415	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	\N	urn:magenta.dk:telefon:+4555335753	adresser	PHONE
1736	416	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1737	416	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	419e5157-6173-4b36-967d-17a5556c1279	\N	tilknyttedebrugere	\N
1738	416	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1739	416	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	\N	urn:mailto:madsr@hjorring.dk	adresser	EMAIL
1740	417	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1741	417	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	419e5157-6173-4b36-967d-17a5556c1279	\N	tilknyttedebrugere	\N
1742	417	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	20b507cf-fdeb-4123-8da4-db4a15524398	\N	tilknyttedeitsystemer	\N
1743	418	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1744	418	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	419e5157-6173-4b36-967d-17a5556c1279	\N	tilknyttedebrugere	\N
1745	418	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
1746	418	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1747	418	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1748	418	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	01f89ef8-0651-43c2-afda-e24f0d8fe05b	\N	opgaver	lederansvar
1749	418	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	861a977e-3490-4d73-b005-587af2532e1d	\N	opgaver	lederansvar
1750	418	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1751	419	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1752	419	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	23768c40-05bf-4d0d-b263-495750673b31	\N	tilknyttedebrugere	\N
1753	419	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
1754	419	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1755	419	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	f66083c8-0fbb-4b15-adee-4ccf4b449b99	\N	opgaver	\N
1756	420	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1757	420	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	23768c40-05bf-4d0d-b263-495750673b31	\N	tilknyttedebrugere	\N
1758	420	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1759	420	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-22f2-32b8-e044-0003ba298018	adresser	DAR
1760	421	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1761	421	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	23768c40-05bf-4d0d-b263-495750673b31	\N	tilknyttedebrugere	\N
1762	421	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1763	421	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1764	421	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4566607282	adresser	PHONE
1765	422	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1766	422	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	23768c40-05bf-4d0d-b263-495750673b31	\N	tilknyttedebrugere	\N
1767	422	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1768	422	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:annej@hjorring.dk	adresser	EMAIL
1769	423	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1770	423	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	23768c40-05bf-4d0d-b263-495750673b31	\N	tilknyttedebrugere	\N
1771	423	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	20b507cf-fdeb-4123-8da4-db4a15524398	\N	tilknyttedeitsystemer	\N
1772	424	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1773	424	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	23768c40-05bf-4d0d-b263-495750673b31	\N	tilknyttedebrugere	\N
1774	424	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
1775	424	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	d4674f4d-0ee9-4bbc-b71d-97903afc3522	\N	organisatoriskfunktionstype	\N
1776	425	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1777	425	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	23768c40-05bf-4d0d-b263-495750673b31	\N	tilknyttedebrugere	\N
1778	425	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
1779	425	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	eb911cea-f1f1-4002-b584-f812022ebe39	\N	organisatoriskfunktionstype	\N
1780	426	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1781	426	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	773abd21-fb11-44a6-930e-74227ad6a470	\N	tilknyttedebrugere	\N
1782	426	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
1783	426	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1784	426	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	b617b6e7-166f-4c30-8ead-aeb360febf0e	\N	opgaver	\N
1785	427	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1786	427	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	773abd21-fb11-44a6-930e-74227ad6a470	\N	tilknyttedebrugere	\N
1787	427	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1788	427	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c9-1b65-32b8-e044-0003ba298018	adresser	DAR
1789	428	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1790	428	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	773abd21-fb11-44a6-930e-74227ad6a470	\N	tilknyttedebrugere	\N
1791	428	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1792	428	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1793	428	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4554628754	adresser	PHONE
1794	429	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1795	429	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	773abd21-fb11-44a6-930e-74227ad6a470	\N	tilknyttedebrugere	\N
1796	429	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1797	429	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:michaelw@hjorring.dk	adresser	EMAIL
1798	430	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1799	430	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	773abd21-fb11-44a6-930e-74227ad6a470	\N	tilknyttedebrugere	\N
1800	430	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	\N	organisatoriskfunktionstype	\N
1801	430	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%2016	adresser	TEXT
1802	431	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1803	431	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	773abd21-fb11-44a6-930e-74227ad6a470	\N	tilknyttedebrugere	\N
1804	431	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	68746352-ef27-44e6-9bcc-30cbbaee4fb3	\N	tilknyttedeitsystemer	\N
1805	432	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1806	432	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	773abd21-fb11-44a6-930e-74227ad6a470	\N	tilknyttedebrugere	\N
1807	432	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	\N	tilknyttedeitsystemer	\N
1808	433	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1809	433	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	20bd601d-581a-4d96-96b7-188e7645bc24	\N	tilknyttedebrugere	\N
1810	433	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	485c8355-ac5e-57f1-b792-3dd5d1b1a0b4	\N	tilknyttedeenheder	\N
1811	433	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1812	433	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	a825965e-da87-4317-a40b-80f8d33814cc	\N	opgaver	\N
1813	434	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1814	434	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	20bd601d-581a-4d96-96b7-188e7645bc24	\N	tilknyttedebrugere	\N
1815	434	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1816	434	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a41a-32b8-e044-0003ba298018	adresser	DAR
1817	435	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1818	435	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	20bd601d-581a-4d96-96b7-188e7645bc24	\N	tilknyttedebrugere	\N
1819	435	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1820	435	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1821	435	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4526543580	adresser	PHONE
1822	436	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1823	436	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	20bd601d-581a-4d96-96b7-188e7645bc24	\N	tilknyttedebrugere	\N
1824	436	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1825	436	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:helgaj@hjorring.dk	adresser	EMAIL
1826	437	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1827	437	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	20bd601d-581a-4d96-96b7-188e7645bc24	\N	tilknyttedebrugere	\N
1828	437	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	\N	organisatoriskfunktionstype	\N
1829	437	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	\N	urn:text:%42ygning%2012	adresser	TEXT
1830	438	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1831	438	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	20bd601d-581a-4d96-96b7-188e7645bc24	\N	tilknyttedebrugere	\N
1832	438	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
1833	439	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1834	439	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	20bd601d-581a-4d96-96b7-188e7645bc24	\N	tilknyttedebrugere	\N
1835	439	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	485c8355-ac5e-57f1-b792-3dd5d1b1a0b4	\N	tilknyttedeenheder	\N
1836	439	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1837	439	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1838	439	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	01f89ef8-0651-43c2-afda-e24f0d8fe05b	\N	opgaver	lederansvar
1839	439	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	9f833d6c-3611-49fe-b155-71a7ba1602a2	\N	opgaver	lederansvar
1840	439	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1841	440	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1842	440	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	139b917c-7135-4c26-847c-e13c9f871c87	\N	tilknyttedebrugere	\N
1843	440	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	485c8355-ac5e-57f1-b792-3dd5d1b1a0b4	\N	tilknyttedeenheder	\N
1844	440	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1845	440	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	bc9f6541-1031-49ff-ab04-c1cad96a2871	\N	opgaver	\N
1846	441	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1847	441	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	139b917c-7135-4c26-847c-e13c9f871c87	\N	tilknyttedebrugere	\N
1848	441	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1849	441	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c7-f4aa-32b8-e044-0003ba298018	adresser	DAR
1850	442	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1851	442	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	139b917c-7135-4c26-847c-e13c9f871c87	\N	tilknyttedebrugere	\N
1852	442	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1853	442	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1854	442	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4511280236	adresser	PHONE
1855	443	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1856	443	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	139b917c-7135-4c26-847c-e13c9f871c87	\N	tilknyttedebrugere	\N
1857	443	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1858	443	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:antons@hjorring.dk	adresser	EMAIL
1859	444	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1860	444	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	139b917c-7135-4c26-847c-e13c9f871c87	\N	tilknyttedebrugere	\N
1861	444	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	\N	tilknyttedeitsystemer	\N
1862	445	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1863	445	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	139b917c-7135-4c26-847c-e13c9f871c87	\N	tilknyttedebrugere	\N
1864	445	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	68746352-ef27-44e6-9bcc-30cbbaee4fb3	\N	tilknyttedeitsystemer	\N
1865	446	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1866	446	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	139b917c-7135-4c26-847c-e13c9f871c87	\N	tilknyttedebrugere	\N
1867	446	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	f20880eb-00e2-5c8b-9ee7-d76e8b0b1a92	\N	tilknyttedeenheder	\N
1868	446	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	ecbe9c67-1b0a-4aba-8e50-67a92691fd61	\N	organisatoriskfunktionstype	\N
1869	447	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1870	447	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	c0e5f7cf-66c7-41d4-8dcb-6137da5d2343	\N	tilknyttedebrugere	\N
1871	447	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
1872	447	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1873	447	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	f19417e6-1f70-442a-bfbf-2ad65397d84f	\N	opgaver	\N
1874	448	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1875	448	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	c0e5f7cf-66c7-41d4-8dcb-6137da5d2343	\N	tilknyttedebrugere	\N
1876	448	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1877	448	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	\N	urn:dar:48284790-c129-61c5-e044-0003ba298018	adresser	DAR
1878	449	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1879	449	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	c0e5f7cf-66c7-41d4-8dcb-6137da5d2343	\N	tilknyttedebrugere	\N
1880	449	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1881	449	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
1882	449	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4532864148	adresser	PHONE
1883	450	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1884	450	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	c0e5f7cf-66c7-41d4-8dcb-6137da5d2343	\N	tilknyttedebrugere	\N
1885	450	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1886	450	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:annah@hjorring.dk	adresser	EMAIL
1887	451	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1888	451	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	c0e5f7cf-66c7-41d4-8dcb-6137da5d2343	\N	tilknyttedebrugere	\N
1889	451	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	68746352-ef27-44e6-9bcc-30cbbaee4fb3	\N	tilknyttedeitsystemer	\N
1890	452	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1891	452	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	c0e5f7cf-66c7-41d4-8dcb-6137da5d2343	\N	tilknyttedebrugere	\N
1892	452	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
1893	452	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	eb911cea-f1f1-4002-b584-f812022ebe39	\N	organisatoriskfunktionstype	\N
1894	453	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1895	453	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	74aa1e09-a97f-4465-94dc-f6568d31451d	\N	tilknyttedebrugere	\N
1896	453	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
1897	453	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1898	453	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	0c7f0826-ec4a-4daf-b08e-d6b34f690cc9	\N	opgaver	\N
1899	454	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1900	454	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	74aa1e09-a97f-4465-94dc-f6568d31451d	\N	tilknyttedebrugere	\N
1901	454	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1902	454	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-a885-32b8-e044-0003ba298018	adresser	DAR
1903	455	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1904	455	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	74aa1e09-a97f-4465-94dc-f6568d31451d	\N	tilknyttedebrugere	\N
1905	455	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1906	455	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1907	455	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4573122501	adresser	PHONE
1908	456	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1909	456	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	74aa1e09-a97f-4465-94dc-f6568d31451d	\N	tilknyttedebrugere	\N
1910	456	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1911	456	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:karenj@hjorring.dk	adresser	EMAIL
1912	457	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1913	457	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	96282f58-e10e-4d4f-ae1a-f25658d68cc8	\N	tilknyttedebrugere	\N
1914	457	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
1915	457	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1916	457	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	166929d8-a994-4f73-b8f1-a6eae9f9889f	\N	opgaver	\N
1917	458	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1918	458	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	96282f58-e10e-4d4f-ae1a-f25658d68cc8	\N	tilknyttedebrugere	\N
1919	458	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1920	458	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	\N	urn:dar:1f7a7527-9e40-403c-e044-0003ba298018	adresser	DAR
1921	459	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1922	459	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	96282f58-e10e-4d4f-ae1a-f25658d68cc8	\N	tilknyttedebrugere	\N
1923	459	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1924	459	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
1925	459	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	\N	urn:magenta.dk:telefon:+4521126756	adresser	PHONE
1926	460	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1927	460	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	96282f58-e10e-4d4f-ae1a-f25658d68cc8	\N	tilknyttedebrugere	\N
1928	460	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1929	460	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	\N	urn:mailto:almal@hjorring.dk	adresser	EMAIL
1930	461	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1931	461	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	96282f58-e10e-4d4f-ae1a-f25658d68cc8	\N	tilknyttedebrugere	\N
1932	461	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	68746352-ef27-44e6-9bcc-30cbbaee4fb3	\N	tilknyttedeitsystemer	\N
1933	462	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1934	462	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	96282f58-e10e-4d4f-ae1a-f25658d68cc8	\N	tilknyttedebrugere	\N
1935	462	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
1936	463	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1937	463	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	96282f58-e10e-4d4f-ae1a-f25658d68cc8	\N	tilknyttedebrugere	\N
1938	463	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
1939	463	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
1940	463	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
1941	463	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	9f833d6c-3611-49fe-b155-71a7ba1602a2	\N	opgaver	lederansvar
1942	463	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	ea13a75a-2b7f-4b89-9ab4-dd7be5fcbd1e	\N	opgaver	lederansvar
1943	463	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
1944	464	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1945	464	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	a9b06498-92aa-4fde-b543-ed8661caa02e	\N	tilknyttedebrugere	\N
1946	464	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	81760628-a69b-584c-baf0-42d217442082	\N	tilknyttedeenheder	\N
1947	464	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1948	464	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	bc9f6541-1031-49ff-ab04-c1cad96a2871	\N	opgaver	\N
1949	465	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1950	465	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	a9b06498-92aa-4fde-b543-ed8661caa02e	\N	tilknyttedebrugere	\N
1951	465	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1952	465	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-1d36-32b8-e044-0003ba298018	adresser	DAR
1953	466	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1954	466	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	a9b06498-92aa-4fde-b543-ed8661caa02e	\N	tilknyttedebrugere	\N
1955	466	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1956	466	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1957	466	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4526672316	adresser	PHONE
1958	467	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1959	467	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	a9b06498-92aa-4fde-b543-ed8661caa02e	\N	tilknyttedebrugere	\N
1960	467	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1961	467	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:valborgn@hjorring.dk	adresser	EMAIL
1962	468	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1963	468	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	a9b06498-92aa-4fde-b543-ed8661caa02e	\N	tilknyttedebrugere	\N
1964	468	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	\N	organisatoriskfunktionstype	\N
1965	468	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%203	adresser	TEXT
1966	469	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1967	469	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	a9b06498-92aa-4fde-b543-ed8661caa02e	\N	tilknyttedebrugere	\N
1968	469	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	20b507cf-fdeb-4123-8da4-db4a15524398	\N	tilknyttedeitsystemer	\N
1969	470	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1970	470	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	de47b9c8-283f-4ea9-9bdf-0795eb5d6a50	\N	tilknyttedebrugere	\N
1971	470	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
1972	470	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1973	470	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	4f5aad51-8c28-4c0d-9b17-a2a30df36849	\N	opgaver	\N
1974	471	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1975	471	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	de47b9c8-283f-4ea9-9bdf-0795eb5d6a50	\N	tilknyttedebrugere	\N
1976	471	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1977	471	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	\N	urn:dar:4a429b69-c601-4d5d-a48f-433b10415df2	adresser	DAR
1978	472	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1979	472	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	de47b9c8-283f-4ea9-9bdf-0795eb5d6a50	\N	tilknyttedebrugere	\N
1980	472	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
1981	472	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
1982	472	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4530320700	adresser	PHONE
1983	473	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1984	473	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	de47b9c8-283f-4ea9-9bdf-0795eb5d6a50	\N	tilknyttedebrugere	\N
1985	473	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
1986	473	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:tinac@hjorring.dk	adresser	EMAIL
1987	474	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1988	474	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	de47b9c8-283f-4ea9-9bdf-0795eb5d6a50	\N	tilknyttedebrugere	\N
1989	474	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
1990	474	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	eb911cea-f1f1-4002-b584-f812022ebe39	\N	organisatoriskfunktionstype	\N
1991	475	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1992	475	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	1969059e-5b9e-43d7-ad9c-01f697c5bfc9	\N	tilknyttedebrugere	\N
1993	475	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
1994	475	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
1995	475	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	bc9f6541-1031-49ff-ab04-c1cad96a2871	\N	opgaver	\N
1996	476	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
1997	476	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	1969059e-5b9e-43d7-ad9c-01f697c5bfc9	\N	tilknyttedebrugere	\N
1998	476	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
1999	476	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	\N	urn:dar:0a3f50c7-e469-32b8-e044-0003ba298018	adresser	DAR
2000	477	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2001	477	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	1969059e-5b9e-43d7-ad9c-01f697c5bfc9	\N	tilknyttedebrugere	\N
2002	477	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
2003	477	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
2004	477	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4553317160	adresser	PHONE
2005	478	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2006	478	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	1969059e-5b9e-43d7-ad9c-01f697c5bfc9	\N	tilknyttedebrugere	\N
2007	478	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
2008	478	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:miep@hjorring.dk	adresser	EMAIL
2009	479	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2010	479	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	1969059e-5b9e-43d7-ad9c-01f697c5bfc9	\N	tilknyttedebrugere	\N
2011	479	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	68746352-ef27-44e6-9bcc-30cbbaee4fb3	\N	tilknyttedeitsystemer	\N
2012	480	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2013	480	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	1969059e-5b9e-43d7-ad9c-01f697c5bfc9	\N	tilknyttedebrugere	\N
2014	480	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	\N	tilknyttedeitsystemer	\N
2015	481	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2016	481	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	1969059e-5b9e-43d7-ad9c-01f697c5bfc9	\N	tilknyttedebrugere	\N
2017	481	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
2018	481	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
2019	481	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
2020	481	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	01f89ef8-0651-43c2-afda-e24f0d8fe05b	\N	opgaver	lederansvar
2021	481	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	861a977e-3490-4d73-b005-587af2532e1d	\N	opgaver	lederansvar
2022	481	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
2023	482	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2024	482	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	ba02c1bc-dd1d-4b04-8f6b-a6093d27a85e	\N	tilknyttedebrugere	\N
2025	482	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
2026	482	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
2027	482	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	d07ce76c-ed70-4b92-b419-84b948e17086	\N	opgaver	\N
2028	483	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2029	483	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	ba02c1bc-dd1d-4b04-8f6b-a6093d27a85e	\N	tilknyttedebrugere	\N
2030	483	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
2031	483	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-0b6a-32b8-e044-0003ba298018	adresser	DAR
2032	484	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2033	484	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	ba02c1bc-dd1d-4b04-8f6b-a6093d27a85e	\N	tilknyttedebrugere	\N
2034	484	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
2035	484	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	5607fe9e-c152-4ad9-b0c2-0472fef9da2d	\N	opgaver	synlighed
2036	484	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4566437087	adresser	PHONE
2037	485	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2038	485	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	ba02c1bc-dd1d-4b04-8f6b-a6093d27a85e	\N	tilknyttedebrugere	\N
2039	485	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
2040	485	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:bc@hjorring.dk	adresser	EMAIL
2041	486	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2042	486	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	ba02c1bc-dd1d-4b04-8f6b-a6093d27a85e	\N	tilknyttedebrugere	\N
2043	486	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	20b507cf-fdeb-4123-8da4-db4a15524398	\N	tilknyttedeitsystemer	\N
2044	487	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2045	487	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	ba02c1bc-dd1d-4b04-8f6b-a6093d27a85e	\N	tilknyttedebrugere	\N
2046	487	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	a726fbe8-32aa-55d0-a1c2-cb42ac13d42c	\N	tilknyttedeenheder	\N
2047	487	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	9b447ec7-81fb-46c8-8820-3447b8a93330	\N	organisatoriskfunktionstype	\N
2048	488	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2049	488	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	0d2d249d-83ca-40f1-ac89-be7e246e7541	\N	tilknyttedebrugere	\N
2050	488	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
2051	488	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
2052	488	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	f19417e6-1f70-442a-bfbf-2ad65397d84f	\N	opgaver	\N
2053	489	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2054	489	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	0d2d249d-83ca-40f1-ac89-be7e246e7541	\N	tilknyttedebrugere	\N
2055	489	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
2056	489	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-09a1-32b8-e044-0003ba298018	adresser	DAR
2057	490	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2058	490	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	0d2d249d-83ca-40f1-ac89-be7e246e7541	\N	tilknyttedebrugere	\N
2059	490	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
2060	490	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
2061	490	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4555806405	adresser	PHONE
2062	491	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2063	491	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	0d2d249d-83ca-40f1-ac89-be7e246e7541	\N	tilknyttedebrugere	\N
2064	491	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
2065	491	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:ryans@hjorring.dk	adresser	EMAIL
2066	492	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2067	492	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	0d2d249d-83ca-40f1-ac89-be7e246e7541	\N	tilknyttedebrugere	\N
2068	492	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	\N	organisatoriskfunktionstype	\N
2069	492	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	\N	urn:text:%42ygning%203	adresser	TEXT
2070	493	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2071	493	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	0d2d249d-83ca-40f1-ac89-be7e246e7541	\N	tilknyttedebrugere	\N
2072	493	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	68746352-ef27-44e6-9bcc-30cbbaee4fb3	\N	tilknyttedeitsystemer	\N
2073	494	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2074	494	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	0d2d249d-83ca-40f1-ac89-be7e246e7541	\N	tilknyttedebrugere	\N
2075	494	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
2076	494	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	68ce5504-54ec-474f-8fed-2709442e0c9b	\N	organisatoriskfunktionstype	\N
2077	495	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2078	495	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	0d2d249d-83ca-40f1-ac89-be7e246e7541	\N	tilknyttedebrugere	\N
2079	495	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
2080	495	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	eb911cea-f1f1-4002-b584-f812022ebe39	\N	organisatoriskfunktionstype	\N
2081	496	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2082	496	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	89e4bf94-8b1d-4ae0-bca2-3465a06f9f08	\N	tilknyttedebrugere	\N
2083	496	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
2084	496	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
2085	496	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	4f5aad51-8c28-4c0d-9b17-a2a30df36849	\N	opgaver	\N
2086	497	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2087	497	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	89e4bf94-8b1d-4ae0-bca2-3465a06f9f08	\N	tilknyttedebrugere	\N
2088	497	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
2089	497	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	\N	urn:dar:0a3f50c8-4321-32b8-e044-0003ba298018	adresser	DAR
2090	498	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2091	498	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	89e4bf94-8b1d-4ae0-bca2-3465a06f9f08	\N	tilknyttedebrugere	\N
2092	498	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
2093	498	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
2094	498	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4575106836	adresser	PHONE
2095	499	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2096	499	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	89e4bf94-8b1d-4ae0-bca2-3465a06f9f08	\N	tilknyttedebrugere	\N
2097	499	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
2098	499	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:pallec@hjorring.dk	adresser	EMAIL
2099	500	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2100	500	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	89e4bf94-8b1d-4ae0-bca2-3465a06f9f08	\N	tilknyttedebrugere	\N
2101	500	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	ed1d88cd-89a8-4899-a26a-faf9393bcbb6	\N	tilknyttedeitsystemer	\N
2102	501	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2103	501	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	8ca64fe4-6231-48e9-818e-34e559a0574f	\N	tilknyttedebrugere	\N
2104	501	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
2105	501	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
2106	501	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	b617b6e7-166f-4c30-8ead-aeb360febf0e	\N	opgaver	\N
2107	502	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2108	502	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	8ca64fe4-6231-48e9-818e-34e559a0574f	\N	tilknyttedebrugere	\N
2109	502	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
2110	502	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	\N	urn:dar:0a3f50c7-ebe5-32b8-e044-0003ba298018	adresser	DAR
2111	503	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2112	503	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	8ca64fe4-6231-48e9-818e-34e559a0574f	\N	tilknyttedebrugere	\N
2113	503	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
2114	503	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
2115	503	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	\N	urn:magenta.dk:telefon:+4551248232	adresser	PHONE
2116	504	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2117	504	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	8ca64fe4-6231-48e9-818e-34e559a0574f	\N	tilknyttedebrugere	\N
2118	504	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
2119	504	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	\N	urn:mailto:edithe@hjorring.dk	adresser	EMAIL
2120	505	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2121	505	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	8ca64fe4-6231-48e9-818e-34e559a0574f	\N	tilknyttedebrugere	\N
2122	505	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	\N	organisatoriskfunktionstype	\N
2123	505	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	\N	urn:text:%42ygning%207	adresser	TEXT
2124	506	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2125	506	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	8ca64fe4-6231-48e9-818e-34e559a0574f	\N	tilknyttedebrugere	\N
2126	506	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
2127	507	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2128	507	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	8ca64fe4-6231-48e9-818e-34e559a0574f	\N	tilknyttedebrugere	\N
2129	507	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	76015baa-c0e0-4fea-82c2-9941c68fa1cd	\N	tilknyttedeitsystemer	\N
2130	508	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2131	508	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	8ca64fe4-6231-48e9-818e-34e559a0574f	\N	tilknyttedebrugere	\N
2132	508	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	d9f93150-f857-5197-bac0-d0182e165c4a	\N	tilknyttedeenheder	\N
2133	508	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
2134	508	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
2135	508	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	01f89ef8-0651-43c2-afda-e24f0d8fe05b	\N	opgaver	lederansvar
2136	508	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	91f65ddc-5eda-4b63-b7bc-506871c76181	\N	opgaver	lederansvar
2137	508	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
2138	509	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2139	509	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	03f084de-3552-4817-b15b-21a5056366d4	\N	tilknyttedebrugere	\N
2140	509	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	tilknyttedeenheder	\N
2141	509	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
2142	509	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	86964252-7c92-4337-a59c-bd847865280b	\N	opgaver	\N
2143	510	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2144	510	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	03f084de-3552-4817-b15b-21a5056366d4	\N	tilknyttedebrugere	\N
2145	510	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
2146	510	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	\N	urn:dar:0a3f50c8-4cbf-32b8-e044-0003ba298018	adresser	DAR
2147	511	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2148	511	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	03f084de-3552-4817-b15b-21a5056366d4	\N	tilknyttedebrugere	\N
2149	511	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
2150	511	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
2151	511	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4550116172	adresser	PHONE
2152	512	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2153	512	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	03f084de-3552-4817-b15b-21a5056366d4	\N	tilknyttedebrugere	\N
2154	512	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
2155	512	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	\N	urn:mailto:jelvap@hjorring.dk	adresser	EMAIL
2156	513	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2157	513	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	03f084de-3552-4817-b15b-21a5056366d4	\N	tilknyttedebrugere	\N
2158	513	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	76015baa-c0e0-4fea-82c2-9941c68fa1cd	\N	tilknyttedeitsystemer	\N
2159	514	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2160	514	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	03f084de-3552-4817-b15b-21a5056366d4	\N	tilknyttedebrugere	\N
2161	514	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
2162	515	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2163	515	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	03f084de-3552-4817-b15b-21a5056366d4	\N	tilknyttedebrugere	\N
2164	515	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	7a8e45f7-4de0-44c8-990f-43c0565ee505	\N	tilknyttedeenheder	\N
2165	515	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
2166	515	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
2167	515	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	01f89ef8-0651-43c2-afda-e24f0d8fe05b	\N	opgaver	lederansvar
2168	515	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	9f833d6c-3611-49fe-b155-71a7ba1602a2	\N	opgaver	lederansvar
2169	515	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
2170	516	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2171	516	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	17c12fbd-8816-4536-923c-cad5c749647e	\N	tilknyttedebrugere	\N
2172	516	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	a6773531-6c0a-4c7b-b0e2-77992412b610	\N	tilknyttedeenheder	\N
2173	516	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
2174	516	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	bc9f6541-1031-49ff-ab04-c1cad96a2871	\N	opgaver	\N
2175	517	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2176	517	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	17c12fbd-8816-4536-923c-cad5c749647e	\N	tilknyttedebrugere	\N
2177	517	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
2178	517	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	\N	urn:dar:367efa59-7595-4563-a4bf-d08293c03643	adresser	DAR
2179	518	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2180	518	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	17c12fbd-8816-4536-923c-cad5c749647e	\N	tilknyttedebrugere	\N
2181	518	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
2182	518	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	34dfe265-4f4d-477c-bd8c-068353085c0e	\N	opgaver	synlighed
2183	518	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	\N	urn:magenta.dk:telefon:+4515524258	adresser	PHONE
2184	519	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2185	519	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	17c12fbd-8816-4536-923c-cad5c749647e	\N	tilknyttedebrugere	\N
2186	519	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
2187	519	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	\N	urn:mailto:elsec@hjorring.dk	adresser	EMAIL
2188	520	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2189	520	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	17c12fbd-8816-4536-923c-cad5c749647e	\N	tilknyttedebrugere	\N
2190	520	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	68746352-ef27-44e6-9bcc-30cbbaee4fb3	\N	tilknyttedeitsystemer	\N
2191	521	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2192	521	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	17c12fbd-8816-4536-923c-cad5c749647e	\N	tilknyttedebrugere	\N
2193	521	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	76015baa-c0e0-4fea-82c2-9941c68fa1cd	\N	tilknyttedeitsystemer	\N
2194	522	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2195	522	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	17c12fbd-8816-4536-923c-cad5c749647e	\N	tilknyttedebrugere	\N
2196	522	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	a6773531-6c0a-4c7b-b0e2-77992412b610	\N	tilknyttedeenheder	\N
2197	522	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
2198	522	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
2199	522	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	91f65ddc-5eda-4b63-b7bc-506871c76181	\N	opgaver	lederansvar
2200	522	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	01f89ef8-0651-43c2-afda-e24f0d8fe05b	\N	opgaver	lederansvar
2201	522	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
2202	523	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2203	523	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	73e0730b-d815-45f3-aad3-1ce9873741f3	\N	tilknyttedebrugere	\N
2204	523	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
2205	523	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	706ae3a8-1976-4a1d-94c1-ab9b760bb635	\N	organisatoriskfunktionstype	\N
2206	523	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	d07ce76c-ed70-4b92-b419-84b948e17086	\N	opgaver	\N
2207	524	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2208	524	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	73e0730b-d815-45f3-aad3-1ce9873741f3	\N	tilknyttedebrugere	\N
2209	524	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	263f43f0-6863-4ad6-a125-15e929dc3475	\N	organisatoriskfunktionstype	\N
2210	524	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	\N	urn:dar:0a3f50c8-4a60-32b8-e044-0003ba298018	adresser	DAR
2211	525	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2212	525	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	73e0730b-d815-45f3-aad3-1ce9873741f3	\N	tilknyttedebrugere	\N
2213	525	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	9270ff78-e2f7-4b47-a229-7a6963469566	\N	organisatoriskfunktionstype	\N
2214	525	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	fffdfd16-d429-4e4c-98f4-d6c0826262a3	\N	opgaver	synlighed
2215	525	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	\N	urn:magenta.dk:telefon:+4517087512	adresser	PHONE
2216	526	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2217	526	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	73e0730b-d815-45f3-aad3-1ce9873741f3	\N	tilknyttedebrugere	\N
2218	526	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	413a8b3b-1a55-4e28-a877-5088c68209ee	\N	organisatoriskfunktionstype	\N
2219	526	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	\N	urn:mailto:mieh@hjorring.dk	adresser	EMAIL
2220	527	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2221	527	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	73e0730b-d815-45f3-aad3-1ce9873741f3	\N	tilknyttedebrugere	\N
2222	527	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	7c9b618a-17ae-47c6-8ec0-bdbf0ff16443	\N	organisatoriskfunktionstype	\N
2223	527	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	\N	urn:text:%42ygning%207	adresser	TEXT
2224	528	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2225	528	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	73e0730b-d815-45f3-aad3-1ce9873741f3	\N	tilknyttedebrugere	\N
2226	528	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	03120151-cd89-4fd6-9c1e-043803d90636	\N	tilknyttedeitsystemer	\N
2227	529	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2228	529	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	73e0730b-d815-45f3-aad3-1ce9873741f3	\N	tilknyttedebrugere	\N
2229	529	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	68746352-ef27-44e6-9bcc-30cbbaee4fb3	\N	tilknyttedeitsystemer	\N
2230	530	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	e89f49ae-1521-4e2e-8adb-9572d159b77f	\N	tilknyttedeorganisationer	\N
2231	530	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	73e0730b-d815-45f3-aad3-1ce9873741f3	\N	tilknyttedebrugere	\N
2232	530	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	f06ee470-9f17-566f-acbe-e938112d46d9	\N	tilknyttedeenheder	\N
2233	530	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	8020a7b0-eae6-4ca8-8abe-1005d72abd88	\N	organisatoriskfunktionstype	\N
2234	530	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	302a9818-452e-4aa7-8811-442f2b91486f	\N	opgaver	lederansvar
2235	530	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	9f833d6c-3611-49fe-b155-71a7ba1602a2	\N	opgaver	lederansvar
2236	530	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	01f89ef8-0651-43c2-afda-e24f0d8fe05b	\N	opgaver	lederansvar
2237	530	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	27e20f86-5c66-42c5-a4fb-36df770d3106	\N	opgaver	lederniveau
\.


--
-- Name: organisationfunktion_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationfunktion_relation_id_seq', 2237, true);


--
-- Data for Name: organisationfunktion_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion_tils_gyldighed (id, virkning, gyldighed, organisationfunktion_registrering_id) FROM stdin;
1	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	1
2	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	2
3	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	3
4	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	4
5	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	5
6	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	6
7	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	7
8	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	8
9	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	9
10	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	10
11	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	11
12	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	12
13	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	13
14	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	14
15	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	15
16	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	16
17	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	17
18	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	18
19	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	19
20	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	20
21	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	21
22	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	22
23	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	23
24	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	24
25	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	25
26	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	26
27	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	27
28	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	28
29	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	29
30	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	30
31	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	31
32	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	32
33	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	33
34	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	34
35	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	35
36	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	36
37	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	37
38	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	38
39	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	39
40	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	40
41	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	41
42	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	42
43	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	43
44	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	44
45	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	45
46	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	46
47	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	47
48	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	48
49	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	49
50	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	50
51	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	51
52	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	52
53	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	53
54	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	54
55	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	55
56	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	56
57	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	57
58	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	58
59	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	59
60	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	60
61	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	61
62	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	62
63	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	63
64	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	64
65	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	65
66	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	66
67	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	67
68	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	68
69	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	69
70	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	70
71	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	71
72	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	72
73	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	73
74	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	74
75	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	75
76	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	76
77	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	77
78	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	78
79	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	79
80	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	80
81	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	81
82	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	82
83	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	83
84	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	84
85	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	85
86	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	86
87	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	87
88	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	88
89	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	89
90	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	90
91	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	91
92	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	92
93	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	93
94	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	94
95	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	95
96	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	96
97	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	97
98	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	98
99	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	99
100	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	100
101	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	101
102	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	102
103	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	103
104	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	104
105	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	105
106	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	106
107	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	107
108	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	108
109	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	109
110	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	110
111	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	111
112	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	112
113	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	113
114	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	114
115	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	115
116	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	116
117	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	117
118	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	118
119	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	119
120	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	120
121	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	121
122	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	122
123	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	123
124	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	124
125	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	125
126	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	126
127	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	127
128	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	128
129	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	129
130	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	130
131	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	131
132	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	132
133	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	133
134	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	134
135	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	135
136	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	136
137	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	137
138	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	138
139	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	139
140	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	140
141	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	141
142	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	142
143	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	143
144	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	144
145	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	145
146	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	146
147	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	147
148	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	148
149	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	149
150	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	150
151	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	151
152	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	152
153	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	153
154	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	154
155	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	155
156	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	156
157	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	157
158	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	158
159	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	159
160	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	160
161	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	161
162	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	162
163	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	163
164	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	164
165	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	165
166	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	166
167	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	167
168	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	168
169	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	169
170	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	170
171	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	171
172	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	172
173	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	173
174	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	174
175	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	175
176	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	176
177	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	177
178	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	178
179	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	179
180	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	180
181	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	181
182	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	182
183	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	183
184	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	184
185	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	185
186	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	186
187	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	187
188	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	188
189	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	189
190	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	190
191	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	191
192	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	192
193	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	193
194	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	194
195	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	195
196	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	196
197	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	197
198	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	198
199	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	199
200	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	200
201	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	201
202	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	202
203	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	203
204	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	204
205	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	205
206	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	206
207	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	207
208	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	208
209	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	209
210	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	210
211	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	211
212	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	212
213	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	213
214	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	214
215	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	215
216	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	216
217	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	217
218	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	218
219	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	219
220	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	220
221	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	221
222	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	222
223	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	223
224	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	224
225	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	225
226	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	226
227	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	227
228	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	228
229	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	229
230	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	230
231	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	231
232	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	232
233	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	233
234	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	234
235	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	235
236	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	236
237	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	237
238	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	238
239	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	239
240	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	240
241	("[""1960-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	241
242	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	Aktiv	242
243	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	Aktiv	243
244	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	Aktiv	244
245	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	Aktiv	245
246	("[""1975-12-08 00:00:00+01"",""1996-04-22 00:00:00+02"")",,,"")	Aktiv	246
247	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	Aktiv	247
248	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	Aktiv	248
249	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	Aktiv	249
250	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	Aktiv	250
251	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	Aktiv	251
252	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	Aktiv	252
253	("[""1967-07-23 00:00:00+01"",infinity)",,,"")	Aktiv	253
254	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	Aktiv	254
255	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	Aktiv	255
256	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	Aktiv	256
257	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	Aktiv	257
258	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	Aktiv	258
259	("[""1980-06-14 00:00:00+02"",""2007-10-22 00:00:00+02"")",,,"")	Aktiv	259
260	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	Aktiv	260
261	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	Aktiv	261
262	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	Aktiv	262
263	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	Aktiv	263
264	("[""1980-11-11 00:00:00+01"",infinity)",,,"")	Aktiv	264
265	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	Aktiv	265
266	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	Aktiv	266
267	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	Aktiv	267
268	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	Aktiv	268
269	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	Aktiv	269
270	("[""2010-10-05 00:00:00+02"",""2029-11-25 00:00:00+01"")",,,"")	Aktiv	270
271	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	Aktiv	271
272	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	Aktiv	272
273	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	Aktiv	273
274	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	Aktiv	274
275	("[""2006-01-29 00:00:00+01"",""2045-03-06 00:00:00+01"")",,,"")	Aktiv	275
276	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	Aktiv	276
277	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	Aktiv	277
278	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	Aktiv	278
279	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	Aktiv	279
280	("[""1991-11-14 00:00:00+01"",infinity)",,,"")	Aktiv	280
281	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	Aktiv	281
282	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	Aktiv	282
283	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	Aktiv	283
284	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	Aktiv	284
285	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	Aktiv	285
286	("[""1964-11-05 00:00:00+01"",infinity)",,,"")	Aktiv	286
287	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	Aktiv	287
288	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	Aktiv	288
289	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	Aktiv	289
290	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	Aktiv	290
291	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	Aktiv	291
292	("[""1994-02-01 00:00:00+01"",""2002-11-17 00:00:00+01"")",,,"")	Aktiv	292
293	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	Aktiv	293
294	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	Aktiv	294
295	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	Aktiv	295
296	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	Aktiv	296
297	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	Aktiv	297
298	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	Aktiv	298
299	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	Aktiv	299
300	("[""1962-01-20 00:00:00+01"",infinity)",,,"")	Aktiv	300
301	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	Aktiv	301
302	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	Aktiv	302
303	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	Aktiv	303
304	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	Aktiv	304
305	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	Aktiv	305
306	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	Aktiv	306
307	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	Aktiv	307
308	("[""1986-03-15 00:00:00+01"",infinity)",,,"")	Aktiv	308
309	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	Aktiv	309
310	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	Aktiv	310
311	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	Aktiv	311
312	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	Aktiv	312
313	("[""1976-05-06 00:00:00+01"",""1998-01-12 00:00:00+01"")",,,"")	Aktiv	313
314	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	Aktiv	314
315	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	Aktiv	315
316	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	Aktiv	316
317	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	Aktiv	317
318	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	Aktiv	318
319	("[""2021-04-10 00:00:00+02"",infinity)",,,"")	Aktiv	319
320	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	Aktiv	320
321	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	Aktiv	321
322	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	Aktiv	322
323	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	Aktiv	323
324	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	Aktiv	324
325	("[""2021-03-11 00:00:00+01"",infinity)",,,"")	Aktiv	325
326	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	Aktiv	326
327	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	Aktiv	327
328	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	Aktiv	328
329	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	Aktiv	329
330	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	Aktiv	330
331	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	Aktiv	331
332	("[""2018-06-25 00:00:00+02"",infinity)",,,"")	Aktiv	332
333	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	Aktiv	333
334	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	Aktiv	334
335	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	Aktiv	335
336	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	Aktiv	336
337	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	Aktiv	337
338	("[""1960-01-31 00:00:00+01"",""1980-04-16 00:00:00+02"")",,,"")	Aktiv	338
339	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	Aktiv	339
340	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	Aktiv	340
341	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	Aktiv	341
342	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	Aktiv	342
343	("[""2014-04-17 00:00:00+02"",infinity)",,,"")	Aktiv	343
344	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	Aktiv	344
345	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	Aktiv	345
346	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	Aktiv	346
347	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	Aktiv	347
348	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	Aktiv	348
349	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	Aktiv	349
350	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	Aktiv	350
351	("[""1991-06-17 00:00:00+02"",""2013-05-23 00:00:00+02"")",,,"")	Aktiv	351
352	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	Aktiv	352
353	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	Aktiv	353
354	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	Aktiv	354
355	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	Aktiv	355
356	("[""1988-09-30 00:00:00+01"",infinity)",,,"")	Aktiv	356
357	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	Aktiv	357
358	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	Aktiv	358
359	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	Aktiv	359
360	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	Aktiv	360
361	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	Aktiv	361
362	("[""2012-12-23 00:00:00+01"",infinity)",,,"")	Aktiv	362
363	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	Aktiv	363
364	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	Aktiv	364
365	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	Aktiv	365
366	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	Aktiv	366
367	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	Aktiv	367
368	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	Aktiv	368
369	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	Aktiv	369
370	("[""2008-09-15 00:00:00+02"",infinity)",,,"")	Aktiv	370
371	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	Aktiv	371
372	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	Aktiv	372
373	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	Aktiv	373
374	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	Aktiv	374
375	("[""2008-10-15 00:00:00+02"",infinity)",,,"")	Aktiv	375
376	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	Aktiv	376
377	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	Aktiv	377
378	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	Aktiv	378
379	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	Aktiv	379
380	("[""1996-05-21 00:00:00+02"",infinity)",,,"")	Aktiv	380
381	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	Aktiv	381
382	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	Aktiv	382
383	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	Aktiv	383
384	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	Aktiv	384
385	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	Aktiv	385
386	("[""1975-03-13 00:00:00+01"",infinity)",,,"")	Aktiv	386
387	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	Aktiv	387
388	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	Aktiv	388
389	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	Aktiv	389
390	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	Aktiv	390
391	("[""1983-12-26 00:00:00+01"",infinity)",,,"")	Aktiv	391
392	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	Aktiv	392
393	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	Aktiv	393
394	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	Aktiv	394
395	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	Aktiv	395
396	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	Aktiv	396
397	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	Aktiv	397
398	("[""1973-04-22 00:00:00+01"",infinity)",,,"")	Aktiv	398
399	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	Aktiv	399
400	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	Aktiv	400
401	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	Aktiv	401
402	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	Aktiv	402
403	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	Aktiv	403
404	("[""1966-07-28 00:00:00+01"",infinity)",,,"")	Aktiv	404
405	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	Aktiv	405
406	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	Aktiv	406
407	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	Aktiv	407
408	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	Aktiv	408
409	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	Aktiv	409
410	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	Aktiv	410
411	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	Aktiv	411
412	("[""2008-08-16 00:00:00+02"",infinity)",,,"")	Aktiv	412
413	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	Aktiv	413
414	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	Aktiv	414
415	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	Aktiv	415
416	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	Aktiv	416
417	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	Aktiv	417
418	("[""1974-06-16 00:00:00+01"",""1995-10-25 00:00:00+01"")",,,"")	Aktiv	418
419	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	Aktiv	419
420	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	Aktiv	420
421	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	Aktiv	421
422	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	Aktiv	422
423	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	Aktiv	423
424	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	Aktiv	424
425	("[""1973-02-21 00:00:00+01"",infinity)",,,"")	Aktiv	425
426	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	Aktiv	426
427	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	Aktiv	427
428	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	Aktiv	428
429	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	Aktiv	429
430	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	Aktiv	430
431	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	Aktiv	431
432	("[""2014-03-18 00:00:00+01"",infinity)",,,"")	Aktiv	432
433	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	Aktiv	433
434	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	Aktiv	434
435	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	Aktiv	435
436	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	Aktiv	436
437	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	Aktiv	437
438	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	Aktiv	438
439	("[""2018-04-26 00:00:00+02"",infinity)",,,"")	Aktiv	439
440	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	Aktiv	440
441	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	Aktiv	441
442	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	Aktiv	442
443	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	Aktiv	443
444	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	Aktiv	444
445	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	Aktiv	445
446	("[""2010-03-09 00:00:00+01"",infinity)",,,"")	Aktiv	446
447	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	Aktiv	447
448	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	Aktiv	448
449	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	Aktiv	449
450	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	Aktiv	450
451	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	Aktiv	451
452	("[""2020-06-14 00:00:00+02"",infinity)",,,"")	Aktiv	452
453	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	Aktiv	453
454	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	Aktiv	454
455	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	Aktiv	455
456	("[""2016-02-06 00:00:00+01"",infinity)",,,"")	Aktiv	456
457	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	Aktiv	457
458	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	Aktiv	458
459	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	Aktiv	459
460	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	Aktiv	460
461	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	Aktiv	461
462	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	Aktiv	462
463	("[""1971-04-03 00:00:00+01"",""1984-09-22 00:00:00+02"")",,,"")	Aktiv	463
464	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	Aktiv	464
465	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	Aktiv	465
466	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	Aktiv	466
467	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	Aktiv	467
468	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	Aktiv	468
469	("[""1993-10-04 00:00:00+01"",infinity)",,,"")	Aktiv	469
470	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	Aktiv	470
471	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	Aktiv	471
472	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	Aktiv	472
473	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	Aktiv	473
474	("[""2006-11-25 00:00:00+01"",infinity)",,,"")	Aktiv	474
475	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	Aktiv	475
476	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	Aktiv	476
477	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	Aktiv	477
478	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	Aktiv	478
479	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	Aktiv	479
480	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	Aktiv	480
481	("[""2000-08-28 00:00:00+02"",infinity)",,,"")	Aktiv	481
482	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	Aktiv	482
483	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	Aktiv	483
484	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	Aktiv	484
485	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	Aktiv	485
486	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	Aktiv	486
487	("[""1966-08-27 00:00:00+01"",infinity)",,,"")	Aktiv	487
488	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	Aktiv	488
489	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	Aktiv	489
490	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	Aktiv	490
491	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	Aktiv	491
492	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	Aktiv	492
493	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	Aktiv	493
494	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	Aktiv	494
495	("[""1976-04-06 00:00:00+01"",infinity)",,,"")	Aktiv	495
496	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	Aktiv	496
497	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	Aktiv	497
498	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	Aktiv	498
499	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	Aktiv	499
500	("[""2004-10-06 00:00:00+02"",infinity)",,,"")	Aktiv	500
501	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	Aktiv	501
502	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	Aktiv	502
503	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	Aktiv	503
504	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	Aktiv	504
505	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	Aktiv	505
506	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	Aktiv	506
507	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	Aktiv	507
508	("[""2011-07-02 00:00:00+02"",""2026-07-14 00:00:00+02"")",,,"")	Aktiv	508
509	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	Aktiv	509
510	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	Aktiv	510
511	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	Aktiv	511
512	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	Aktiv	512
513	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	Aktiv	513
514	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	Aktiv	514
515	("[""1976-01-07 00:00:00+01"",infinity)",,,"")	Aktiv	515
516	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	Aktiv	516
517	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	Aktiv	517
518	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	Aktiv	518
519	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	Aktiv	519
520	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	Aktiv	520
521	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	Aktiv	521
522	("[""2021-06-09 00:00:00+02"",infinity)",,,"")	Aktiv	522
523	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	Aktiv	523
524	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	Aktiv	524
525	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	Aktiv	525
526	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	Aktiv	526
527	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	Aktiv	527
528	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	Aktiv	528
529	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	Aktiv	529
530	("[""2000-07-29 00:00:00+02"",""2027-08-08 00:00:00+02"")",,,"")	Aktiv	530
\.


--
-- Name: organisationfunktion_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationfunktion_tils_gyldighed_id_seq', 530, true);


--
-- Data for Name: sag; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.sag (id) FROM stdin;
\.


--
-- Data for Name: sag_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.sag_registrering (id, sag_id, registrering) FROM stdin;
\.


--
-- Data for Name: sag_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.sag_attr_egenskaber (id, brugervendtnoegle, afleveret, beskrivelse, hjemmel, kassationskode, offentlighedundtaget, principiel, sagsnummer, titel, integrationsdata, virkning, sag_registrering_id) FROM stdin;
\.


--
-- Name: sag_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.sag_attr_egenskaber_id_seq', 1, false);


--
-- Name: sag_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.sag_registrering_id_seq', 1, false);


--
-- Data for Name: sag_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.sag_relation (id, sag_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type, rel_index, rel_type_spec, journal_notat, journal_dokument_attr) FROM stdin;
\.


--
-- Name: sag_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.sag_relation_id_seq', 1, false);


--
-- Data for Name: sag_tils_fremdrift; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.sag_tils_fremdrift (id, virkning, fremdrift, sag_registrering_id) FROM stdin;
\.


--
-- Name: sag_tils_fremdrift_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.sag_tils_fremdrift_id_seq', 1, false);


--
-- Data for Name: tilstand; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.tilstand (id) FROM stdin;
\.


--
-- Data for Name: tilstand_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.tilstand_registrering (id, tilstand_id, registrering) FROM stdin;
\.


--
-- Data for Name: tilstand_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.tilstand_attr_egenskaber (id, brugervendtnoegle, beskrivelse, integrationsdata, virkning, tilstand_registrering_id) FROM stdin;
\.


--
-- Name: tilstand_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.tilstand_attr_egenskaber_id_seq', 1, false);


--
-- Name: tilstand_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.tilstand_registrering_id_seq', 1, false);


--
-- Data for Name: tilstand_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.tilstand_relation (id, tilstand_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type, rel_index, tilstand_vaerdi_attr) FROM stdin;
\.


--
-- Name: tilstand_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.tilstand_relation_id_seq', 1, false);


--
-- Data for Name: tilstand_tils_publiceret; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.tilstand_tils_publiceret (id, virkning, publiceret, tilstand_registrering_id) FROM stdin;
\.


--
-- Name: tilstand_tils_publiceret_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.tilstand_tils_publiceret_id_seq', 1, false);


--
-- Data for Name: tilstand_tils_status; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.tilstand_tils_status (id, virkning, status, tilstand_registrering_id) FROM stdin;
\.


--
-- Name: tilstand_tils_status_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.tilstand_tils_status_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

