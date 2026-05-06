-- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
-- SPDX-License-Identifier: MPL-2.0

SELECT  as_list_{{ class_name | lower }}(
    {{ uuid|adapt }}::uuid[],
    {{ registrering_tstzrange|adapt }},
    {{ virkning_tstzrange|adapt }}
) :: json[];
