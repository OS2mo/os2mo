# mo-engagement-picker 

A engagement picker component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `employee` ***Object*** (*required*) 

  Defines a required employee. 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a selected name. 

## data 

- `selected` 

  The selected, engagements, isLoading component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `engagements` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

## computed properties 

- `nameId` 

  Get name `engagement-picker` 

   **dependencies:** `_uid` 

- `isRequired` 

  Set employee as required. 

   **dependencies:** `employeeDefined`, `required` 

- `employeeDefined` 

  If employee is not defined, return false and disable. 

   **dependencies:** `employee`, `employee` 

- `orderedListOptions` 

   **dependencies:** `engagements` 


## events 

- `input` 

## methods 

- `getEngagements()` 

  Get engagement details. 

- `updateSelectedEngagement()` 

  Update selected engagement. 

