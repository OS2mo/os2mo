<template>
  <div>    
    <liquor-tree :data="treeData" :options="treeOptions" ref="tree"/>
  </div>
</template>

<script>
  import Organisation from '@/api/Organisation'
  import OrganisationUnit from '@/api/OrganisationUnit'
  import LiquorTree from 'liquor-tree'
  import treeStore from './_store'
  import { mapGetters } from 'vuex'

  // import Store from '@/vuex/store'

  export default {
    components: {
      LiquorTree
    },

    computed: {
      ...mapGetters({
        currentUnit: 'organisationUnit/GET_ORG_UNIT'
      }),
      ...mapGetters({
        orgUuid: 'organisation/getUuid'
      })
    },

    data () {
      let vm = this

      return {
        treeData: [],
        treeOptions: {
          minFetchDelay: 1,
          propertyNames: {
            text: 'name',
            isBatch: 'child_count',
            id: 'uuid'
          },
          fetchData (node) {
            return vm.fetch(node)
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
      this.renderTree()

      this.$refs.tree.$on('node:expanded', node => {
        console.log('expanded', node.text)
      })

      this.$refs.tree.$on('node:selected', (node) => {
        console.log('selected', node.text)
      })

      this.$refs.tree.$on('tree:data:fetch', node => {
        console.log('fetching', node.text)
      })

      this.$refs.tree.$on('node:selected', node => {
        if (node.id !== this.currentUnit.uuid) {
          this.$router.push({
            name: 'OrganisationDetail',
            params: { uuid: node.id }
          })
        }
      })
    },

    watch: {
      orgUuid () {
        this.renderTree()
      },

      currentUnit: {
        handler (val) {
          let node = this.$refs.tree.find({id: val.uuid})

          if (node) {
            node.select()
          }
        },
        deep: true
      }
    },

    methods: {
      renderTree () {
        let vm = this
        let tree = this.$refs.tree

        if (!this.orgUuid) {
          return
        }

        Organisation.getChildren(this.orgUuid, this.atDate)
          .then(response => {
            vm.treeData.length = 0
            vm.treeData.push.apply(vm.treeData, response)
            tree.remove({})

            this.addNodes(tree, response)
          })
      },

      addNodes (parent, units) {
        units.forEach(this.addNode.bind(this, parent))
      },

      addNode (parent, unit) {
        parent.append({
          text: unit.name,
          isBatch: unit.child_count,
          id: unit.uuid
        })

        let node = this.$refs.tree.find({id: unit.uuid})
        let isCurrent = (unit.uuid === this.currentUnit.uuid)
        let isParent = (this.currentUnit.parents.indexOf(unit.uuid) !== -1)

        if (isCurrent) {
          setTimeout(node.select.bind(node), 0)
        } else if (isParent) {
          setTimeout(node.expand.bind(node), 0)
        }
      },

      fetch (node) {
        if (!this.orgUuid || node.fetching) {
          // return something that does nothing
          return new Promise(() => [])
        }

        node.fetching = true

        return OrganisationUnit.getChildren(node.id, this.atDate)
          .then(response => {
            this.addNodes(node, response)

            node.fetching = false
          }).catch(error => {
            console.error('fetch failed', error)

            node.fetching = false

            throw error
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
