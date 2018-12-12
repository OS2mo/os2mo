<template>
  <div class="orgunit-tree">
    <liquor-tree
      :ref="nameId"
      :v-model="selected"
      :data="treeData"
      :options="treeOptions"
      @node:checked="onNodeChecked"
      @node:unchecked="onNodeUnchecked"
    >

      <div class="tree-scope" slot-scope="{ node }">
        <template>
          <icon name="users"/>

          <span class="text">
            {{ node.text }}
          </span>
        </template>
      </div>
    </liquor-tree>
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
    atDate: [Date, String],

    /**
     * Select more than one node
     */
    multiple: Boolean
  },

  data () {
    let vm = this

    return {
      treeData: [],
      selected: undefined,
      units: {},

      treeOptions: {
        parentSelect: true,
        multiple: false,
        checkbox: this.multiple,
        checkOnSelect: this.multiple,
        autoCheckChildren: false,
        minFetchDelay: 1,
        fetchData (node) {
          return vm.fetch(node)
        }
      }
    }
  },

  computed: {
    ...mapGetters({
      orgUuid: 'organisation/getUuid'
    }),

    nameId () {
      return 'moTreeView' + this._uid
    },

    tree () {
      return this.$refs[this.nameId]
    },

    contents () {
      function visitNode (node, level) {
        if (!node) {
          return null
        } else if (node instanceof Array) {
          return node
            .filter(c => c.visible())
            .map(c => visitNode(c, level))
        }

        let text = node.selected() ? `=+= ${node.text} =+=` : node.text

        if (node.expanded()) {
          const r = {}

          r[text] = visitNode(node.children, level + 1)

          return r
        } else if (node.hasChildren()) {
          return '> ' + text
        } else {
          return text
        }
      }

      return visitNode(this.tree.getRootNode(), 0)
    }
  },

  mounted () {
    const vm = this

    this.tree.$on('node:added', node => {
      console.log(`TREE: adding node ${node.id}`)
    })

    this.tree.$on('node:removed', node => {
      console.log(`TREE: removing node ${node.id}`)
      delete vm.units[node.id]
    })

    this.tree.$on('node:selected', node => {
      console.log(`TREE: selected node ${node.id}`)

      vm.$emit('input', vm.units[node.id])
    })

    this.tree.$on('node:expanded', node => {
      console.log('TREE: expanded', node.text, node.id)
    })

    EventBus.$on('update-tree-view', () => {
      console.log(`TREE: update tree view!`)
      vm.updateTree(true)
    })

    this.updateTree()
  },

  watch: {
    unitUuid (newVal, oldVal) {
      console.log(`TREE: changing unit from ${oldVal} to ${newVal} (org=${this.orgUuid})`)

      if (this.units && this.units[newVal]) {
        this.setSelection(newVal)
      } else if (newVal !== oldVal) {
        this.updateTree()
      }
    },

    selected: {
      handler (newVal, oldVal) {
        console.log(`TREE: selected changed to ${newVal}`)
      },
      deep: true
    },

    treeData: {
      handler (newVal, oldVal) {
        console.log(`TREE: treeData changed to ${newVal}`)
      },
      deep: true
    },

    orgUuid (newVal, oldVal) {
      let vm = this

      console.log(`TREE: changing organisation from ${oldVal} to ${newVal}`)

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
          vm.updateTree(true)
        }
      }, 100)
    },

    atDate () {
      this.updateTree()
    }
  },

  methods: {

    onNodeChecked (event) {
      if (!(this.selected instanceof Array)) {
        this.selected = []
      }
      this.selected.push(event.id)
      this.$emit('input', this.selected)
    },

    onNodeUnchecked (event) {
      const index = this.selected.indexOf(event.id)
      if (index !== -1) this.selected.splice(index, 1)
      this.$emit('input', this.selected)
    },

    /**
     * Select the unit corresponding to the given ID, assuming it's present.
     */
    setSelection (unitid) {
      if (!unitid) {
        unitid = this.unitUuid
      }

      console.log(`TREE: selecting ${unitid}`)
      this.tree.tree.unselectAll()

      let n = this.tree.tree.getNodeById(unitid)

      if (n) {
        n.expandTop()
        n.select()
      }
    },

    addNode (unit, parent) {
      let preexisting = this.tree.tree.getNodeById(unit.uuid)

      if (preexisting) {
        if (unit.children) {
          for (let child of unit.children) {
            this.addNode(child, preexisting)
          }
        }

        preexisting.text = unit.name
        preexisting.isBatch = unit.children ? false : unit.child_count > 0
      } else if (parent) {
        parent.append(this.toNode(unit))
      } else {
        this.tree.append(this.toNode(unit))
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
        children: unit.children ? unit.children.map(this.toNode.bind(this)) : null
      }
    },

    /**
     * Reset and re-fetch the tree.
     */
    updateTree (force) {
      let vm = this

      if (!this.orgUuid || !this.tree) {
        return
      }

      if (force) {
        this.tree.remove({}, true)
        this.units = {}
      }

      if (this.unitUuid) {
        OrganisationUnit.getAncestorTree(this.unitUuid, this.atDate)
          .then(response => {
            console.log('TREE: injecting unit tree', response.uuid)

            vm.addNode(response, null)
            vm.tree.sort()

            vm.setSelection()
          })
      } else {
        Organisation.getChildren(this.orgUuid, this.atDate)
          .then(response => {
            console.log('TREE: injecting org tree')

            vm.units = {}

            for (let unit of response) {
              vm.addNode(unit, null)
            }

            vm.tree.sort()
          })
      }
    },

    fetch (node) {
      let vm = this

      console.log(`TREE: fetching ${node.text}`)

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

<!-- this particular styling is not scoped, otherwise liqour tree cannot detect the overwrites -->
<style>
  .tree > .tree-root, .tree-content {
     padding: 0;
   }

   .tree-children {
     transition-timing-function: ease-in-out;
     transition-duration: 150ms;
   }

  .tree-node.selected > .tree-content {
    background: #007bff;
  }

  .tree-node.selected > .tree-content > .tree-anchor {
    color: #fff;
  }
</style>
