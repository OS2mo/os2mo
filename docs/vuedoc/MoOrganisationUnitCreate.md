# organisation-unit-create 

A organisation unit create component 

## data 

- `entry` 

  The entry, postAddress, phone, addresses, isLoading, backendValidationError component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `addresses` 

**initial value:** `[object Object]` 

- `postAddress` 

**initial value:** `[object Object]` 

- `phone` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

- `backendValidationError` 

**initial value:** `null` 

- `addressEntry` 

  The addressEntry component.
  Used to add MoAddressEntry component in `<mo-add-many/>`. 

**initial value:** `'MoOrgUnitAddressEntry'` 

## methods 

- `resetData()` 

  Resets the data fields. 

- `createOrganisationUnit(evt)` 

  Create a organisation unit and check if the data fields are valid.
  Then throw a error if not. 

