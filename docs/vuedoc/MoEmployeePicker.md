# mo-employee-picker 

A employee picker component. 

## props 

- `no-label` ***Boolean*** (*optional*) 

  This boolean property defines a noLabel value. 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a selected name. 

## data 

- `item` 

  The item, items component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `items` 

**initial value:** `[object Object]` 

- `template` 

  The template component value.
  Used to add MoSearchBarTemplate to the autocomplete search. 

**initial value:** `'MoSearchBarTemplate'` 

## events 

- `input` 

## methods 

- `getLabel(item)` 

  Get employee name. 

- `updateItems(query)` 

  Update employees suggestions based on search query. 

- `selected(value)` 

  Update selected value. 

