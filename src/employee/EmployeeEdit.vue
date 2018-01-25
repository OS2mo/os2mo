<template>
  <b-modal 
    id="employeeEdit" 
    size="lg" 
    hide-footer 
    title="Rediger Medarbejder"
    ref="employeeEdit"
  >
    <div>
      <h4>Engagement</h4>
      <date-start-end v-model="dateStartEnd" :preselected="dates.startDate"/>
      <div class="form-row"  
       
      >
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="orgUnit"/>
        <engagement-title 
          v-model="engagement.selectedTitle"
          
        />
        {{employeeEngagement['job-title']}}
        {{engagement.job_title_uuid}}
        <engagement-type v-model="engagement.engagement_type_uuid"/>
      </div>
    </div>
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
        engagement: {
          job_title_uuid: ''
        },
        jobTitle: '',
        engagementType: '',
        employeeEngagement: {}
      }
    },
    created () {
      this.getEngagements()
    },
    methods: {
      getEngagements () {
        var vm = this
        Employee.getEngagementDetails(this.$route.params.uuid)
        .then(response => {
          vm.employeeEngagement = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style> 