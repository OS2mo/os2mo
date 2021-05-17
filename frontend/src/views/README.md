# Views

This folder contains the core views of OS2MO. These are:

* employee
* frontpage
* organisation
* page not found

`employee` is as of this writing (29/01/2019) the most developed view folder.
It contains the following:

```javascript
employee/
  MoEmployeeWorkflows/
    _store/
      employeeCreate.js
      ...
    MoEmployeeCreate.vue
    ...
  EmployeeDetail.vue
  EmployeeDetailTabs.vue
  index.vue
  install.js
  MenuItem.vue
  MoEmployeeList.vue
  router.js
```

The idea is that the folder contains **everything** related to the employee page.
The detail view, router, workflows and workflow stores. Ideally the employee store
would also be in here, as it is only used for this view. This if future work.

`router.js` contains all the routing nessecary for the view. It is imported into
the global `router.js` file at the root.

`install.js` installs the module in the global `main.js` file at the root. It adds
the employee button to the frontpage so it becomes available.

`MenuItem.vue` is the button on the frontpage that is added in `index.js`.

A view can use anything located in `api/` `components/` `filters` etc. However,
modules are off limits. Instead, a module should inject itself into a view if
nessecary. This likely requires a new api to be possible.
