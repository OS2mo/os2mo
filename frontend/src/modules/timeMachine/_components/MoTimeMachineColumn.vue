<template>
  <div>
    <div class="card">
      <div class="form-row">
        <mo-date-picker v-model="date"/>
      </div>

      <mo-organisation-picker
        v-model="org"
        :at-date="date"
        ignore-event
      />

      <mo-tree-view
        v-model="orgUnit"
        :at-date="date"
        :org-uuid="org.uuid"
      />
    </div>

    <div class="card margin-top" v-if="orgUnit">
      <h4>{{orgUnit.name}}</h4>

      <organisation-detail-tabs
        :uuid="orgUnit.uuid"
        :at-date="date"
        timemachine-friendly
      />
    </div>
  </div>
</template>

<script>
/**
   * A timemachine column component.
   */

import MoDatePicker from '@/components/atoms/MoDatePicker'
import MoOrganisationPicker from '@/components/MoPicker/MoOrganisationPicker'
import MoTreeView from '@/components/MoTreeView/MoTreeView'
import OrganisationDetailTabs from '@/organisation/OrganisationDetailTabs'

export default {
  components: {
    MoDatePicker,
    MoOrganisationPicker,
    MoTreeView,
    OrganisationDetailTabs
  },

  data () {
    return {
      /**
       * The date, org, orgUnit component value.
       * Used to detect changes and restore the value.
       */
      date: new Date(),
      org: {},
      orgUnit: null
    }
  },

  watch: {
    /**
       * Whenever org change, update.
       */
    org () {
      this.orgUnit = null
    }
  }
}
</script>

<style scoped>
  .margin-top {
    margin-top: 1rem;
  }
</style>
