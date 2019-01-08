<template>
  <div class="orgunit-tree">
    <liquor-tree
      :ref="nameId"
      :data="treeData"
      :options="treeOptions"
      @node:selected="onNodeSelected"
      @node:removed="onNodeRemoved"
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
     * @model
     */
    value: [Object, String],

    /**
     * Defines a atDate.
     */
    atDate: [Date, String],
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

  data () {
    let vm = this

    return {
      treeData: [],
      units: {},

      treeOptions: {
        minFetchDelay: 1,
        parentSelect: true,

        fetchData (node) {
          return vm.fetch(node)
        }
      }
    }
  },

  mounted () {
    const vm = this

    EventBus.$on('update-tree-view', () => {
      vm.updateTree(true)
    })

    this.updateTree()
  },

  watch: {
    value (newVal, oldVal) {
      if (!newVal || this.units && this.units[newVal]) {
        this.setSelection(newVal)
      } else if (newVal !== oldVal) {
        this.updateTree()
      }
    },

    orgUuid (newVal, oldVal) {
      let vm = this

      // in order to avoid updating twice, only do so when no unit
      // is configured; otherwise, we'll update when the unit clears
      //
      // however, as we invariably get the org notification *before*
      // the unit notification, delay the check by 100ms -- or 0.1s
      // -- so that we still update when we don't get a unit
      //
      // yes, this is a bit of a hack :(
      setTimeout(() => {
        if (oldVal || !vm.value) {
          vm.updateTree(true)
        }
      }, 100)
    },

    atDate () {
      this.updateTree()
    }
  },

  methods: {

    onNodeSelected (node) {
      this.$emit('input', node.id)
    },

    onNodeRemoved (node) {
      delete this.units[node.id]
    },

    /**
     * Select the unit corresponding to the given ID, assuming it's present.
     */
    setSelection (unitid) {
      unitid = unitid || this.value

      this.tree.tree.unselectAll()

      let node = this.tree.tree.getNodeById(unitid)

      if (node) {
        node.expandTop()
        node.select()
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
        children: unit.children ? unit.children.map(this.toNode.bind(this)) : null,
        state: {
          expanded: Boolean(unit.children),
        }
      }
    },

    /**
     * Reset and re-fetch the tree.
     */
    updateTree (force) {
      let vm = this

      if (force) {
        this.tree.remove({}, true)
        this.units = {}
      }

      if (this.value) {
        OrganisationUnit.getAncestorTree(this.value, this.atDate)
          .then(response => {
            vm.addNode(response, null)
            vm.tree.sort()
            vm.setSelection()
          })
      } else if (this.orgUuid) {
        Organisation.getChildren(this.orgUuid, this.atDate)
          .then(response => {
            vm.units = {}

            for (let unit of response) {
              vm.addNode(unit, null)
            }

            vm.tree.sort()
            vm.setSelection()
          })
      }
    },

    fetch (node) {
      let vm = this

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
          node.fetching = false
          throw error
        })
    }
  }
}
</script>

<!-- this particular styling is not scoped, otherwise liqour tree 
     cannot detect the overwrites. to ensure that we _always_ win, we
     increase the specificity of the selectors  -->
<style>
  .orgunit-tree .tree > .tree-root, .tree-content {
     padding: 0;
   }

   .orgunit-tree .tree-children {
     transition-timing-function: ease-in-out;
     transition-duration: 150ms;
   }

  .orgunit-tree .tree-node.selected > .tree-content {
    background-color: #007bff;
  }

  .orgunit-tree .tree-node.selected > .tree-content > .tree-anchor {
    color: #fff;
  }
</style>
