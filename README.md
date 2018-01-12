# os2mo

> A Vue.js project

## Build Setup

``` bash
# install dependencies
yarn

# serve with hot reload at localhost:8080
yarn start

# build for production with minification
yarn build

# build for production and view the bundle analyzer report
yarn build --report

# run unit tests
yarn unit

# run e2e tests
yarn e2e

# run all tests
yarn test
```

## Documentation

``` bash
# Install vuedoc globally to use in commandline
npm install --global @vuedoc/md

# generate documentation into docs/ folder
yarn docs
```

## File structure

``` bash
- build/
- config/
- src/
  - api/
  - assets/
    - css/
    - logo/
  - components/
  - directives/ 
  - employee/
  - help/
  - login/
  - organisation/
  - router/
  - timemachine/
  App.vue
  EventBus.vue
  main.js
- static/
- test/
  e2e/
  unit/
```
Most of the structure should be fairly self explanatory. `components/` contain all the components, `organisation/` contain all views related to organisations, `employee/` contain all views related to employees, etc.

`EventBus.vue` control global events.

For a detailed explanation on how things work, check out the [guide](http://vuejs-templates.github.io/webpack/) and [docs for vue-loader](http://vuejs.github.io/vue-loader).
