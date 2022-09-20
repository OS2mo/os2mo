#Modules

The modules folder is where we put any extra modules that should be added to OS2MO.

## Structure of the `modules` folder

The modules folder has the following structure

```
modules/
  someModule1/
  someModule2/
  install.js
  router.js
```

`install.js` is loaded into the applications `main.js` file.
`router.js` is loaded into the applications `router.js` file.

## Structure of a module

A module should have the following structure:

```
yourModule/
  _api/
  _components/
  _store/
  _views/
  index.vue (or index.js)
  install.js
  router.js
```

`_api/` folder contains any api specific to this module
`_components/` folder contains any components specific to this module
`_store/` folder contains the store specific for this module
`_views/` folder contains the views for this module
`index.vue` or `index.js` is the main page of your module
`install.js` should contain any commands that injects into the main system
`router.js` should contain the routing specific to this module

## Install a module

To install a module, do the following:

import your modules install file in to the main module install file

```javascript
import './yourModule/install'
```

Next add your modules router to the main module router

```javascript
import yourModuleRouter from './yourModule/router.js'

export default [
  ...,
  yourModuleRouter
]
```

Now your module is available in the application.
