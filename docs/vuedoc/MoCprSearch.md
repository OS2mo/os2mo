# mo-cpr-search 

cpr search component. 

## props 

- `no-label` ***Boolean*** (*optional*) 

  This boolean property defines a label if it does not have one. 

- `label` ***String*** (*optional*) `default: 'CPR nummer'` 

  Defines a default label name. 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a valid cpr number. 

## data 

- `nameId` 

  The nameId, cprNo, backendValidationError component value.
  Used to detect changes and restore the value. 

**initial value:** `'cpr-search'` 

- `cprNo` 

**initial value:** `''` 

- `isLoading` 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

