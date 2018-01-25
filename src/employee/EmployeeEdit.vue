<template>
  <b-modal 
    id="employeeEdit" 
    size="lg" 
    hide-footer 
    title="Rediger Medarbejder"
    ref="employeeEdit"
  >
  <date-start-end v-model="dateStartEnd" :preselected="dates.startDate"/>

    <div class="float-right">
      <button-submit @click.native="editEmployee"/>
    </div>
  </b-modal>

</template>

<script>
  import Employee from '../api/Employee'
  import DateStartEnd from '../components/DatePickerStartEnd'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import UnitTypeSelect from '../components/OrganisationUnitTypeSelect'
  import EngagementTitle from '../components/EngagementTitle'
  import EngagementType from '../components/EngagementType'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      DateStartEnd,
      OrganisationUnitPicker,
      UnitTypeSelect,
      EngagementTitle,
      EngagementType,
      ButtonSubmit
    },
    data () {
      return {
        orgUnit: {},
        dateStartEnd: {},
        dates: {
          startDate: '2018-08-02T12:13:00+00:00',
          startEnd: '2018-09-12T12:13:00+00:00'
        },
        engagement: {},
        jobTitle: '',
        engagementType: ''
      }
    },
    created: function () {
    },
    methods: {
      getEngagementDetails: function (uuid) {
        var vm = this
        Employee.getEngagementDetails(uuid)
        .then(response => {
          vm.engagement = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style> 