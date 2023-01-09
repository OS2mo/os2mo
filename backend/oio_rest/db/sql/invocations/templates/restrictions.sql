    -- SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
    -- SPDX-License-Identifier: MPL-2.0
    -- restrictions
    ARRAY[
    {% for r in restrictions %}
    {{ r }}{% if not loop.last %},{% endif %}
    {% endfor %}
    ]
