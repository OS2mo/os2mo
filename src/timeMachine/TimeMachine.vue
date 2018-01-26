<template>
  <div>
    <h1>{{ msg }}</h1>
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
          {{orgUnitLeft}}
          <!-- <organisation-detail :orgUnit="orgUnitLeft"/> -->
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
          {{orgUnitRight}}
          <!-- <organisation-detail :orgUnit="orgUnitRight"/> -->
        </div>
      </div>
  </div>
  </div>
</template>

<script>
  import DatePicker from '../components/DatePicker'
  import OrganisationPicker from '../components/OrganisationPicker'
  import Treeview from '../components/Treeview'
  import OrganisationDetail from '../organisation/OrganisationDetail'

  export default {
    components: {
      DatePicker,
      OrganisationPicker,
      Treeview,
      OrganisationDetail
    },
    data () {
      return {
        msg: 'Her kommer tidsmaskinen',
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