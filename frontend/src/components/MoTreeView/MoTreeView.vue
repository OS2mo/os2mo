<template>
  <div class="orgunit-tree">
    <liquor-tree
      :ref="_nameId"
      :data="treeData"
      :options="treeOptions"
      @node:selected="onNodeSelected"
      @node:checked="onNodeCheckedChanged"
      @node:unchecked="onNodeCheckedChanged"
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
     * This control takes a string variable as its model, representing
     * the UUID of the selected unit. Internally, the tree view does
     * have access to reasonably full objects representing the unit,
     * but they don't correspond _exactly_ to those used elsewhere, so
     * we only pass the UUID.
     *
     * @model
     */
    value: {type: [String, Array]},

    /**
     * Defines the date for rendering the tree; used for the time machine.
     */
    atDate: {type: [Date, String]},

    /**
     * Select more than one node
     */
    multiple: Boolean
  },

  computed: {
    ...mapGetters({
      /**
       * The tree view itself is dependent on the currently active
       * organisation. Among other things, we should only show the units
       * for that organisation, and also ensure that we reset the view
       * whenever it changes.
       */
      orgUuid: 'organisation/getUuid'
    }),

    /**
     * @private
     */
    _nameId () {
      return 'moTreeView' + this._uid
    },

    /**
     * Accessor for the LiquorTree instance.
     *
     * @protected
     */
    tree () {
      return this.$refs[this._nameId]
    },

    /**
     * A string representation of the currently rendered tree, useful
     * for inspection and tests, with highlighting of expansion and
     * selection states.
     */
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
      /**
       * LiquorTree model; required for some reason or other, but not
       * actually used?
       *
       * @private
       */
      treeData: [],

      /**
       * LiquorTree options.
       *
       * @private
       */
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

  mounted () {
    const vm = this

    EventBus.$on('update-tree-view', () => {
      vm.updateTree(true)
    })

    this.updateTree()
  },

  watch: {
    /**
     * Update the selection when the value changes.
     */
    value (newVal, oldVal) {
      if (this.multiple) {
        this.setChecked(newVal)
      } else {
        if (!newVal || this.tree.tree.getNodeById(newVal)) {
          this.setSelection(newVal)
        } else if (newVal !== oldVal) {
          this.updateTree()
        }
      }
    },

    /**
     * Reset the selection when the organisation changes.
     */
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

    /**
     * Re-render the tree when the date changes.
     */
    atDate () {
      this.updateTree()
    }
  },

  methods: {
    onNodeCheckedChanged (node) {
      if (this.multiple) {
        let checked = this.getChecked()
        console.log(`TREE: checked ${checked.join(', ')}`)

        this.$emit('input', checked)
      }
    },

    /**
     * Propagate the selection to the model.
     *
     * @protected
     */
    onNodeSelected (node) {
      if (!this.multiple) {
        console.log(`TREE: selected ${node.id}`)
        this.$emit('input', node.id)
      }
    },

    getSelection () {
      let current = this.tree.selected()

      return current.length ? current[0].id : null
    },

    /**
     * Select the unit corresponding to the given ID, assuming it's present.
     */
    setSelection (unitid) {
      const oldVal = getSelection()
      const newVal = unitid || this.value

      if (oldVal === newVal) {
        return
      }

      this.tree.tree.unselectAll()

      let node = this.tree.tree.getNodeById(newVal)

      if (node) {
        node.expandTop()
        node.select()
      }
    },

    getChecked () {
      const ids = this.tree.checked().map(n => n.id)
      ids.sort()
      return ids
    },

    /**
     * Select the unit corresponding to the given ID, assuming it's present.
     */
    setChecked (unitids) {
      const oldVal = this.getChecked()
      const newVal = unitids || this.value

      if (JSON.stringify(oldVal) === JSON.stringify(newVal)) {
        return
      }

      for (const uuid of oldVal) {
        if (newVal.indexOf(uuid) < 0) {
          this.tree.uncheck
        }
      }
      this.tree.tree.uncheckAll()

      for (const unitid of unitids) {
        let node = this.tree.tree.getNodeById(unitid)

        if (node) {
          node.expandTop()
          node.check(true)
        }
      }
    },

    /**
     * Add the given node to the tree, nested under the parent, specified, or
     * root otherwise.
     */
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
        this.tree.append(this.toNode(unit))
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

            for (let unit of response) {
              vm.addNode(unit, null)
            }

            vm.tree.sort()
            vm.setSelection()
          })
      }
    },

    /**
     * LiquorTree lazy data fetcher.
     */
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
