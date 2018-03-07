<template>
<b-modal 
    id="employeeTerminate" 
    size="lg" 
    hide-footer 
    title="Afslut medarbejder"
    ref="employeeTerminate"
    lazy
  >
  <div class="col">
    <employee-picker v-model="employee"/>
    
    <div class="form-row">
      <date-picker label="Slutdato" v-model="terminate.validity.from"/>
    </div>
    
    <div class="float-right">
      <button-submit :on-click-action="endEmployee" :is-loading="isLoading" :is-disabled="isDisabled"/>
    </div>
  </div>
</b-modal>
</template>

<script>
  import Employee from '../../api/Employee'
  import EmployeePicker from '../../components/EmployeePicker'
  import DatePicker from '../../components/DatePicker'
  import ButtonSubmit from '../../components/ButtonSubmit'

  export default {
    components: {
      EmployeePicker,
      DatePicker,
      ButtonSubmit
    },
    data () {
      return {
        isLoading: false,
        employee: {},
        terminate: {
          validity: {}
        }
      }
    },
    computed: {
      isDisabled () {
        return !this.employee.uuid || !this.terminate.validity.from
      }
    },
    methods: {
      endEmployee () {
        let vm = this
        vm.isLoading = true
        Employee.terminate(this.employee.uuid, this.terminate)
        .then(response => {
          vm.isLoading = false
          vm.$refs.employeeTerminate.hide()
        })
      }
    }
  }
</script>
