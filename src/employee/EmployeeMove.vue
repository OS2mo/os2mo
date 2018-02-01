<template>
<b-modal 
    id="employeeMove" 
    size="lg" 
    hide-footer 
    title="Flyt medarbejder"
    ref="employeeMove"
  >
  <div>
      <div class="form-row">
        <date-picker 
          class="col"
          label="Dato for flytning"
          v-model="selectedDate"
        />
      </div>
      
      <div class="form-row">
        <div class="form-group">
        <!-- THIS THING NEEDS TO DIE SOMETIME -->
        <label>Vælg engagement som skal flyttes</label>
        <select
          class="form-control" 
          v-model="selectedEngagement"
        >
          <option disabled>Vælg engagement</option>
          <option 
            v-for="e in engagements" 
            :key="e.uuid"
            :value="e.uuid"
          >
            {{e.job_function | getProperty('name')}} ({{e.org_unit | getProperty('name')}})
          </option>
        </select>
        </div>
        </div>
        <!-- HOPEFULLY IT IS DEAD NOW. OTHERWISE GO BACK AND KILL IT AGAIN -->
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          v-model="orgUnit"
        />       
      </div>

    <div class="float-right">
      <button-submit @click.native="moveEmployee"/>
    </div>
  </div>
</b-modal>
</template>

<script>
  import Employee from '../api/Employee'
  import '../filters/GetProperty'
  import DatePicker from '../components/DatePicker'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      Employee,
      DatePicker,
      OrganisationUnitPicker,
      ButtonSubmit
    },
    data () {
      return {
        orgUnit: {},
        selectedDate: null,
        selectedEngagement: null,
        engagements: []
      }
    },
    created () {
      this.getEngagements()
    },
    methods: {
      // part of the death sin
      getEngagements () {
        console.log('get engagements')
        var vm = this
        Employee.getEngagementDetails(this.$route.params.uuid)
        .then(response => {
          console.log(response)
          vm.engagements = response
        })
      },
      // carry on

      moveEmployee () {
        let vm = this
        let edit = [{
          type: 'engagement',
          uuid: this.selectedEngagement,
          data: {
            valid_from: this.selectedDate,
            valid_to: null,
            org_unit_uuid: this.orgUnit.uuid
          }
        }]
        Employee.editEmployee(this.$route.params.uuid, edit)
        .then(response => {
          vm.$refs.employeeMove.hide()
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>