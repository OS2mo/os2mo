# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Drop unused tables."""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9525559842d6"
down_revision = "699bd68b7e73"
branch_labels = None
depends_on = None


def upgrade():
    table_constraints = {
        # Aktivitet
        "aktivitet_relation": [
            "aktivitet_relation_aktoer_repr_either_uri_or_urn",
            "aktivitet_relation_no_virkning_overlap",
        ],
        # Dokument
        "dokument_relation": ["dokument_relation_no_virkning_overlap"],
        # Indsats
        "indsats_relation": ["indsats_relation_no_virkning_overlap"],
        # Interessefaellesskab
        "interessefaellesskab_relation": [
            "interessefaellesskab_relation_no_virkning_overlap"
        ],
        # Loghaendelse
        "loghaendelse_relation": ["loghaendelse_relation_no_virkning_overlap"],
        # Sag
        "sag_relation": ["sag_relation_no_virkning_overlap"],
        # Tilstand
        "tilstand_relation": ["tilstand_relation_no_virkning_overlap"],
    }

    functions = [
        # Aktivitet
        "_aktivitet_aktoer_attr_repr_urn_to_text",
        "_aktivitet_aktoer_attr_repr_uuid_to_text",
        "_as_convert_aktivitet_relation_kode_to_txt",
        "_as_create_aktivitet_registrering",
        "_as_filter_unauth_aktivitet",
        "_as_get_prev_aktivitet_registrering",
        "_as_sorted_aktivitet",
        "as_create_or_import_aktivitet",
        "as_list_aktivitet",
        "as_read_aktivitet",
        "as_search_aktivitet",
        "as_update_aktivitet",
        # Dokument
        "_as_convert_dokument_relation_kode_to_txt",
        "_as_create_dokument_registrering",
        "_as_filter_unauth_dokument",
        "_as_get_prev_dokument_registrering",
        "_as_list_dokument_varianter",
        "_as_sorted_dokument",
        "as_create_or_import_dokument",
        "as_list_dokument",
        "as_read_dokument",
        "as_search_dokument",
        "as_update_dokument",
        # Indsats
        "_as_convert_indsats_relation_kode_to_txt",
        "_as_create_indsats_registrering",
        "_as_filter_unauth_indsats",
        "_as_get_prev_indsats_registrering",
        "_as_sorted_indsats",
        "as_create_or_import_indsats",
        "as_list_indsats",
        "as_read_indsats",
        "as_search_indsats",
        "as_update_indsats",
        # Interessefaellesskab
        "_as_convert_interessefaellesskab_relation_kode_to_txt",
        "_as_create_interessefaellesskab_registrering",
        "_as_filter_unauth_interessefaellesskab",
        "_as_get_prev_interessefaellesskab_registrering",
        "_as_sorted_interessefaellesskab",
        "as_create_or_import_interessefaellesskab",
        "as_list_interessefaellesskab",
        "as_read_interessefaellesskab",
        "as_search_interessefaellesskab",
        "as_update_interessefaellesskab",
        # Loghaendelse
        "_as_convert_loghaendelse_relation_kode_to_txt",
        "_as_create_loghaendelse_registrering",
        "_as_filter_unauth_loghaendelse",
        "_as_get_prev_loghaendelse_registrering",
        "_as_sorted_loghaendelse",
        "as_create_or_import_loghaendelse",
        "as_list_loghaendelse",
        "as_read_loghaendelse",
        "as_search_loghaendelse",
        "as_update_loghaendelse",
        # Sag
        "_as_convert_sag_relation_kode_to_txt",
        "_as_create_sag_registrering",
        "_as_filter_unauth_sag",
        "_as_get_prev_sag_registrering",
        "_as_sorted_sag",
        "as_create_or_import_sag",
        "as_list_sag",
        "as_read_sag",
        "as_search_sag",
        "as_update_sag",
        # Tilstand
        "_as_convert_tilstand_relation_kode_to_txt",
        "_as_create_tilstand_registrering",
        "_as_filter_unauth_tilstand",
        "_as_get_prev_tilstand_registrering",
        "_as_sorted_tilstand",
        "as_create_or_import_tilstand",
        "as_list_tilstand",
        "as_read_tilstand",
        "as_search_tilstand",
        "as_update_tilstand",
    ]

    tables = [
        # Aktivitet
        "aktivitet_attr_egenskaber",
        "aktivitet_tils_status",
        "aktivitet_tils_publiceret",
        "aktivitet_relation",
        "aktivitet_registrering",
        "aktivitet",
        # Dokument
        "dokument_attr_egenskaber",
        "dokument_del_egenskaber",
        "dokument_del_relation",
        "dokument_del",
        "dokument_relation",
        "dokument_tils_fremdrift",
        "dokument_variant_egenskaber",
        "dokument_variant",
        "dokument_registrering",
        "dokument",
        # Indsats
        "indsats_attr_egenskaber",
        "indsats_relation",
        "indsats_tils_fremdrift",
        "indsats_tils_publiceret",
        "indsats_registrering",
        "indsats",
        # Interessefaellesskab
        "interessefaellesskab_attr_egenskaber",
        "interessefaellesskab_relation",
        "interessefaellesskab_tils_gyldighed",
        "interessefaellesskab_registrering",
        "interessefaellesskab",
        # Loghaendelse
        "loghaendelse_attr_egenskaber",
        "loghaendelse_relation",
        "loghaendelse_tils_gyldighed",
        "loghaendelse_registrering",
        "loghaendelse",
        # Sag
        "sag_attr_egenskaber",
        "sag_relation",
        "sag_tils_fremdrift",
        "sag_registrering",
        "sag",
        # Tilstand
        "tilstand_attr_egenskaber",
        "tilstand_relation",
        "tilstand_tils_publiceret",
        "tilstand_tils_status",
        "tilstand_registrering",
        "tilstand",
    ]

    sequences = [
        # Aktivitet
        "aktivitet_attr_egenskaber_id_seq",
        "aktivitet_registrering_id_seq",
        "aktivitet_relation_id_seq",
        "aktivitet_tils_publiceret_id_seq",
        "aktivitet_tils_status_id_seq",
        # Dokument
        "dokument_attr_egenskaber_id_seq",
        "dokument_del_egenskaber_id_seq",
        "dokument_del_id_seq",
        "dokument_del_relation_id_seq",
        "dokument_registrering_id_seq",
        "dokument_relation_id_seq",
        "dokument_tils_fremdrift_id_seq",
        "dokument_variant_egenskaber_id_seq",
        "dokument_variant_id_seq",
        # Indsats
        "indsats_attr_egenskaber_id_seq",
        "indsats_registrering_id_seq",
        "indsats_relation_id_seq",
        "indsats_tils_fremdrift_id_seq",
        "indsats_tils_publiceret_id_seq",
        # Interessefaellesskab
        "interessefaellesskab_attr_egenskaber_id_seq",
        "interessefaellesskab_registrering_id_seq",
        "interessefaellesskab_relation_id_seq",
        "interessefaellesskab_tils_gyldighed_id_seq",
        # Loghaendelse
        "loghaendelse_attr_egenskaber_id_seq",
        "loghaendelse_registrering_id_seq",
        "loghaendelse_relation_id_seq",
        "loghaendelse_tils_gyldighed_id_seq",
        # Sag
        "sag_attr_egenskaber_id_seq",
        "sag_registrering_id_seq",
        "sag_relation_id_seq",
        "sag_tils_fremdrift_id_seq",
        # Tilstand
        "tilstand_attr_egenskaber_id_seq",
        "tilstand_registrering_id_seq",
        "tilstand_relation_id_seq",
        "tilstand_tils_publiceret_id_seq",
        "tilstand_tils_status_id_seq",
    ]

    for table, constraints in table_constraints.items():
        for constraint in constraints:
            op.drop_constraint(constraint, table)

    for function in functions:
        op.drop_function(function)

    for table in tables:
        op.drop_table(table)

    for sequence in sequences:
        op.drop_sequence(sequence)
