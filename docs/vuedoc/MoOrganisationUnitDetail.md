# mo-organisation-unit-detail 

A organisation unit detail component. 

## props 

- `uuid` ***String*** (*required*) 

  Defines a unique identifier which must be unique. 

- `at-date` ***ArrayExpression*** (*optional*) 

  Defines a at date. 

- `detail` ***String*** (*required*) 

  Defines the detail content type. 

- `columns` ***Array*** (*optional*) 

  Defines columns. 

- `entry-component` ***Object*** (*optional*) 

  Defines a entryComponent for create. 

- `hide-create` ***Boolean*** (*optional*) 

  This Boolean property hides the create button. 

## data 

- `details` 

  The details, loading component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `loading` 

**initial value:** `[object Object]` 

## methods 

- `getAllDetails()` 

  Let past, present, future be array for getDetails. 

- `getDetails(tense)` 

  Get all organisation details. 

