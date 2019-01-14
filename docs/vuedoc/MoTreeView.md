# mo-tree-view 

## props 

- `v-model` ***String*** (*optional*) 

  This control takes a string variable as its model, representing
  the UUID of the selected unit. Internally, the tree view does
  have access to reasonably full objects representing the unit,
  but they don't correspond _exactly_ to those used elsewhere, so
  we only pass the UUID. 

- `at-date` ***Date|String*** (*optional*) 

  Defines the date for rendering the tree; used for the time machine. 

## computed properties 

- `contents` 

  A string representation of the currently rendered tree, useful
  for inspection and tests, with highlighting of expansion and
  selection states. 

   **dependencies:** `tree` 


## events 

- `input` 

  Emitted whenever the selection changes. 

## methods 

- `setSelection(unitid)` 

  Select the unit corresponding to the given ID, assuming it's present. 

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

