# mo-address-search-field 

A address search field component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `label` ***String*** (*optional*) 

  Defines a label. 

- `global` ***Boolean*** (*optional*) 

  This boolean property change it to global search. 

## data 

- `addressSuggestions` 

  The addressSuggestions, selectedItem component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `selectedItem` 

**initial value:** `null` 

- `template` 

  The template component.
  Used to add MoAddressSearchTemplate component. 

**initial value:** `'MoAddressSearchTemplate'` 

## computed properties 

- `nameId` 

  Get name `address-search-field`. 

   **dependencies:** `_uid` 


## methods 

- `getLabel(item)` 

  Get location name. 

- `getGeographicalLocation(query)` 

  Update address suggestions based on search query. 

