<template>
  <b-modal 
    id="employeeLeave" 
    size="lg" 
    hide-footer 
    title="Meld orlov"
    ref="employeeLeave"
    lazy
  >
    <employee-picker v-model="employee"/>
    <mo-leave-entry v-model="leave" :org="org" @is-valid="isValid"/>

    <div class="float-right">
      <button-submit 
      :is-disabled="isDisabled"
      :is-loading="isLoading"
      :on-click-action="createLeave"/>
    </div>
  </b-modal>

</template>

<script>
import Employee from '../../api/Employee'
import EmployeePicker from '../../components/EmployeePicker'
import MoLeaveEntry from '../MoLeave/MoLeaveEntry'
import ButtonSubmit from '../../components/ButtonSubmit'

export default {
  components: {
    EmployeePicker,
    MoLeaveEntry,
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
      isLoading: false,
      leaveValid: false,
      employee: {},
      leave: {
        validity: {}
      }
    }
  },
  computed: {
    isDisabled () {
      return !this.leaveValid || !this.employee.uuid
    }
  },
  methods: {
    isValid (val) {
      this.leaveValid = val
    },

    createLeave () {
      let vm = this
      vm.isLoading = true
      Employee.leave(this.employee.uuid, [this.leave])
      .then(response => {
        vm.isLoading = false
        vm.$refs.employeeLeave.hide()
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>