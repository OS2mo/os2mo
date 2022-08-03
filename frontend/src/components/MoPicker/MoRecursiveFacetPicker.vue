SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0

<script>
/**
 * A facet picker component.
 */

import MoTreePicker from "@/components/MoPicker/MoTreePicker"
import { Facet as FacetStore } from "@/store/actions/facet"
import Class from "@/api/Class"
import Facet from "@/api/Facet"

export default {
  name: "MoRecursiveFacetPicker",

  extends: MoTreePicker,

  props: {
    facet_uuid: String,
  },

  created() {
    this.$store.dispatch(FacetStore.actions.SET_FACET, {
      facet: this.facet_uuid,
      full: true,
    })
  },

  methods: {
    get_name_id() {
      return "facet-" + this._uid
    },

    async get_entry(newVal) {
      let details = [Facet.ClassDetails.TOP_LEVEL_FACET]
      return await Class.get(newVal, details)
    },

    get_ancestor_tree(uuid, date) {
      return Class.getAncestorTree(uuid, date)
    },

    get_toplevel_children(uuid, date) {
      return Facet.getChildren(this.facet_uuid, date)
    },

    get_children(uuid, date) {
      return Class.getChildren(uuid, date)
    },

    get_store_uuid() {
      /**
       * The tree view itself is dependent on the currently active
       * facet. Among other things, we should only show the classes
       * for that facet, and also ensure that we reset the view
       * whenever it changes.
       */
      return FacetStore.getters.GET_UUID
    },
  },
}
</script>
