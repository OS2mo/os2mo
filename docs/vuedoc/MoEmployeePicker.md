# mo-employee-picker 

A employee picker component. 

## props 

- `value` ***Object*** (*optional*) 

- `no-label` ***Boolean*** (*optional*) 

- `required` ***Boolean*** (*optional*) 

- `validity` ***Object*** (*optional*) 

  Validities, used for validation 

- `extra-validations` ***Object*** (*optional*) 

  An object of additional validations to be performed 

## data 

- `item` 

**initial value:** `null` 

- `items` 

**initial value:** `[object Object]` 

- `template` 

**initial value:** `'MoSearchBarTemplate'` 

## computed properties 

- `orderedListOptions` 

   **dependencies:** `items` 

- `validations` 

   **dependencies:** `required`, `validity`, `extraValidations`, `extraValidations` 


## methods 

- `getLabel(item)` 

  Get employee name. 

- `updateItems(query)` 

  Update employees suggestions based on search query. 

