Release type: minor

[#52316] Cleanup Employee Create

This commit changes how the RequestHandler dict is generated.
It is now generated via `to_handler_dict` similar to how
`create_org_unit` does it.

All the relevant tests have been rewritten to follow the style that
`create_org_unit` utilizes.

Finally the input model has been modified, with the following changes:

* Take a separate `givenname` (first name) and `surname` (last name)

Previously the code took just a 'name' and the backend had to split it
up. We prefer to get structured data directly from the source over
trying to derive it on demand.

* Ensures names are actually set

Previously the code would accept the empty string for the `name`
parameter, however the validation logic actually acquires a non-empty
string.

A change has been made to ensure that the strings are actually set.

* The CPR number field has been renamed from `cpr_no` to `cpr_number`

Bytes are cheap and we might as well use a fuller name.

* The CPR number field has been made optional

We deploy OS2mo in non-danish contexts, thus we cannot assume a CPR
number is always available. We could consider converting it to a more
generic 'national identification number' concept.

* User-key has been added

A lot of integrations utilize the user-key for a domain specific key,
for instance the employee identifier in the HR system.

Note: This is really a breaking change as `name` has been removed, and
      as `cpr_no` has been renamed, thus breaking the current interface.
      Usually we would handle such a change by creating a new GraphQL
      version, however as noone uses the current interface yet, we are
      okay with breaking it without creating a new version.
