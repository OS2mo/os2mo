<template>
  <b-modal 
    id="employeeMove" 
    size="lg" 
    hide-footer 
    title="Flyt medarbejder"
    ref="employeeMove"
    lazy
  >
    <div>

        <employee-picker 
          v-model="employee" 
          :org="org"
        />

      <div class="form-row">
        <date-picker 
          class="col"
          label="Dato for flytning"
          v-model="move.data.validity.from"
        />
      </div>
      
      <div class="form-row">
        <engagement-picker 
          v-model="original"
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
      <button-submit :on-click-action="moveEmployee" :is-loading="isLoading" :is-disabled="isDisabled"/>
    </div>
  </div>
</b-modal>
</template>

<script>
  import Employee from '../../api/Employee'
  import '../../filters/GetProperty'
  import DatePicker from '../../components/DatePicker'
  import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
  import EngagementPicker from '../../components/EngagementPicker'
  import EmployeePicker from '../../components/EmployeePicker'
  import ButtonSubmit from '../../components/ButtonSubmit'

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
        original: {},
        move: {
          type: 'engagement',
          data: {
            validity: {}
          }
        }
      }
    },
    computed: {
      isDisabled () {
        return !this.employee.uuid || !this.move.data.validity.from || !this.move.data.org_unit || !this.original
      }
    },
    methods: {
      moveEmployee () {
        let vm = this
        vm.isLoading = true
        vm.move.uuid = this.original.uuid

        Employee.move(this.employee.uuid, [this.move])
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
