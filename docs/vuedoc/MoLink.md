# mo-link 

A link component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `field` ***String*** (*optional*) `default: 'name'` 

  Defines a default field name. 

- `index` ***Number*** (*optional*) `default: [object Object]` 

  If set, restrict this entry to the given index in an array. 

- `column` ***String*** (*optional*) `default: null` 

  Defines a default column. 

## data 

- `column_handlers` 

  The column_handlers component value.
  Used to add OrganisationDetail, EmployeeDetail components. 

**initial value:** `[object Object]` 

## computed properties 

- `classes` 

  Returns columns and fields. 

   **dependencies:** `column`, `field`, `column`, `field`, `column`, `column`, `field`, `field` 

- `parts` 

  Defines contents, columns and value. 

   **dependencies:** `column`, `value`, `column`, `value`, `column`, `value`, `value`, `column`, `column`, `value`, `column`, `value`, `value`, `column`, `column`, `value`, `column`, `index`, `index`, `column_handlers`, `column`, `field`, `field` 


