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
        :org-unit-info="orgUnitInfo"
        @show="loadContent($event)"
        :content="$store.getters[storeId + '/GET_DETAILS']"
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
import orgUnit from '@/store/modules/organisationUnit'

export default {
  components: {
    MoDatePicker,
    MoOrganisationPicker,
    MoTreeView,
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
      date: new Date(),
      org: {},
      orgUnit: null
    }
  },
  computed: {
    orgUnitInfo () {
      return this.$store.getters[this.storeId + '/GET_ORG_UNIT']
    }
  },

  watch: {
    /**
     * Whenever org change, update.
     */
    org () {
      this.orgUnit = null
    },
    orgUnit (val) {
      this.$store.dispatch(this.storeId + '/SET_ORG_UNIT', val.uuid)
    }
  },
  created () {
    // avoid reregistering the module if it already exists
    if (!this.$store._modules.root._children[this.storeId]) {
      this.$store.registerModule(this.storeId, orgUnit)
    }
  },
  destroyed () {
    this.$store.unregisterModule(this.storeId)
  },
  methods: {
    loadContent (event) {
      event.atDate = this.date
      this.$store.dispatch(this.storeId + '/SET_DETAIL', event)
    }
  }
}
</script>

<style scoped>
  .margin-top {
    margin-top: 1rem;
  }
</style>
