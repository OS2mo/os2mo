SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="unit-tree">
    <mo-loader v-show="isLoading" />
    <div v-show="!isLoading" class="scroll">
      <liquor-tree
        :ref="_nameId"
        :data="treeData"
        :options="treeOptions"
        @node:selected="onNodeSelected"
        @node:checked="onNodeCheckedChanged"
        @node:unchecked="onNodeCheckedChanged"
      >
        <div class="tree-scope" slot-scope="{ node }" :title="node.text">
          <template>
            <icon name="users" />
            <span class="text">{{ node.text }}</span>
          </template>
        </div>
      </liquor-tree>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex"
import { EventBus, Events } from "@/EventBus"
import MoLoader from "@/components/atoms/MoLoader"
import LiquorTree from "liquor-tree"
import { AtDate } from "@/store/actions/atDate"

export default {
  components: {
    MoLoader,
    LiquorTree,
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
    value: { type: [String, Array] },

    /**
     * UUID of unselectable unit.
     */
    disabledUnit: String,

    /**
     * Select more than one node
     */
    multiple: Boolean,

    /**
     * Function to fetch ancestor tree
     */
    get_ancestor_tree: Function,

    /**
     * Function to fetch top-level children
     */
    get_toplevel_children: Function,

    /**
     * Function to fetch non top-level children
     */
    get_children: Function,

    /**
     * Function to return store getter key
     */
    get_store_uuid: Function,
  },

  computed: {
    unitUuid() {
      return this.$store.getters[this.get_store_uuid()]
    },

    /**
     * @private
     */
    _nameId() {
      return "moTreeView" + this._uid
    },

    /**
     * Accessor for the LiquorTree instance.
     *
     * @protected
     */
    tree() {
      return this.$refs[this._nameId]
    },

    /**
     * A string representation of the currently rendered tree, useful
     * for inspection and tests, with highlighting of expansion and
     * selection states.
     */
    contents() {
      function visitNode(node, level) {
        if (!node) {
          return null
        } else if (node instanceof Array) {
          return node.filter((c) => c.visible()).map((c) => visitNode(c, level))
        }

        let text = node.text

        if (node.checked()) {
          text = `\u2713 ${text}`
        }

        if (node.selected()) {
          text = `=+= ${text} =+=`
        }

        if (node.disabled()) {
          text = `~~~ ${text} ~~~`
        }

        if (node.expanded()) {
          const r = {}
          r[text] = visitNode(node.children, level + 1)
          return r
        } else if (node.hasChildren()) {
          return "> " + text
        } else {
          return text
        }
      }

      return visitNode(this.tree.getRootNode(), 0)
    },

    ...mapGetters({
      atDate: AtDate.getters.GET,
    }),
  },

  data() {
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
        autoDisableChildren: false,
        autoCheckChildren: false,
        minFetchDelay: 1,
        fetchData(node) {
          return vm.fetch(node)
        },
      },

      isLoading: true,

      _atDate: undefined,
    }
  },

  mounted() {
    this._atDate = this.$store.getters[AtDate.getters.GET]
    EventBus.$on(Events.UPDATE_TREE_VIEW, this.listener)
    this.updateTree()
  },

  beforeDestroy() {
    EventBus.$off(Events.UPDATE_TREE_VIEW, this.listener)
  },

  watch: {
    /**
     * Update the selection when the value changes.
     */
    value(newVal, oldVal) {
      if (JSON.stringify(newVal) === JSON.stringify(oldVal)) {
        return
      }

      const missing = this.tree.tree
        ? this.toArray(newVal).filter((v) => !this.tree.tree.getNodeById(v))
        : []

      if (missing.length) {
        this.updateTree()
      } else {
        this.setSelection(newVal)
      }
    },

    /**
     * Reset the selection when the organisation changes.
     */
    unitUuid(newVal, oldVal) {
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
        if (oldVal || !vm.value || vm.value.length === 0) {
          vm.updateTree(true)
        }
      }, 100)
    },

    disabledUnit(newVal) {
      for (const oldNode of this.tree.findAll({ disabled: true })) {
        if (oldNode.id !== newVal) {
          oldNode.enable()
        }
      }

      let newNode = this.tree.tree.getNodeById(newVal)

      if (newNode && newNode.enabled()) {
        newNode.uncheck()
        newNode.unselect()
        newNode.disable()
      }
    },

    /**
     * Re-render the tree when the date changes.
     */
    atDate(newVal) {
      this._atDate = newVal
      this.updateTree(true)
    },
  },

  methods: {
    onNodeCheckedChanged(node) {
      if (this.multiple) {
        let checked = this.getSelection()

        this.$emit("input", checked)
      }
    },

    /**
     * Propagate the selection to the model.
     *
     * @protected
     */
    onNodeSelected(node) {
      if (!this.multiple) {
        this.$emit("input", node.id)
      }
    },

    getSelection() {
      let nodes = this.multiple ? this.tree.checked() : this.tree.selected()
      return this.toArray(nodes.map((n) => n.id))
    },

    toArray(values) {
      let vs = values ? (values instanceof Array ? values : [values]) : []

      vs.sort()

      return vs
    },

    /**
     * Select the units corresponding to the given IDs, assuming
     * they're present, and updating the tree otherwise.
     */
    setSelection(unitids) {
      // wrap the values in a list, if necessary, handling absence
      const newVal = this.toArray(unitids)
      const oldVal = this.getSelection()

      // handle removals
      for (const uuid of oldVal.filter((v) => !newVal.includes(v))) {
        const node = this.tree.tree.getNodeById(uuid)

        if (this.multiple) {
          node.uncheck()
        } else {
          node.unselect()
        }
      }

      // handle additions
      for (const uuid of newVal.filter((v) => !oldVal.includes(v))) {
        const node = this.tree.tree.getNodeById(uuid)

        if (node) {
          node.expandTop()

          if (this.multiple) {
            node.check()
          } else {
            node.select()
          }
        }
      }
    },

    /**
     * Add the given nodes to the tree.
     */
    addNodes(units) {
      for (let unit of units) {
        this.addNode(unit, null)
      }

      this.tree.sort()
      this.setSelection(this.value)
      this.isLoading = false
    },

    /**
     * Add the given node to the tree, nested under the parent, specified, or
     * root otherwise.
     */
    addNode(unit, parent) {
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
    toNode(unit) {
      return {
        text: unit.name,
        isBatch: unit.children ? false : unit.child_count > 0,
        id: unit.uuid,
        children: unit.children ? unit.children.map(this.toNode.bind(this)) : null,
        state: {
          disabled: unit.uuid === this.disabledUnit,
          expanded: Boolean(unit.children),
        },
      }
    },

    /**
     * Reset and re-fetch the tree.
     */
    updateTree(force) {
      this.isLoading = true
      if (force) {
        this.tree.remove({}, true)
      }
      if (this.multiple ? this.value.length > 0 : this.value) {
        this.get_ancestor_tree(this.value, this._atDate).then((response) => {
          // Check if ancestor is empty
          if (response.length === 0) {
            // Ancestor tree is empty, reset to top-level children
            this.get_toplevel_children(this.unitUuid, this._atDate).then(this.addNodes)
          } else {
            // Add ancestor tree
            this.addNodes(response)
          }
        })
      } else if (this.unitUuid) {
        this.get_toplevel_children(this.unitUuid, this._atDate).then(this.addNodes)
      }
    },

    /**
     * LiquorTree lazy data fetcher.
     */
    fetch(node) {
      let vm = this

      if (!this.unitUuid || node.fetching) {
        // nothing to do, so return something that does nothing
        return new Promise(() => [])
      }

      // ensure that we only ever have a single outstanding fetch
      // per node; otherwise, double-clicking to expand leads to
      // duplicates
      node.fetching = true

      return this.get_children(node.id, this._atDate)
        .then((response) => {
          node.fetching = false
          return response.map(vm.toNode.bind(vm))
        })
        .catch((error) => {
          node.fetching = false
          throw error
        })
    },

    listener() {
      this.updateTree(true)
    },

    updateValidity(validity) {
      this._atDate = validity.from
      this.updateTree(true)
    },
  },
}
</script>

<!-- this particular styling is not scoped, otherwise liqour tree
     cannot detect the overwrites. to ensure that we _always_ win, we
     increase the specificity of the selectors  -->
<style>
.unit-tree .tree > .tree-root,
.tree-content {
  padding: 0.2vh;
}

.unit-tree .tree-children {
  transition-timing-function: ease-in-out;
  transition-duration: 150ms;
}

.unit-tree .tree-node.selected > .tree-content {
  background-color: #007bff;
}

.unit-tree .tree-node.selected > .tree-content > .tree-anchor {
  color: #fff;
}
</style>
