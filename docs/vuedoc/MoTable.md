# mo-table 

A table component. 

## props 

- `content` ***Array*** (*optional*) 

  Defines a content. 

- `content-type` ***String*** (*optional*) 

  Defines a contentType. 

- `columns` ***Array*** (*optional*) 

  Defines columns. 

- `is-loading` ***Boolean*** (*optional*) 

  This boolean property defines the loading. 

- `edit-component` ***Object*** (*optional*) 

  Defines the editComponent. 

- `edit-uuid` ***String*** (*optional*) 

  Defines the editUuid. 

- `multi-select` ***Boolean*** (*optional*) 

  This boolean property defines the multiSelect 

- `type` ***String*** (*required*) 

  Defines a required type. 

## data 

- `selectAll` 

  The selectAll, selected, open, sortableContent component value.
  Used to detect changes and restore the value. 

**initial value:** `false` 

- `selected` 

**initial value:** `[object Object]` 

- `open` 

**initial value:** `[object Object]` 

- `sortableContent` 

**initial value:** `null` 

## computed properties 

- `contentAvailable` 

  If content is available, get content. 

   **dependencies:** `content`, `content` 


## methods 

- `sortData(colName, toggleIcon)` 

  Sort data in columns. 

- `sortDate(toggleIcon, date)` 

  Sort dates in columns. 

