# mo-search-bar 

A searchbar component. 

## data 

- `item` 

  The item, items, routeName component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `items` 

**initial value:** `[object Object]` 

- `routeName` 

**initial value:** `''` 

- `template` 

  The template component value.
  Used to add MoSearchBarTemplate to the v-autocomplete. 

**initial value:** `'MoSearchBarTemplate'` 

- `noItem` 

  The noItem component value.
  Used to give a default name. 

**initial value:** `[object Object]` 

## computed properties 

- `orderedListOptions` 

   **dependencies:** `items` 


## methods 

- `getLabel(item)` 

  Get label name. 

- `getRouteName(route)` 

  Get to the route name.
  So if we're viewing an employee, it goes to the employee detail. 

- `updateItems(query)` 

  Update employee or organisation suggestions based on search query. 

- `selected(item)` 

  Go to the selected route. 

