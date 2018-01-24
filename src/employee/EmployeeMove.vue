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
        selectedDate: null
      }
    },
    created: function () {},
    methods: {
      moveEmployee () {
        let vm = this
        let edit = {
          type: 'engagement',
          uuid: this.$route.params.uuid,
          data: {
            valid_from: this.selectedDate,
            org_unit_uuid: this.orgUnit.uuid
          }
        }
        Employee.moveEmployee(this.$route.params.uuid, edit)
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