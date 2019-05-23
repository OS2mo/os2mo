# mo-tree-view 

## props 

- `v-model` ***String|Array*** (*optional*) 

  This control takes a string variable as its model, representing
  the UUID of the selected unit. Internally, the tree view does
  have access to reasonably full objects representing the unit,
  but they don't correspond _exactly_ to those used elsewhere, so
  we only pass the UUID. 

- `at-date` ***Date|String*** (*optional*) 

  Defines the date for rendering the tree; used for the time machine. 

- `disabled-unit` ***String*** (*optional*) 

  UUID of unselectable unit. 

- `multiple` ***Boolean*** (*optional*) 

  Select more than one node 

## computed properties 

- `contents` 

  A string representation of the currently rendered tree, useful
  for inspection and tests, with highlighting of expansion and
  selection states. 

   **dependencies:** `tree` 


## events 

- `input` 

## methods 

- `onNodeCheckedChanged(node)` 

- `getSelection()` 

- `toArray(values)` 

- `setSelection(unitids)` 

  Select the units corresponding to the given IDs, assuming
  they're present, and updating the tree otherwise. 

- `addNodes(units)` 

  Add the given nodes to the tree. 

- `addNode(unit, parent)` 

  Add the given node to the tree, nested under the parent, specified, or
  root otherwise. 

- `toNode(unit)` 

  Convert a unit object into a node suitable for adding to the
  tree.
  
  This method handles both eager and lazy loading of child nodes. 

- `updateTree(force)` 

  Reset and re-fetch the tree. 

- `fetch(node)` 

  LiquorTree lazy data fetcher. 

