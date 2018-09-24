# mo-employee-detail 

A employeedetail component. 

## props 

- `uuid` ***String*** (*required*) 

  Defines a unique identifier which must be unique. 

- `detail` ***String*** (*required*) 

  Defines the detail content type. 

- `columns` ***Array*** (*optional*) 

  Defines columns. 

- `entry-component` ***Object*** (*optional*) 

  Defines a entry component for create. 

## data 

- `details` 

  The details, loading component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `loading` 

**initial value:** `[object Object]` 

## methods 

- `getAllDetails()` 

  Let past, present, future be array for getDetails. 

- `getDetails(tense)` 

  Get all employee details. 

