# employee-detail-tabs 

A employee detail tabs component. 

## props 

- `uuid` ***String*** (*optional*) 

  Defines a unique identifier which must be unique. 

- `hide-actions` ***Boolean*** (*optional*) 

  This Boolean property hides the actions. 

## data 

- `isLoading` 

  The isLoading, leave, it, address, engagement, association, role, manager component value.
  Used to detect changes and restore the value for columns. 

**initial value:** `false` 

- `engagement` 

**initial value:** `[object Object]` 

- `role` 

**initial value:** `[object Object]` 

- `it` 

**initial value:** `[object Object]` 

- `association` 

**initial value:** `[object Object]` 

- `leave` 

**initial value:** `[object Object]` 

- `manager` 

**initial value:** `[object Object]` 

- `address` 

**initial value:** `[object Object]` 

- `components` 

  The MoEngagementEntry, MoAddressEntry, MoRoleEntry, MoItSystemEntry,
  MoAssociationEntry, MoLeaveEntry, MoManagerEntry component.
  Used to add the components in the tabs. 

**initial value:** `[object Object]` 

