<template>
  <b-modal 
    id="employeeCreate" 
    size="lg" 
    hide-footer 
    title="Ny medarbejder"
    ref="employeeCreate"
  >
  
    <div>
      <h4>Engagement</h4>
      <date-start-end v-model="dateStartEnd"/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="orgUnit"/>
        <engagement-title v-model="engagement.job_title_uuid"/>
        <engagement-type v-model="engagement.engagement_type_uuid"/>

      </div>
      
      <div class="form-row">
        <div class="form-check col">
          <label class="form-check-label">
            <input class="form-check-input" type="checkbox" value=""> Overføre
          </label>
        </div>
      </div>
    </div>

    <div class="float-right">
      <button-submit @click.native="createEmployee"/>
    </div>
  </b-modal>

</template>

<script>
  import Employee from '../api/Employee'
  import DateStartEnd from '../components/DatePickerStartEnd'
  import AddressSearch from '../components/AddressSearch'
  import ContactChannel from '../components/ContactChannelInput'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import UnitTypeSelect from '../components/OrganisationUnitTypeSelect'
  import EngagementTitle from '../components/EngagementTitle'
  import EngagementType from '../components/EngagementType'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      DateStartEnd,
      AddressSearch,
      ContactChannel,
      OrganisationUnitPicker,
      UnitTypeSelect,
      EngagementTitle,
      EngagementType,
      ButtonSubmit
    },
    data () {
      return {
        dateStartEnd: {},
        orgUnit: {},
        engagement: {
        },
        jobTitle: '',
        engagementType: ''
      }
    },
    created: function () {},
    methods: {
      createEmployee () {
        this.engagement.type = 'engagement'
        this.engagement.org_uuid = this.orgUnit.org
        this.engagement.org_unit_uuid = this.orgUnit.uuid
        this.engagement.valid_from = this.dateStartEnd.startDate
        this.engagement.valid_to = this.dateStartEnd.endDate

        let vm = this
        Employee.createEmployee(this.$route.params.uuid, [this.engagement])
        .then(response => {
          vm.$refs.employeeCreate.hide()
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>