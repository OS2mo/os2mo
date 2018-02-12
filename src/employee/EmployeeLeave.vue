<template>
  <b-modal 
    id="employeeLeave" 
    size="lg" 
    hide-footer 
    title="Meld orlov"
    ref="employeeLeave"
  >
      <h3>Orlov</h3>
      <div class="form-row">
        <date-picker-start-end v-model="leave.validity"/>

        <div class="form-group col">
          <leave-picker :org="org" v-model="leave.leave_type"/>
        </div>        
      </div>

    <div class="float-right">
      <button-submit 
      :disabled="errors.any() || !isCompleted"
      @click.native="createLeave"/>
    </div>
  </b-modal>

</template>

<script>
import Employee from '../api/Employee'
import DatePickerStartEnd from '../components/DatePickerStartEnd'
import LeavePicker from '../components/LeavePicker'
import ButtonSubmit from '../components/ButtonSubmit'

export default {
  components: {
    DatePickerStartEnd,
    LeavePicker,
    ButtonSubmit
  },
  computed: {
    isCompleted () {
      return this.leave.validity && this.leave.leave_type
    }
  },
  props: {
    org: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      leave: {
        type: 'leave'
      }
    }
  },
  methods: {
    createLeave () {
      let vm = this
      let create = []

      create.push(this.leave)

      Employee.createEmployee(this.$route.params.uuid, create)
      .then(response => {
        vm.$refs.employeeLeave.hide()
        console.log(response)
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>