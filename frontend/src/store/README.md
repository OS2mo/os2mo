# Store

The Vuex store is where we store the current state os the application.
Only globally needed stores, such as `organisation` are here.
Any other stores are loaded by the modules or views that require them.

The idea is that we have an `actions/` and `modules/` folder. In the
`modules/` folder we have the module definition, i.e. it's state, action,
mutation and getters. In the `actions/` folder we store the constants
for the store modules namespace, actions, mutations and getters.

The purpose of this is to leave room for at little typing and text
strings as possible for the stores. Instead, every time you need to
access are store from a component, you import the actions you need.

Read more about vuex [here](https://vuex.vuejs.org/)
Read more about large scale vuex stores [here](https://medium.com/3yourmind/large-scale-vuex-application-structures-651e44863e2f)
Read more about complex vues stores [here](https://markus.oberlehner.net/blog/how-to-structure-a-complex-vuex-store/)
