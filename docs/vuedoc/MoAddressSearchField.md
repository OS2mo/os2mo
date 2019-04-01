# mo-address-search-field 

Address search field component. 

## props 

- `global` ***Boolean*** (*optional*) `default: false` 

  Enable global search 

## data 

- `addressSuggestions` 

  Results from query 

**initial value:** `[object Object]` 

- `template` 

  Results template 

**initial value:** `'MoAddressSearchTemplate'` 

## methods 

- `getLabel(item)` 

  Get a label to display 

   **return value:** 

     - **Any** - {String} 
- `getGeographicalLocation(query)` 

  Update address suggestions based on search query. 

