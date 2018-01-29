<template>
  <div>
    <h1>Tidsmaskinen</h1>
  <div class="row">
      <div class="col">
        <div class="card">
          <div class="form-row">
          <date-picker v-model="dateLeft"/>
          </div>
          <organisation-picker
            v-model="orgLeft"
            :at-date="dateLeft"
            />
          <treeview 
            :orgUuid="orgLeft.uuid"
            v-model="orgUnitLeft"
          />

          Navn: {{orgUnitLeft.name}}
          <organisation-detail-tabs :uuid="orgUnitLeft.uuid"/>
        </div>
      </div>
      <div class="col">
        <div class="card">
          <div class="form-row">
            <date-picker/>
          </div>
          <organisation-picker v-model="orgRight"/>
          <treeview 
            :orgUuid="orgRight.uuid"
            v-model="orgUnitRight"
          />
           Navn: {{orgUnitRight.name}}
          <organisation-detail-tabs :uuid="orgUnitRight.uuid"/>
        </div>
      </div>
  </div>
  </div>
</template>

<script>
  import DatePicker from '../components/DatePicker'
  import OrganisationPicker from '../components/OrganisationPicker'
  import Treeview from '../components/Treeview'
  import OrganisationDetailTabs from '../organisation/OrganisationDetailTabs'

  export default {
    components: {
      DatePicker,
      OrganisationPicker,
      Treeview,
      OrganisationDetailTabs
    },
    data () {
      return {
        dateLeft: null,
        dateRight: null,
        orgLeft: {},
        orgRight: {},
        orgUnitLeft: {},
        orgUnitRight: {}
      }
    },
    created () {},
    methods: {}
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>