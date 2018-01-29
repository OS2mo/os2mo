<template>
  <b-modal 
    id="employeeEdit" 
    size="lg" 
    hide-footer 
    title="Rediger medarbejder"
    ref="employeeEdit"
  >
    <div v-for="e in employeeEngagement" v-bind:key="e.uuid">
      <h4>Engagement</h4>
      {{e['valid-from']}} {{e['valid-to']}}
      <date-start-end v-model="dateStartEnd" :preselected="dates.startDateEnd"/>
      <div class="form-row">
        <organisation-unit-picker 
          id="unit"
          class="col" 
          label="Vælg enhed"
          v-model="orgUnit"
        />
        {{e['org-unit'].name}}
        <engagement-title v-model="engagement.selectedTitle"/>
        {{e['job-title'].name}}
        <engagement-type v-model="engagement.engagement_type_uuid"/>
        {{e['type'].name}}
      </div>
    </div>{{employeeEngagement}}
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
          startDate: '',
          startEnd: ''
        },
        engagement: {
          selectedTitle: '',
          job_title_uuid: ''
        },
        engagementType: '',
        employeeEngagement: {},
        selectedEngagement: null
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
      },

      editEmployee () {
        let vm = this
        let edit = [{
          type: 'engagement',
          uuid: this.selectedEngagement,
          overwrite: {
            valid_from: this.dateStartEnd.startDate,
            valid_to: this.dateStartEnd.endDate,
            job_title_uuid: this.engagement.selectedTitle,
            engagement_type_uuid: this.engagement.engagement_type_uuid,
            org_unit_uuid: this.engagement.orgUnit
          },
          data: {
            valid_from: this.dateStartEnd.startDate,
            valid_to: this.dateStartEnd.endDate,
            org_unit_uuid: this.engagement.orgUnit
          }
        }]
        Employee.editEmployee(this.$route.params.uuid, edit)
        .then(response => {
          vm.$refs.employeeEdit.hide()
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style> 