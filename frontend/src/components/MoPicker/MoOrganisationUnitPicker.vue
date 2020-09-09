SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0

<script>
/**
 * A organisation unit picker component.
 */

import MoTreePicker from '@/components/MoPicker/MoTreePicker'
import { Organisation as OrgStore } from '@/store/actions/organisation'
import Organisation from '@/api/Organisation'
import OrganisationUnit from '@/api/OrganisationUnit'


export default {
  name: 'MoOrganisationUnitPicker',

  extends: MoTreePicker,

  methods: {
    get_name_id() {
      return 'org-unit-' + this._uid
    },

    get_validations() {
      return {
        orgunit: [this.validity, this.unitUuid]
      }
    },

    async get_unit(uuid, validity) {
      return await OrganisationUnit.get(uuid, validity)
    },

    get_ancestor_tree(uuid, date) {
      return OrganisationUnit.getAncestorTree(uuid, date)
    },

    get_toplevel_children(uuid, date) {
      return Organisation.getChildren(uuid, date)
    },

    get_children(uuid, date) {
      return OrganisationUnit.getChildren(uuid, date)
    },

    get_store_uuid() {
      /**
       * The tree view itself is dependent on the currently active
       * organisation. Among other things, we should only show the units
       * for that organisation, and also ensure that we reset the view
       * whenever it changes.
       */
      return OrgStore.getters.GET_UUID
    }
  }
}
</script>
