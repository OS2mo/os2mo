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
      <date-start-end v-model="engagement.dateStartEnd"/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="engagement.orgUnit"/>
        <engagement-title v-model="engagement.job_function"/>
        <engagement-type v-model="engagement.type"/>
      </div>
      <div class="form-row">
        <div class="form-check col">
          <label class="form-check-label">
            <input class="form-check-input" type="checkbox" value=""> Overføre
          </label>
        </div>
      </div>
{{engagement}}
      <h4>Tilknytning</h4>
      <date-start-end v-model="association.dateStartEnd"/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="association.orgUnit"/>
        <engagement-title v-model="association.job_function"/>
        <address-search 
        :orgUuid="org.uuid"/>
      </div>
      {{association}}
    </div>

    <div class="float-right">
      <button-submit @click.native="createEmployee"/>
    </div>
  </b-modal>

</template>

<script>
  import Organisation from '../api/Organisation'
  import Employee from '../api/Employee'
  import DateStartEnd from '../components/DatePickerStartEnd'
  import AddressSearch from '../components/AddressSearch'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import UnitTypeSelect from '../components/OrganisationUnitTypeSelect'
  import EngagementTitle from '../components/EngagementTitle'
  import EngagementType from '../components/EngagementType'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      DateStartEnd,
      AddressSearch,
      OrganisationUnitPicker,
      UnitTypeSelect,
      EngagementTitle,
      EngagementType,
      ButtonSubmit
    },
    data () {
      return {
        engagement: {},
        association: {},
        org: {},
        test: {}
      }
    },
    created () {
      this.org = Organisation.getSelectedOrganisation()
    },
    methods: {
      createEmployee () {
        let vm = this
        let create = [
          this.engagement = {
            type: 'engagement',
            org_unit: {
              uuid: this.engagement.orgUnit.org
            },
            org: {
              uuid: this.engagement.orgUnit.uuid
            },
            job_function: {
              uuid: this.engagement.job_function
            },
            engagement_type: {
              uuid: this.engagement.type
            },
            valid_from: this.engagement.dateStartEnd.startDate,
            valid_to: this.engagement.dateStartEnd.endDate
          },

          this.association = {
            type: 'association',
            org_unit: {
              uuid: this.association.orgUnit.org
            },
            org: {
              uuid: this.association.orgUnit.uuid
            },
            job_function: {
              uuid: this.association.job_function
            },
            association_type: {
              uuid: this.association.type
            },
            location: {
              uuid: '5e0d7420-e06b-4832-b843-c4ad6955f5ec'
            },
            valid_from: this.association.dateStartEnd.startDate,
            valid_to: this.association.dateStartEnd.endDate
          }
        ]

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