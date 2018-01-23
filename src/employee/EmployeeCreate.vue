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
        <engagement-title v-model="engagement.jobtitle"/>
        <engagement-type v-model="engagement.type"/>
      </div>
      
      <div class="form-row">
        <div class="form-check col">
          <label class="form-check-label">
            <input class="form-check-input" type="checkbox" value=""> Overføre
          </label>
        </div>
      </div>
    </div>

    <!-- <div>
      <h4>Tilknytning</h4>
      <date-start-end/>

      <div class="form-row">
        <organisation-unit-picker class="col"/>

        <div class="form-group col">
          <label>Stillingsbetegnelse</label>
          <select class="form-control col" id="" >
            <option>Stillingsbetegnelse</option>
          </select>
        </div>

        <div class="form-group col">
          <label>Fysisk placering</label>
          <select class="form-control col" id="" disabled>
            <option>Fysisk placering</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group col">
          <label>Tilknytningstype</label>
          <select class="form-control col" id="" >
            <option>Tilknytningstype</option>
          </select>
        </div>
        <div class="form-group col">
          <label>Relateret engagement</label>
          <select class="form-control col" id="" >
            <option>Relateret engagement</option>
          </select>
        </div>
      </div>
    </div> -->

    <!-- <div>
      <h4>IT</h4>
      <date-start-end/>

      <div class="form-row">
        <div class="form-group col">
          <label>IT system</label>
          <select class="form-control col" id="" >
            <option>IT system</option>
          </select>
        </div>
      </div>
    </div> -->

    <!-- <div>
      <h4>Kontakt</h4>
      <date-start-end/>

      <contact-channel/>     
    </div> -->

    <!-- <div>
      <h4>Leder</h4>
      <date-start-end/>

      <div class="form-row">
        <organisation-unit-picker class="col"/>

        <div class="form-group col">
          <label>Stillingsbetegnelse</label>
          <select class="form-control col" id="" >
            <option>Stillingsbetegnelse</option>
          </select>
        </div>

        <div class="form-group col">
          <label>Lederfunktion</label>
          <select class="form-control col" id="">
            <option>Lederfunktion</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group col">
          <label>Lederniveau</label>
          <select class="form-control col" id="" >
            <option>Lederniveau</option>
          </select>
        </div>

        <div class="form-group col">
          <label>Lederansvar</label>
          <select class="form-control col" id="" >
            <option>Lederansvar</option>
          </select>
        </div>

        <div class="form-group col">
          <label>Tilknyttet adresse</label>
          <select class="form-control col" id="" disabled>
            <option>Tilknyttet adresse</option>
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group col">
          <label>Relateret engagement</label>
          <select class="form-control col" id="" >
            <option>Relateret engagement</option>
          </select>
        </div>
      </div>
    </div> -->

    <div class="float-right">
      <button-submit @click.native="createEngagement()"/>
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
        orgUnit: {},
        dateStartEnd: {},
        engagement: {
          validfrom: '',
          validto: '',
          orgunit: '',
          org: '',
          type: '',
          jobtitle: ''
        }
      }
    },
    created: function () {},
    methods: {
      createNewEmployee () {
      },

      createEngagement () {
        this.engagement.orgunit = this.orgUnit.uuid
        this.engagement.org = this.orgUnit.org
        this.engagement.validfrom = this.dateStartEnd.startDate
        this.engagement.validto = this.dateStartEnd.endDate

        let uuid = '1f67e646-0306-43c1-aba7-86af8c1c6b14'

        Employee.createEngagement(uuid, this.engagement)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>