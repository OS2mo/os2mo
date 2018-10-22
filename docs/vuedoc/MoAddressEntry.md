# mo-address-entry 

A address entry component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `validity-hidden` ***Boolean*** (*optional*) 

  This boolean property hides the validity dates. 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a selected address type. 

- `label` ***String*** (*optional*) 

  Defines a label. 

- `preselected-type` ***String*** (*optional*) 

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

- `isDisabled` 

  Disable address type. 

   **dependencies:** `entry` 

- `noPreselectedType` 

  If it has not a preselectedType. 

   **dependencies:** `preselectedType` 

- `nameId` 

  Get name `scope-type`. 

   **dependencies:** `_uid` 

- `validityRules` 

  Every scopes validity rules. 

   **dependencies:** `entry`, `entry`, `entry`, `entry`, `entry`, `entry`, `entry` 


