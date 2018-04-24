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
              ignore-event
            />

            <treeview 
              v-model="orgUnitLeft"
              :at-date="dateLeft"
              :org-uuid="orgLeft.uuid"
            />
          </div>

          <div class="card margin-top" v-if="orgUnitLeft">
            <h4>{{orgUnitLeft.name}}</h4>
            <organisation-detail-tabs 
              :uuid="orgUnitLeft.uuid"
              :at-date="dateLeft"
              timemachine-friendly
            />
          </div>
        </div>

        <div class="col">
          <div class="card">
            <div class="form-row">
              <date-picker v-model="dateRight"/>
            </div>
            <organisation-picker 
              :at-date="dateRight"
              v-model="orgRight"
              ignore-event
              />
              
            <treeview 
              :org-uuid="orgRight.uuid"
              :at-date="dateRight"
              v-model="orgUnitRight"
            />
          </div>

          <div class="card margin-top" v-if="orgUnitRight">
            <h4>{{orgUnitRight.name}}</h4>
            <organisation-detail-tabs 
              :uuid="orgUnitRight.uuid"
              :at-date="dateRight"
              timemachine-friendly/>
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
        dateLeft: new Date(),
        dateRight: new Date(),
        orgLeft: {},
        orgRight: {},
        orgUnitLeft: null,
        orgUnitRight: null
      }
    },
    watch: {
      orgLeft () {
        this.orgUnitLeft = null
      },
      orgRight () {
        this.orgUnitRight = null
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.margin-top {
  margin-top: 1rem;
}
</style>