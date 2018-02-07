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
        <employee-picker 
          v-model="employee" 
          :org="org"
        />
      </div>

      <div class="form-row">
        <date-picker 
          class="col"
          label="Dato for flytning"
          v-model="move.data.valid_from"
        />
      </div>
      
      <div class="form-row">
        <engagement-picker 
          v-model="move.original"
          :employee="employee"
        />
      </div>

      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          v-model="move.data.org_unit"
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
  import DatePicker from '../components/DatePicker'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import EngagementPicker from '../components/EngagementPicker'
  import EmployeePicker from '../components/EmployeePicker'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      Employee,
      DatePicker,
      OrganisationUnitPicker,
      EngagementPicker,
      EmployeePicker,
      ButtonSubmit
    },
    props: {
      org: {
        type: Object,
        required: true
      }
    },
    data () {
      return {
        orgUnit: {},
        employee: {},
        selectedDate: null,
        selectedEngagement: null,
        engagements: [],
        engagement: {},
        move: {
          type: 'engagement',
          data: {}
        }
      }
    },
    methods: {
      moveEmployee () {
        let vm = this

        this.move.uuid = this.move.original.uuid

        console.log(this.move)
        Employee.editEmployee(this.employee.uuid, [this.move])
        .then(response => {
          console.log(response)
          vm.$refs.employeeMove.hide()
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>