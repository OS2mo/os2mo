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
          v-model="move.data.validity.from"
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
          label="Angiv enhed" 
          class="col" 
          v-model="move.data.org_unit"
        />       
      </div>

    <div class="float-right">
      <button-submit @click.native="moveEmployee" :is-loading="isLoading"/>
    </div>
  </div>
</b-modal>
</template>

<script>
  import Employee from '../api/Employee'
  import '../filters/GetProperty'
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
        employee: {},
        isLoading: false,
        move: {
          type: 'engagement',
          data: {
            validity: {}
          }
        }
      }
    },
    methods: {
      moveEmployee () {
        let vm = this
        vm.isLoading = true
        vm.move.uuid = this.move.original.uuid

        Employee.editEmployee(this.employee.uuid, [this.move])
        .then(response => {
          vm.isLoading = false
          vm.$refs.employeeMove.hide()
        })
        .catch(err => {
          console.log(err)
          vm.isLoading = false
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>