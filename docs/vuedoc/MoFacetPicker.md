# mo-facet-picker 

A facet picker component. 

## props 

- `value` ***Object*** (*optional*) 

- `facet` ***String*** (*required*) 

- `required` ***Boolean*** (*optional*) 

- `preselected-user-key` ***String*** (*optional*) `default: null` 

## data 

- `internalValue` 

**initial value:** `null` 

## computed properties 

- `facetData` 

   **dependencies:** `$store`, `facet` 

- `sortedOptions` 

   **dependencies:** `facetData` 

- `isDisabled` 

   **dependencies:** `preselectedUserKey` 

- `labelText` 

   **dependencies:** `facetData`, `$t`, `facetData` 

- `preselected` 

   **dependencies:** `facetData`, `facetData`, `preselectedUserKey` 


## methods 

- `setInternalValue()` 

