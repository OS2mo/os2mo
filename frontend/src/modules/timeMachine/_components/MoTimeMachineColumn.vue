SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <div class="card">
      <div class="form-row">
        <mo-input-date v-model="date"/>
      </div>

      <mo-org-tree-view v-model="unitUuid" :at-date="date"
      />
    </div>

    <div class="card margin-top" v-if="unitUuid">
      <h4>{{orgUnit.name}}</h4>

      <organisation-detail-tabs
        :uuid="orgUnit.uuid"
        :org-unit-info="orgUnit"
        :content="$store.getters[storeId + '/GET_DETAILS']"
        @show="loadContent($event)"
        timemachine-friendly
      />
    </div>
  </div>
</template>

<script>
/**
 * A timemachine column component.
 */

import { MoInputDate } from '@/components/MoInput'
import MoOrgTreeView from '@/components/MoTreeView/MoOrgTreeView'
import OrganisationDetailTabs from '@/views/organisation/OrganisationDetailTabs'
import orgUnitStore from '@/store/modules/organisationUnit'

export default {
  components: {
    MoInputDate,
    MoOrgTreeView,
    OrganisationDetailTabs
  },
  props: {
    storeId: { type: String, required: true }
  },

  data () {
    return {
      /**
       * The date, org, orgUnit component value.
       * Used to detect changes and restore the value.
       */
      date: new Date()
    }
  },

  computed: {
    unitUuid: {
      get () {
        return this.orgUnit && this.orgUnit.uuid
      },
      set (val) {
        this.$store.dispatch(this.storeId + '/SET_ORG_UNIT', val)
      }
    },

    orgUnit () {
      return this.$store.getters[this.storeId + '/GET_ORG_UNIT']
    }
  },
  created () {
    // avoid reregistering the module if it already exists
    if (!this.$store._modules.root._children[this.storeId]) {
      this.$store.registerModule(this.storeId, orgUnitStore)
    }
  },
  destroyed () {
    this.$store.unregisterModule(this.storeId)
  },
  methods: {
    loadContent (event) {
      this.latestEvent = event

      if (this.orgUnit) {
        this.$store.dispatch(this.storeId + '/SET_ORG_UNIT', this.unitUuid)
        this.$store.dispatch(this.storeId + '/SET_DETAIL', event)
      }
    }
  }
}
</script>

<style scoped>
  .margin-top {
    margin-top: 1rem;
  }
</style>
