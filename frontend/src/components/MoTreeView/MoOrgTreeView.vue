SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <mo-tree-view
    ref="treeview"
    v-model="treeValue"
    :multiple="multiple"
    :disabled-unit="disabledUnit"
    :get_ancestor_tree="get_ancestor_tree"
    :get_toplevel_children="get_toplevel_children"
    :get_children="get_children"
    :get_store_uuid="get_store_uuid"
    :atDate="atDate"
    v-bind="$attrs"
    v-on="$listeners"
  >
    <template v-for="(_, slot) of $scopedSlots" v-slot:[slot]="scope">
      <slot :name="slot" v-bind="scope" />
    </template>
  </mo-tree-view>
</template>

<script>
/**
 * A organisation unit picker component.
 */

import MoTreeView from "@/components/MoTreeView/MoTreeView"
import { Organisation as OrgStore } from "@/store/actions/organisation"
import Organisation from "@/api/Organisation"
import OrganisationUnit from "@/api/OrganisationUnit"

export default {
  name: "MoOrgTreeView",

  components: {
    MoTreeView,
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
     * Defines the date for rendering the tree; used for the time machine.
     */
    atDate: { type: [Date, String] },

    /**
     * UUID of unselectable unit.
     */
    disabledUnit: String,

    /**
     * Select more than one node
     */
    multiple: Boolean,
  },

  computed: {
    treeValue: {
      set(val) {
        this.$emit("input", val)
      },
      get() {
        return this.value
      },
    },
  },

  data() {
    let vm = this

    return {
      get_ancestor_tree(uuid, date) {
        return OrganisationUnit.getAncestorTree(uuid, date, vm._extraQueryArgs)
      },

      get_toplevel_children(uuid, date) {
        return Organisation.getChildren(uuid, date, vm._extraQueryArgs)
      },

      get_children(uuid, date) {
        return OrganisationUnit.getChildren(uuid, date, vm._extraQueryArgs)
      },

      get_store_uuid() {
        /**
         * The tree view itself is dependent on the currently active
         * organisation. Among other things, we should only show the units
         * for that organisation, and also ensure that we reset the view
         * whenever it changes.
         */
        return OrgStore.getters.GET_UUID
      },

      _extraQueryArgs: undefined,
    }
  },

  methods: {
    setFilter(val) {
      this._extraQueryArgs = val === null ? undefined : { org_unit_hierarchy: val }
      this.$refs.treeview.updateTree(true)
    },
  },
}
</script>
