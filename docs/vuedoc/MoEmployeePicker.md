# mo-employee-picker 

A employee picker component. 

## props 

- `value` ***Object*** (*optional*) 

- `no-label` ***Boolean*** (*optional*) 

- `required` ***Boolean*** (*optional*) 

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


## methods 

- `getLabel(item)` 

  Get employee name. 

- `updateItems(query)` 

  Update employees suggestions based on search query. 

