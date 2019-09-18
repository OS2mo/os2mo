# mo-facet-picker 

A facet picker component. 

## props 

- `value` ***Object*** (*optional*) 

- `facet` ***String*** (*required*) 

- `required` ***Boolean*** (*optional*) 

## data 

- `internalValue` 

**initial value:** `null` 

## computed properties 

- `facetData` 

   **dependencies:** `$store`, `facet` 

- `sortedOptions` 

   **dependencies:** `facetData` 

- `labelText` 

   **dependencies:** `facetData`, `$t`, `facetData` 

- `preselected` 

   **dependencies:** `facetData` 


## methods 

- `setInternalValue()` 

