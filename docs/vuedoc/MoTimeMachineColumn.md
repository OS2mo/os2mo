# mo-time-machine-column 

A timemachine column component. 

## props 

- `store-id` ***String*** (*required*) 

## data 

- `date` 

  The date, org, orgUnit component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `org` 

**initial value:** `[object Object]` 

- `orgUnit` 

**initial value:** `null` 

## computed properties 

- `orgUnitInfo` 

   **dependencies:** `$store`, `storeId` 


## methods 

- `loadContent(event)` 

