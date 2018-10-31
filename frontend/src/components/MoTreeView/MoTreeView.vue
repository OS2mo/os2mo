<template>
  <div>    

    {{children}}
    <liquor-tree :data="treeData" :options="treeOptions" ref="tree"/>

  </div>
</template>

<script>
  import Organisation from '@/api/Organisation'
  import OrganisationUnit from '@/api/OrganisationUnit'
  import LiquorTree from 'liquor-tree'
  import treeStore from './_store'
  // import Store from '@/vuex/store'

  export default {
    components: {
      LiquorTree
    },

    props: {
      value: Object,
      orgUuid: String
    },

    data () {
      return {
        treeData: [

        ],
        children: [],
        treeOptions: {
          propertyNames: {
            text: 'name',
            isBatch: 'child_count',
            id: 'uuid'
          },
          fetchData (node) {
            return OrganisationUnit.getChildren(node.id, this.atDate)
              .then(response => {
                // node.append(response)
                console.log(node.children)
                return response
              })
          }
          // store: {
          //   store: Store,
          //   getter: () => {
          //     return this.$store.getters['liquorTree/getTreeData']
          //   },
          //   dispatcher (tree) {
          //     this.$store.dispatch('liquorTree/updateTree', tree)
          //   }
          // }
        }
      }
    },

    created () {
      this.$store.registerModule('liquorTree', treeStore)
    },

    mounted () {
      this.$refs.tree.$on('node:expanded', () => {
        console.log('hello')
      })
    },

    methods: {

      /**
       * Get organisation children.
       */
      getRootChildren () {
        if (this.orgUuid === undefined) return
        let vm = this
        vm.isLoading = true
        return Organisation.getChildren(this.orgUuid, this.atDate)
          .then(response => {
            vm.isLoading = false
            vm.children = response
            return response
          })
      },

      getOrgUnitChildren (event) {
        // let vm = this
        // vm.loading = true
        // vm.model.children = []
        OrganisationUnit.getChildren(event.uuid, this.atDate)
          .then(response => {
            console.log(response)
            // vm.loading = false
            // vm.model.children = response
          })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}
</style>
