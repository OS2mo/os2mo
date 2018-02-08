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
        <date-picker 
          label="Orlov start"
        />
        <date-picker 
          label="Orlov slut"
        />

        <div class="form-group col">
          <label>Orlovstype</label>
          <select class="form-control col" id="" >
            <option>Orlovstype</option>
          </select>
        </div>        
      </div>

    <div class="float-right">
      <button-submit/>
    </div>
  </b-modal>

</template>

<script>
import Organisation from '../api/Organisation'
import Employee from '../api/Employee'
import { EventBus } from '../EventBus'
import DatePicker from '../components/DatePicker'
import ButtonSubmit from '../components/ButtonSubmit'

export default {
  components: {
    DatePicker,
    ButtonSubmit
  },
  data () {
    return {
      leave: {
        type: 'leave'
      },
      org: {}
    }
  },
  created () {
    this.org = Organisation.getSelectedOrganisation()
  },
  mounted () {
    EventBus.$on('organisation-changed', newOrg => {
      this.org = newOrg
    })
  },
  methods: {
    createEmployee () {
      let vm = this
      let create = []

      create.push(this.leave)

      Employee.createEmployee(this.$route.params.uuid, create)
      .then(response => {
        vm.$refs.employeeCreate.hide()
        console.log(response)
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>