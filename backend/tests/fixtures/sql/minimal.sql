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
53181ed2-f1de-4c4a-a8fd-ab358c2c454a
6ee24785-ee9a-4502-81c2-7697009c9053
\.


--
-- Data for Name: bruger_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.bruger_registrering (id, bruger_id, registrering) FROM stdin;
1	53181ed2-f1de-4c4a-a8fd-ab358c2c454a	("[""2019-03-18 17:50:51.78563+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
2	6ee24785-ee9a-4502-81c2-7697009c9053	("[""2019-03-18 17:50:51.808375+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
\.


--
-- Data for Name: bruger_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.bruger_attr_egenskaber (id, brugervendtnoegle, brugernavn, brugertype, integrationsdata, virkning, bruger_registrering_id) FROM stdin;
1	andersand	Anders And	\N	\N	("[""1934-06-09 00:00:00+01"",infinity)",,,"")	1
2	fedtmule	Fedtmule	\N	\N	("[""1932-05-12 00:00:00+01"",infinity)",,,"")	2
\.


--
-- Name: bruger_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.bruger_attr_egenskaber_id_seq', 2, true);

--
-- Data for Name: bruger_attr_udvidelser; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.bruger_attr_udvidelser (id, fornavn, efternavn, virkning, bruger_registrering_id) FROM stdin;
1	Anders	And	("[""1934-06-09 00:00:00+01"",infinity)",,,"")	1
2	Fedtmule	Hest	("[""1932-05-12 00:00:00+01"",infinity)",,,"")	2
\.


--
-- Name: bruger_attr_udvidelser_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.bruger_attr_udvidelser_id_seq', 2, true);


--
-- Name: bruger_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.bruger_registrering_id_seq', 2, true);


--
-- Data for Name: bruger_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.bruger_relation (id, bruger_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""1934-06-09 00:00:00+01"",infinity)",,,"")	\N	urn:email	brugertyper	\N
2	1	("[""1934-06-09 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilhoerer	\N
3	1	("[""1934-06-09 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:0906340000	tilknyttedepersoner	\N
4	2	("[""1932-05-12 00:00:00+01"",infinity)",,,"")	\N	urn:email	brugertyper	\N
5	2	("[""1932-05-12 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilhoerer	\N
6	2	("[""1932-05-12 00:00:00+01"",infinity)",,,"")	\N	urn:dk:cpr:person:1205320000	tilknyttedepersoner	\N
\.


--
-- Name: bruger_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.bruger_relation_id_seq', 6, true);


--
-- Data for Name: bruger_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.bruger_tils_gyldighed (id, virkning, gyldighed, bruger_registrering_id) FROM stdin;
1	("[""1934-06-09 00:00:00+01"",infinity)",,,"")	Aktiv	1
2	("[""1932-05-12 00:00:00+01"",infinity)",,,"")	Aktiv	2
\.


--
-- Name: bruger_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.bruger_tils_gyldighed_id_seq', 2, true);


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
fc917e7c-fc3b-47c2-8aa5-a0383342a280
e337bab4-635f-49ce-aa31-b44047a43aa1
ef71fe9c-7901-48e2-86d8-84116e210202
\.


--
-- Data for Name: facet_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.facet_registrering (id, facet_id, registrering) FROM stdin;
1	fc917e7c-fc3b-47c2-8aa5-a0383342a280	("[""2019-03-18 17:50:51.554678+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
2	e337bab4-635f-49ce-aa31-b44047a43aa1	("[""2019-03-18 17:50:51.573412+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
3	ef71fe9c-7901-48e2-86d8-84116e210202	("[""2019-03-18 17:50:51.586648+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
\.


--
-- Data for Name: facet_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.facet_attr_egenskaber (id, brugervendtnoegle, beskrivelse, opbygning, ophavsret, plan, supplement, retskilde, integrationsdata, virkning, facet_registrering_id) FROM stdin;
1	org_unit_type	\N	\N	\N	\N	\N	\N	\N	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	1
2	address_type	\N	\N	\N	\N	\N	\N	\N	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	2
3	association_type	\N	\N	\N	\N	\N	\N	\N	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	3
\.


--
-- Name: facet_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.facet_attr_egenskaber_id_seq', 3, true);


--
-- Name: facet_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.facet_registrering_id_seq', 3, true);


--
-- Data for Name: facet_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.facet_relation (id, facet_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	cdeecc2f-5f96-4a2c-b5df-a59d3a04de59	\N	facettilhoerer	klassifikation
2	1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	ansvarlig	organisation
3	2	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	cdeecc2f-5f96-4a2c-b5df-a59d3a04de59	\N	facettilhoerer	klassifikation
4	2	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	ansvarlig	organisation
5	3	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	cdeecc2f-5f96-4a2c-b5df-a59d3a04de59	\N	facettilhoerer	klassifikation
6	3	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	ansvarlig	organisation
\.


--
-- Name: facet_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.facet_relation_id_seq', 6, true);


--
-- Data for Name: facet_tils_publiceret; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.facet_tils_publiceret (id, virkning, publiceret, facet_registrering_id) FROM stdin;
1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	1
2	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	2
3	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	3
\.


--
-- Name: facet_tils_publiceret_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.facet_tils_publiceret_id_seq', 3, true);


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
59c135c9-2b15-41cc-97c8-b5dff7180beb
0872fb72-926d-4c5c-a063-ff800b8ee697
\.


--
-- Data for Name: itsystem_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.itsystem_registrering (id, itsystem_id, registrering) FROM stdin;
1	59c135c9-2b15-41cc-97c8-b5dff7180beb	("[""2019-03-18 17:50:51.826608+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
2	0872fb72-926d-4c5c-a063-ff800b8ee697	("[""2019-03-18 17:50:51.851014+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"")
\.


--
-- Data for Name: itsystem_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.itsystem_attr_egenskaber (id, brugervendtnoegle, itsystemnavn, itsystemtype, konfigurationreference, integrationsdata, virkning, itsystem_registrering_id) FROM stdin;
1	AD	Active Directory	\N	\N	\N	("[""2002-02-14 00:00:00+01"",infinity)",,,"")	1
2	LoRa	Lokal Rammearkitektur	\N	\N	\N	("[""2010-01-01 00:00:00+01"",infinity)",,,"")	2
\.


--
-- Name: itsystem_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.itsystem_attr_egenskaber_id_seq', 2, true);


--
-- Name: itsystem_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.itsystem_registrering_id_seq', 2, true);


--
-- Data for Name: itsystem_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.itsystem_relation (id, itsystem_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""2002-02-14 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilhoerer	\N
2	2	("[""2010-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilhoerer	\N
\.


--
-- Name: itsystem_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.itsystem_relation_id_seq', 2, true);


--
-- Data for Name: itsystem_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.itsystem_tils_gyldighed (id, virkning, gyldighed, itsystem_registrering_id) FROM stdin;
1	("[""2002-02-14 00:00:00+01"",infinity)",,,"")	Aktiv	1
2	("[""2010-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	2
\.


--
-- Name: itsystem_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.itsystem_tils_gyldighed_id_seq', 2, true);


--
-- Data for Name: klasse; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse (id) FROM stdin;
32547559-cfc1-4d97-94c6-70b192eff825
\.


--
-- Data for Name: klasse_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse_registrering (id, klasse_id, registrering) FROM stdin;
1	32547559-cfc1-4d97-94c6-70b192eff825	("[""2019-03-18 17:50:51.603317+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
\.


--
-- Data for Name: klasse_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse_attr_egenskaber (id, brugervendtnoegle, beskrivelse, eksempel, omfang, titel, retskilde, aendringsnotat, integrationsdata, virkning, klasse_registrering_id) FROM stdin;
1	afd	Dette er en afdeling	\N	\N	Afdeling	\N	\N	\N	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	1
\.


--
-- Name: klasse_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klasse_attr_egenskaber_id_seq', 1, true);


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

SELECT pg_catalog.setval('actual_state.klasse_registrering_id_seq', 1, true);


--
-- Data for Name: klasse_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse_relation (id, klasse_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	ansvarlig	organisation
2	1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	fc917e7c-fc3b-47c2-8aa5-a0383342a280	\N	facet	facet
\.


--
-- Name: klasse_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klasse_relation_id_seq', 2, true);


--
-- Data for Name: klasse_tils_publiceret; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klasse_tils_publiceret (id, virkning, publiceret, klasse_registrering_id) FROM stdin;
1	("[""1900-01-01 00:00:00+01"",infinity)",,,"")	Publiceret	1
\.


--
-- Name: klasse_tils_publiceret_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klasse_tils_publiceret_id_seq', 1, true);


--
-- Data for Name: klassifikation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klassifikation (id) FROM stdin;
\.


--
-- Data for Name: klassifikation_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klassifikation_registrering (id, klassifikation_id, registrering) FROM stdin;
\.


--
-- Data for Name: klassifikation_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klassifikation_attr_egenskaber (id, brugervendtnoegle, beskrivelse, kaldenavn, ophavsret, integrationsdata, virkning, klassifikation_registrering_id) FROM stdin;
\.


--
-- Name: klassifikation_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klassifikation_attr_egenskaber_id_seq', 1, false);


--
-- Name: klassifikation_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klassifikation_registrering_id_seq', 1, false);


--
-- Data for Name: klassifikation_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klassifikation_relation (id, klassifikation_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
\.


--
-- Name: klassifikation_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klassifikation_relation_id_seq', 1, false);


--
-- Data for Name: klassifikation_tils_publiceret; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.klassifikation_tils_publiceret (id, virkning, publiceret, klassifikation_registrering_id) FROM stdin;
\.


--
-- Name: klassifikation_tils_publiceret_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.klassifikation_tils_publiceret_id_seq', 1, false);


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
456362c4-0ee4-4e5e-a72c-751239745e62
\.


--
-- Data for Name: organisation_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisation_registrering (id, organisation_id, registrering) FROM stdin;
1	456362c4-0ee4-4e5e-a72c-751239745e62	("[""2019-03-18 17:50:51.533888+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
\.


--
-- Data for Name: organisation_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisation_attr_egenskaber (id, brugervendtnoegle, organisationsnavn, integrationsdata, virkning, organisation_registrering_id) FROM stdin;
1	AU	Aarhus Universitet	\N	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	1
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
1	1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	\N	urn:dk:kommune:751	myndighed	\N
\.


--
-- Name: organisation_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisation_relation_id_seq', 1, true);


--
-- Data for Name: organisation_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisation_tils_gyldighed (id, virkning, gyldighed, organisation_registrering_id) FROM stdin;
1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	1
\.


--
-- Name: organisation_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisation_tils_gyldighed_id_seq', 1, true);


--
-- Data for Name: organisationenhed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationenhed (id) FROM stdin;
2874e1dc-85e6-4269-823a-e1125484dfd3
\.


--
-- Data for Name: organisationenhed_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationenhed_registrering (id, organisationenhed_id, registrering) FROM stdin;
1	2874e1dc-85e6-4269-823a-e1125484dfd3	("[""2019-03-18 17:50:51.627687+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
\.


--
-- Data for Name: organisationenhed_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationenhed_attr_egenskaber (id, brugervendtnoegle, enhedsnavn, integrationsdata, virkning, organisationenhed_registrering_id) FROM stdin;
1	root	Overordnet Enhed	\N	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	1
\.


--
-- Name: organisationenhed_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationenhed_attr_egenskaber_id_seq', 1, true);


--
-- Name: organisationenhed_registrering_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationenhed_registrering_id_seq', 1, true);


--
-- Data for Name: organisationenhed_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationenhed_relation (id, organisationenhed_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	overordnet	\N
2	1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilhoerer	\N
3	1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	32547559-cfc1-4d97-94c6-70b192eff825	\N	enhedstype	\N
\.


--
-- Name: organisationenhed_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationenhed_relation_id_seq', 3, true);


--
-- Data for Name: organisationenhed_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationenhed_tils_gyldighed (id, virkning, gyldighed, organisationenhed_registrering_id) FROM stdin;
1	("[""2016-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	1
\.


--
-- Name: organisationenhed_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationenhed_tils_gyldighed_id_seq', 1, true);


--
-- Data for Name: organisationfunktion; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion (id) FROM stdin;
d000591f-8705-4324-897a-075e3623f37b
c2153d5d-4a2b-492d-a18c-c498f7bb6221
1b20d0b9-96a0-42a6-b196-293bb86e62e8
b807628c-030c-4f5f-a438-de41c1f26ba5
05609702-977f-4869-9fb4-50ad74c6999a
aaa8c495-d7d4-4af1-b33a-f4cb27b82c66
cd4dcccb-5bf7-4c6b-9e1a-f6ebb193e276
daa77a4d-6500-483d-b099-2c2eb7fa7a76
5c68402c-2a8d-4776-9237-16349fc72648
\.


--
-- Data for Name: organisationfunktion_registrering; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion_registrering (id, organisationfunktion_id, registrering) FROM stdin;
1	d000591f-8705-4324-897a-075e3623f37b	("[""2019-03-18 17:50:51.649843+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
2	c2153d5d-4a2b-492d-a18c-c498f7bb6221	("[""2019-03-18 17:50:51.669407+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
3	1b20d0b9-96a0-42a6-b196-293bb86e62e8	("[""2019-03-18 17:50:51.684009+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
4	b807628c-030c-4f5f-a438-de41c1f26ba5	("[""2019-03-18 17:50:51.698965+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
5	05609702-977f-4869-9fb4-50ad74c6999a	("[""2019-03-18 17:50:51.713252+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
6	aaa8c495-d7d4-4af1-b33a-f4cb27b82c66	("[""2019-03-18 17:50:51.727102+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
7	cd4dcccb-5bf7-4c6b-9e1a-f6ebb193e276	("[""2019-03-18 17:50:51.741458+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
8	daa77a4d-6500-483d-b099-2c2eb7fa7a76	("[""2019-03-18 17:50:51.754838+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
9	5c68402c-2a8d-4776-9237-16349fc72648	("[""2019-03-18 17:50:51.768475+01"",infinity)",Importeret,42c432e8-9c4a-11e6-9f62-873cf34a735f,"Automatisk indlæsning")
\.


--
-- Data for Name: organisationfunktion_attr_egenskaber; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion_attr_egenskaber (id, brugervendtnoegle, funktionsnavn, integrationsdata, virkning, organisationfunktion_registrering_id) FROM stdin;
1	bvn	Engagement	\N	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	1
2	bvn	Tilknytning	\N	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	2
3	bvn	Rolle	\N	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	3
4	bvn	Orlov	\N	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	4
5	be736ee5-5c44-4ed9-b4a4-15ffa19e2848	Leder	\N	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	5
6	donald	IT-system	\N	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	6
7	fwaf	IT-system	\N	("[""2017-01-01 00:00:00+01"",""2018-01-01 00:00:00+01"")",,,"")	7
8	rod <-> fil	Relateret Enhed	\N	("[""2017-01-01 00:00:00+01"",""2019-01-01 00:00:00+01"")",,,"")	8
9	rod <-> hum	Relateret Enhed	\N	("[""2016-06-01 00:00:00+02"",infinity)",,,"")	9
\.


--
-- Name: organisationfunktion_attr_egenskaber_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationfunktion_attr_egenskaber_id_seq', 9, true);


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

SELECT pg_catalog.setval('actual_state.organisationfunktion_registrering_id_seq', 9, true);


--
-- Data for Name: organisationfunktion_relation; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion_relation (id, organisationfunktion_registrering_id, virkning, rel_maal_uuid, rel_maal_urn, rel_type, objekt_type) FROM stdin;
1	1	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	32547559-cfc1-4d97-94c6-70b192eff825	\N	organisatoriskfunktionstype	\N
2	1	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	4311e351-6a3c-4e7e-ae60-8a3b2938fbd6	\N	opgaver	\N
3	1	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	53181ed2-f1de-4c4a-a8fd-ab358c2c454a	\N	tilknyttedebrugere	\N
4	1	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	9d07123e-47ac-4a9a-88c8-da82e3a4bc9e	\N	tilknyttedeenheder	\N
5	1	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilknyttedeorganisationer	\N
6	2	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	32547559-cfc1-4d97-94c6-70b192eff825	\N	organisatoriskfunktionstype	\N
7	2	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	53181ed2-f1de-4c4a-a8fd-ab358c2c454a	\N	tilknyttedebrugere	\N
8	2	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	9d07123e-47ac-4a9a-88c8-da82e3a4bc9e	\N	tilknyttedeenheder	\N
9	2	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilknyttedeorganisationer	\N
10	3	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	32547559-cfc1-4d97-94c6-70b192eff825	\N	organisatoriskfunktionstype	\N
11	3	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	53181ed2-f1de-4c4a-a8fd-ab358c2c454a	\N	tilknyttedebrugere	\N
12	3	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	9d07123e-47ac-4a9a-88c8-da82e3a4bc9e	\N	tilknyttedeenheder	\N
13	3	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilknyttedeorganisationer	\N
14	4	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	32547559-cfc1-4d97-94c6-70b192eff825	\N	organisatoriskfunktionstype	\N
15	4	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	53181ed2-f1de-4c4a-a8fd-ab358c2c454a	\N	tilknyttedebrugere	\N
16	4	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilknyttedeorganisationer	\N
17	5	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	32547559-cfc1-4d97-94c6-70b192eff825	\N	organisatoriskfunktionstype	\N
18	5	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	414044e0-fe5f-4f82-be20-1e107ad50e80	\N	tilknyttedefunktioner	\N
19	5	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	4311e351-6a3c-4e7e-ae60-8a3b2938fbd6	\N	opgaver	lederansvar
20	5	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	ca76a441-6226-404f-88a9-31e02e420e52	\N	opgaver	lederniveau
21	5	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	53181ed2-f1de-4c4a-a8fd-ab358c2c454a	\N	tilknyttedebrugere	\N
22	5	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	9d07123e-47ac-4a9a-88c8-da82e3a4bc9e	\N	tilknyttedeenheder	\N
23	5	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilknyttedeorganisationer	\N
24	6	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	53181ed2-f1de-4c4a-a8fd-ab358c2c454a	\N	tilknyttedebrugere	\N
25	6	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	59c135c9-2b15-41cc-97c8-b5dff7180beb	\N	tilknyttedeitsystemer	\N
26	6	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilknyttedeorganisationer	\N
27	7	("[""2017-01-01 00:00:00+01"",""2018-01-01 00:00:00+01"")",,,"")	04c78fc2-72d2-4d02-b55f-807af19eac48	\N	tilknyttedeenheder	\N
28	7	("[""2017-01-01 00:00:00+01"",""2018-01-01 00:00:00+01"")",,,"")	0872fb72-926d-4c5c-a063-ff800b8ee697	\N	tilknyttedeitsystemer	\N
29	7	("[""2017-01-01 00:00:00+01"",""2018-01-01 00:00:00+01"")",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilknyttedeorganisationer	\N
30	8	("[""2017-01-01 00:00:00+01"",""2019-01-01 00:00:00+01"")",,,"")	2874e1dc-85e6-4269-823a-e1125484dfd3	\N	tilknyttedeenheder	organisationenhed
31	8	("[""2017-01-01 00:00:00+01"",""2019-01-01 00:00:00+01"")",,,"")	da77153e-30f3-4dc2-a611-ee912a28d8aa	\N	tilknyttedeenheder	organisationenhed
32	8	("[""2017-01-01 00:00:00+01"",""2019-01-01 00:00:00+01"")",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilknyttedeorganisationer	\N
33	9	("[""2016-06-01 00:00:00+02"",infinity)",,,"")	2874e1dc-85e6-4269-823a-e1125484dfd3	\N	tilknyttedeenheder	organisationenhed
34	9	("[""2016-06-01 00:00:00+02"",infinity)",,,"")	9d07123e-47ac-4a9a-88c8-da82e3a4bc9e	\N	tilknyttedeenheder	organisationenhed
35	9	("[""2016-06-01 00:00:00+02"",infinity)",,,"")	456362c4-0ee4-4e5e-a72c-751239745e62	\N	tilknyttedeorganisationer	\N
\.


--
-- Name: organisationfunktion_relation_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationfunktion_relation_id_seq', 35, true);


--
-- Data for Name: organisationfunktion_tils_gyldighed; Type: TABLE DATA; Schema: actual_state; Owner: mox
--

COPY actual_state.organisationfunktion_tils_gyldighed (id, virkning, gyldighed, organisationfunktion_registrering_id) FROM stdin;
1	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	1
2	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	2
3	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	3
4	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	4
5	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	5
6	("[""2017-01-01 00:00:00+01"",infinity)",,,"")	Aktiv	6
7	("[""2017-01-01 00:00:00+01"",""2018-01-01 00:00:00+01"")",,,"")	Aktiv	7
8	("[""2017-01-01 00:00:00+01"",""2019-01-01 00:00:00+01"")",,,"")	Aktiv	8
9	("[""2016-06-01 00:00:00+02"",infinity)",,,"")	Aktiv	9
\.


--
-- Name: organisationfunktion_tils_gyldighed_id_seq; Type: SEQUENCE SET; Schema: actual_state; Owner: mox
--

SELECT pg_catalog.setval('actual_state.organisationfunktion_tils_gyldighed_id_seq', 9, true);


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

