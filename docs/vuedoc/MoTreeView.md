# mo-tree-view 

A tree view component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `org-uuid` ***String*** (*optional*) 

  Defines a orgUuid. 

- `linkable` ***Boolean*** (*optional*) 

  This boolean property defines a able link. 

- `at-date` ***ArrayExpression*** (*optional*) 

  Defines a atDate. 

## data 

- `children` 

  The children, selectedOrgUnit, isLoading component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `selectedOrgUnit` 

**initial value:** `[object Object]` 

- `isLoading` 

**initial value:** `false` 

## methods 

- `getChildren()` 

  Get organisation children. 

