# mo-entry-terminate-modal 

Terminate an entry, e.g. an association or engagement. 

## props 

- `type` ***String*** (*required*) 

- `content` ***Object*** (*required*) 

## data 

- `validity` 

**initial value:** `[object Object]` 

- `backendValidationError` 

**initial value:** `null` 

- `isLoading` 

**initial value:** `false` 

## computed properties 

- `title` 

   **dependencies:** `$t`, `$tc`, `type` 

- `nameId` 

   **dependencies:** `_uid` 

- `payload` 

   **dependencies:** `type`, `content`, `validity` 

- `validDates` 

  Check if the organisation date are valid. 

   **dependencies:** `content` 


## events 

- `submit` 

## methods 

- `onHidden()` 

- `terminate(evt)` 

  Terminate a organisation unit and check if the data fields are valid.
  Then throw a error if not. 

