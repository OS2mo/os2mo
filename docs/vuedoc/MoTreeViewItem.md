# mo-tree-view-item 

A tree view item component 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `model` ***Object*** (*optional*) 

  Defines a model name. 

- `first-open` ***Boolean*** (*optional*) 

  This boolean property defines a open link. 

- `linkable` ***Boolean*** (*optional*) 

  This boolean defines a able link. 

- `at-date` ***ArrayExpression*** (*optional*) 

  Defines a atDate. 

## data 

- `selected` 

  The selected, open, loading component value.
  Used to detect changes and restore the value. 

**initial value:** `[object Object]` 

- `open` 

**initial value:** `false` 

- `loading` 

**initial value:** `true` 

## computed properties 

- `hasChildren` 

  Show children if it has. 

   **dependencies:** `model` 


## events 

- `input` 

## methods 

- `toggle()` 

  On toggle open children. 

- `selectOrgUnit(org)` 

  When selectOrgUnit change, update org. 

- `loadChildren()` 

  Get organisation unit children. 

