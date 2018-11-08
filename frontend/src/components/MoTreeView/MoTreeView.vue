<template>
  <div class="orgunit-tree">
    <liquor-tree
      ref="tree"
      :data="treeData"
      :options="treeOptions"/>
  </div>
</template>

<script>
  import { EventBus } from '@/EventBus'
  import { mapGetters } from 'vuex'
  import Organisation from '@/api/Organisation'
  import OrganisationUnit from '@/api/OrganisationUnit'
  import LiquorTree from 'liquor-tree'

  export default {
    components: {
      LiquorTree
    },

    props: {
      /**
       * Defines a orgUuid.
       */
      unitUuid: String,

      /**
       * Defines a atDate.
       */
      atDate: [Date, String]
    },

    computed: {
      ...mapGetters({
        orgUuid: 'organisation/getUuid'
      })

    },

    data () {
      let vm = this

      return {
        treeData: [],
        units: {},

        treeOptions: {
          minFetchDelay: 0,
          parentSelect: true,

          fetchData (node) {
            return vm.fetch(node)
          }
        }
      }
    },

    mounted () {
      const vm = this

      this.$refs.tree.$on('node:selected', node => {
        vm.$emit('input', vm.units[node.id])
      })

      EventBus.$on('update-tree-view', () => vm.updateTree())

      // this.$refs.tree.$on('node:expanded', node => {
      //   console.log('expanded', node.text, node.id)
      // })

      // this.$refs.tree.$on('node:unselected', node => {
      //   console.log('deselected', node.text)
      // })

      // this.$refs.tree.$on('tree:data:fetch', node => {
      //   console.log('fetching', node.text, node.id)
      // })

      // this.$refs.tree.$on('tree:data:received', node => {
      //   console.log('received', node.text, node.children)
      // })

      this.updateTree()
    },

    watch: {
      unitUuid (newVal, oldVal) {
        this.log(`changing unit from ${oldVal} to ${newVal} (org=${this.orgUuid})`)

        if (this.units && this.units[newVal]) {
          this.setSelection(newVal)
        } else if (newVal !== oldVal) {
          this.updateTree()
        }
      },

      orgUuid (newVal, oldVal) {
        let vm = this

        this.log(`changing organisation from ${oldVal} to ${newVal}`)

        // in order to avoid updating twice, only do so when no unit
        // is configured; otherwise, we'll update when the unit clears
        //
        // however, as we invariably get the org notification *before*
        // the unit notification, delay the check by 100ms -- or 0.1s
        // -- so that we still update when we don't get a unit
        //
        // yes, this is a bit of a hack :(
        setTimeout(() => {
          if (oldVal || !vm.unitUuid) {
            vm.updateTree()
          }
        }, 100)
      },

      atDate () {
        this.updateTree()
      }
    },

    methods: {
      log (s, ...args) {
        console.log('TREE: ' + s, ...args)
      },

      /**
       * Select the unit corresponding to the given ID, assuming it's present.
       */
      setSelection (unitid) {
        if (!unitid) {
          unitid = this.unitUuid
        }

        this.log(`selecting ${unitid}`)
        this.$refs.tree.tree.unselectAll()

        for (let n of this.$refs.tree.tree.find({id: unitid})) {
          n.expandTop()
          n.select()
        }
      },

      /**
       * Convert a unit object into a node suitable for adding to the
       * tree.
       *
       * This method handles both eager and lazy loading of child nodes.
       */
      toNode (unit) {
        this.units[unit.uuid] = unit

        return {
          text: unit.name,
          isBatch: unit.children ? false : unit.child_count > 0,
          id: unit.uuid,
          children: unit.children
            ? unit.children.map(this.toNode.bind(this)) : null
        }
      },

      /**
       * Reset and re-fetch the tree.
       */
      updateTree () {
        let vm = this
        let tree = this.$refs.tree

        if (!this.orgUuid) {
          return
        }

        this.log(`updating tree org=${this.orgUuid} unit=${this.unitUuid}`)

        if (this.unitUuid) {
          OrganisationUnit.getTree(this.unitUuid, this.atDate)
            .then(response => {
              vm.log('injecting unit tree')

              vm.units = {}
              tree.remove({})
              tree.append(vm.toNode(response))

              vm.setSelection()
            })
        } else {
          Organisation.getChildren(this.orgUuid, this.atDate)
            .then(response => {
              vm.log('injecting org tree')

              vm.units = {}
              tree.remove({})

              for (let unit of response) {
                tree.append(vm.toNode(unit))
              }
            })
        }
      },

      fetch (node) {
        let vm = this

        this.log(`fetching ${node.text}`)

        if (!this.orgUuid || node.fetching) {
          // nothing to do, so return something that does nothing
          return new Promise(() => [])
        }

        // ensure that we only ever have a single outstanding fetch
        // per node; otherwise, double-clicking to expand leads to
        // duplicates
        node.fetching = true

        return OrganisationUnit.getChildren(node.id, this.atDate)
          .then(response => {
            node.fetching = false

            return response.map(vm.toNode.bind(vm))
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
