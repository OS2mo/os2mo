# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from mo_ldap_import_export.environments.main import filter_extract_mitid_uuid


def test_extract_mitid_uuid_success():
    input_val = [
        "SomeOtherValue",
        "NL3UUID-ACTIVE-NSIS:29189846.6b6831fc-00cf-49f3-91b7-23217d77072b.f99c7445-e95e-4824-b299-d968033021fb.79783962.H4lX2Lhsi2LlZnuyyxtdhwyyfLMx0QE8CaRuo1dWL7NTgihs/WkOWwDUs7dYSI+qodP+J0bUt4eM4uxdH8fP4bnCZXcE3ZpunUfEYGl+altg0TqEs2CHukuzxmmVS/kcwD/WZ3I3wXtdY5hexy/ZgxDAYV4Q3zKx959e9m3M6Py4gcJpikX1cmNZrKWYLk7CjSY6LdWv11qxIGa5EDkRBTzR85UxsR4lZJDsta7hRe0aSGj2W1l89dNIrYzTwyUpCFf0Vb1zP2FirwTmuoHNVaPMLXoKvHGIgzFrPyLeeOUuqZMHGVI4VZzl+PquHtXeR/EGFGE0aPfsw99lzHXNFWHDoNGLJCLCwSd0ZeHFb26D9UyTqTLy5sFitJ18arYoLQ6th0XDlQuAJU908mzPgxaCV7QyXBFaC2owOFIR/h93CtiWdXKVru7GoydDBqT8inTHvD+7ZlyeXqwEXZQZwIRkeu8hpIpNqHlksUpsw1j+diokfYz2RAqpc+c7r6m9HGjqqmYEU6cyeywmsxx7xjfbQl1DCJQhtju6CrohALUWoJiMTs8O5Jshrn3qJLDUt76Cf9jnzn/w7pEZM8uImYtGYayzwmHkaEAzD8+rwj31SEL65Dc59sCoChSJ+kTT9LSCOo+gucdUSW9hcJKnlGCe3k6hgAOX/T/iD3GgKcI=",
        "AnotherValue",
    ]
    assert (
        filter_extract_mitid_uuid(input_val) == "f99c7445-e95e-4824-b299-d968033021fb"
    )


def test_extract_mitid_uuid_none():
    assert filter_extract_mitid_uuid(None) is None


def test_extract_mitid_uuid_empty_list():
    assert filter_extract_mitid_uuid([]) is None


def test_extract_mitid_uuid_no_match():
    input_val = ["SomeOtherValue", "AnotherValue"]
    assert filter_extract_mitid_uuid(input_val) is None


def test_extract_mitid_uuid_single_string():
    input_val = "NL3UUID-ACTIVE-NSIS:1.2.uuid-value.rest"
    assert filter_extract_mitid_uuid(input_val) == "uuid-value"


def test_extract_mitid_uuid_malformed():
    input_val = ["NL3UUID-ACTIVE-NSIS:1.2"]  # Not enough parts
    assert filter_extract_mitid_uuid(input_val) is None

    input_val = ["NL3UUID-ACTIVE-NSIS:1"]  # Not enough parts
    assert filter_extract_mitid_uuid(input_val) is None


def test_extract_mitid_uuid_not_string():
    input_val = [123, None, "NL3UUID-ACTIVE-NSIS:1.2.uuid.rest"]
    assert filter_extract_mitid_uuid(input_val) == "uuid"
