# mo-facet-picker 

A facet picker component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `facet` ***String*** (*required*) 

  Defines a required facet. 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a selected value. 

- `preselected-user-key` ***String*** (*optional*) 

  Defines a preselectedUserKey. 

## data 

- `selected` 

  The selected, facets, label component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `facets` 

**initial value:** `[object Object]` 

- `label` 

**initial value:** `''` 

## computed properties 

- `isDisabled` 

  Disabled value if its undefined. 

   **dependencies:** `preselectedUserKey` 


## methods 

- `getFacet()` 

  Get a facet. 

- `setPreselected()` 

  Set a preselected value. 

