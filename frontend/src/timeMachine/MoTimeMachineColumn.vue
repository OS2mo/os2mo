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
        date: new Date(),
        org: {},
        orgUnit: null
      }
    },

    watch: {
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