# mo-facet-picker 

A facet picker component. 

## props 

- `value` ***Object*** (*optional*) 

- `facet` ***String*** (*required*) 

- `required` ***Boolean*** (*optional*) 

- `preselected-user-key` ***String*** (*optional*) 

## data 

- `selected` 

**initial value:** `null` 

## computed properties 

- `facetData` 

   **dependencies:** `$store`, `facet` 

- `isDisabled` 

   **dependencies:** `preselectedUserKey` 


## methods 

- `setPreselected()` 

