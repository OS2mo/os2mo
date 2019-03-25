# mo-address-entry 

A address entry component. 

## props 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a selected address type. 

- `label` ***String*** (*optional*) 

  Defines a label. 

- `preselected-type` ***String*** (*optional*) 

  Defines a preselectedType. 

- `facet` ***String*** (*required*) 

  Defines a preselectedType. 

## data 

- `contactInfo` 

  The contactInfo, entry, address, addressScope component value.
  Used to detect changes and restore the value. 

**initial value:** `''` 

- `entry` 

**initial value:** `[object Object]` 

- `address` 

**initial value:** `null` 

- `addressScope` 

**initial value:** `null` 

## computed properties 

- `isDarAddress` 

  If the address is a DAR. 

   **dependencies:** `entry`, `entry` 

- `isPhone` 

  If the address is a PHONE. 

   **dependencies:** `entry`, `entry` 

- `noPreselectedType` 

  If it has not a preselectedType. 

   **dependencies:** `preselectedType` 

- `validityRules` 

  Every scopes validity rules. 

   **dependencies:** `entry` 


