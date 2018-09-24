# mo-history 

A history component. 

## props 

- `uuid` ***String*** (*required*) 

  Defines a required uuid. 

- `type` ***String*** (*required*) 

  Defines a required type - employee or organisation unit. 

## data 

- `history` 

  The history component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

## methods 

- `reloadHistory(val)` 

  Reload history. 

- `getHistory()` 

  Switch between organisation and employee getHistory. 

- `getOrgUnitHistory(uuid)` 

  Get organisation unit history. 

- `getEmployeeHistory(uuid)` 

  Get employee history. 

