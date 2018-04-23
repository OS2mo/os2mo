<template>
  <b-modal 
    id="employeeLeave" 
    size="lg" 
    title="Meld orlov"
    ref="employeeLeave"
    hide-footer 
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="createLeave">
      <mo-employee-picker v-model="employee" required/>
      <mo-leave-entry v-model="leave"/>

      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
      </div>
    </form>
  </b-modal>
</template>

<script>
import Employee from '@/api/Employee'
import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
import MoLeaveEntry from '@/components/MoEntry/MoLeaveEntry'
import ButtonSubmit from '@/components/ButtonSubmit'

export default {
  $_veeValidate: {
    validator: 'new'
  },
  components: {
    MoEmployeePicker,
    MoLeaveEntry,
    ButtonSubmit
  },
  data () {
    return {
      isLoading: false,
      employee: {},
      leave: {
        validity: {}
      }
    }
  },
  computed: {
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
    createLeave (evt) {
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        vm.isLoading = true
        Employee.leave(this.employee.uuid, [this.leave])
          .then(response => {
            vm.isLoading = false
            vm.$refs.employeeLeave.hide()
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>
