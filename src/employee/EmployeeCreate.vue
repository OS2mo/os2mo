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
          v-model="engagement.org_unit"/>
        <engagement-title 
          :org-uuid="org.uuid" 
          v-model="engagement.job_function"
        />
        <engagement-type 
          :org-uuid="org.uuid" 
          v-model="engagement.engagement_type"
        />
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
          v-model="association.org_unit"/>
        <engagement-title 
          :org-uuid="org.uuid" 
          v-model="association.job_function"
        />
        <association-type 
          :org-uuid="org.uuid" 
          v-model="association.association_type"
        />
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
import { EventBus } from '../EventBus'
import DateStartEnd from '../components/DatePickerStartEnd'
import AddressSearch from '../components/AddressSearch'
import AssociationType from '../components/AssociationType'
import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
import UnitTypeSelect from '../components/OrganisationUnitTypeSelect'
import EngagementTitle from '../components/EngagementTitle'
import EngagementType from '../components/EngagementType'
import ButtonSubmit from '../components/ButtonSubmit'

export default {
  components: {
    DateStartEnd,
    AddressSearch,
    AssociationType,
    OrganisationUnitPicker,
    UnitTypeSelect,
    EngagementTitle,
    EngagementType,
    ButtonSubmit
  },
  data () {
    return {
      engagement: {
        type: 'engagement'
      },
      association: {
        type: 'association'
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

      this.engagement.valid_from = this.engagement.dateStartEnd.startDate
      this.engagement.valid_to = this.engagement.dateStartEnd.endDate

      this.association.valid_from = this.association.dateStartEnd.startDate
      this.association.valid_to = this.association.dateStartEnd.endDate

      create.push(this.engagement)
      create.push(this.association)

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