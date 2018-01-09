# address-search 
The address search component 


- **author** - Anders Jepsen 
- **input** -  


## props 
- `local-uuid` ***String*** (*optional*) `default: ''` 
The organisation uuid used to search locally 


## data 
- `location` The initial component values. 
 *initial value:* `[object Object]` 

- `addressSuggestions` 
 *initial value:* `[object Object]` 

- `template` 
 *initial value:* `'AddressSearchTemplate'` 

- `searchCountry` 
 *initial value:* `false` 


## events 
- `updateAddress` Fired when the address is changed 

## methods 
- `getLabel(item)` 
Return the street name of an item and set the location 

- `getGeographicalLocation(query)` 
Update address suggestions based on search query 


