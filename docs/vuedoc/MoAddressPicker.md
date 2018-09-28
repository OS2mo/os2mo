# address-picker 

A address picker component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `org-unit` ***Object*** (*optional*) 

  Defines a orgUnit. 

## data 

- `label` 

  The label component value.
  Used to set a default value. 

**initial value:** `'Adresser'` 

- `selected` 

  The selected, addresses, isLoading component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `addresses` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

## computed properties 

- `nameId` 

  Get name `mo-address-picker`. 

   **dependencies:** `_uid` 

- `isDisabled` 

  Disable orgUnit. 

   **dependencies:** `orgUnit` 

- `noAddresses` 

  Return blank address. 

   **dependencies:** `addresses` 

- `orderedListOptions` 

   **dependencies:** `addresses` 


## events 

- `input` 

## methods 

- `getAddresses()` 

  Get organisation unit address details. 

- `updateSelectedAddress()` 

  Update selected address. 

