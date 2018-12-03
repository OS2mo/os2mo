# mo-tree-view 

## props 

- `unit-uuid` ***String*** (*optional*) 

  Defines a orgUuid. 

- `at-date` ***ArrayExpression*** (*optional*) 

  Defines a atDate. 

## data 

- `treeData` 

**initial value:** `[object Object]` 

- `selected` 

**initial value:** `undefined` 

- `units` 

**initial value:** `[object Object]` 

- `treeOptions` 

**initial value:** `[object Object]` 

## computed properties 

- `nameId` 

   **dependencies:** `_uid` 

- `tree` 

   **dependencies:** `$refs`, `nameId` 

- `contents` 

   **dependencies:** `tree` 


## events 

- `input` 

## methods 

- `setSelection(unitid)` 

  Select the unit corresponding to the given ID, assuming it's present. 

- `addNode(unit, parent)` 

- `toNode(unit)` 

  Convert a unit object into a node suitable for adding to the
  tree.
  
  This method handles both eager and lazy loading of child nodes. 

- `updateTree(force)` 

  Reset and re-fetch the tree. 

- `fetch(node)` 

