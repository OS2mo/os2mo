# mo-organisation-picker 

A organisation picker component. 

## props 

- `v-model` ***Object*** (*optional*) 

- `at-date` ***ArrayExpression*** (*optional*) 

  Defines a atDate. 

- `reset-route` ***Boolean*** (*optional*) 

  This boolean property resets the route. 

- `ignore-event` ***Boolean*** (*optional*) 

  This boolean property igonores a event. 

## data 

- `selectedOrganisation` 

  The selectedOrganisation, orgs component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `orgs` 

**initial value:** `[object Object]` 

## computed properties 

- `orderedListOptions` 

   **dependencies:** `orgs` 


## methods 

- `getAll()` 

  Get all organisations for this atDate. 

- `resetToBaseRoute()` 

  Resets the route back to base.
  So if we're viewing an employee, it goes back to the employee list. 

