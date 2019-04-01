# mo-time-machine-column 

A timemachine column component. 

## props 

- `store-id` ***String*** (*required*) 

## data 

- `date` 

  The date, org, orgUnit component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

## computed properties 

- `unitUuid` 

   **dependencies:** `orgUnit`, `orgUnit` 

- `orgUnit` 

   **dependencies:** `$store`, `storeId` 


## methods 

- `loadContent(event)` 

