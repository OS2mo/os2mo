<template>
  <b-modal 
    id="employeeTerminate" 
    size="lg" 
    hide-footer 
    title="Afslut medarbejder"
    ref="employeeTerminate"
    lazy
  >
    <form @submit.prevent="endEmployee">
      <div class="col">
        <employee-picker v-model="employee" required/>
        
        <div class="form-row">
          <date-picker label="Slutdato" v-model="terminate.validity.from" required/>
        </div>
        
        <div class="float-right">
          <button-submit :is-loading="isLoading" :is-disabled="!formValid"/>
        </div>
      </div>
    </form>
  </b-modal>
</template>

<script>
import Employee from '../../api/Employee'
import EmployeePicker from '../../components/EmployeePicker'
import DatePicker from '../../components/DatePicker'
import ButtonSubmit from '../../components/ButtonSubmit'

export default {
  $_veeValidate: {
    validator: 'new'
  },
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
    },

    formValid () {
      // loop over all contents of the fields object and check if they exist and valid.
      return Object.keys(this.fields).every(field => {
        return this.fields[field] && this.fields[field].valid
      })
    }
  },
  mounted () {
    this.$root.$on('bv::modal::hidden', resetData => {
      Object.assign(this.$data, this.$options.data())
    })
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
