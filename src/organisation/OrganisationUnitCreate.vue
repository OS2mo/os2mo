<template>
  <div>
    <h1>Opret enhed</h1>
    
    <date-picker-start-end v-model="dateStartEnd"/>

    <div class="form-row">
      <div class="form-group col">
        <label for="">Navn</label>
        <input 
          v-model="orgUnit.name" 
          type="text" 
          class="form-control" 
          id="" 
          placeholder="">
      </div>

      <unit-type-select v-model="orgUnit.type"/>
    </div>

    <organisation-unit-picker v-model="superUnit"/>

    <address-search 
    v-model="orgUnit.locations[0]"
    :localUuid="superUnit.org"
    />
    
    <component 
      v-for="(channel, key) in channels" 
      v-bind:is="channel" 
      v-bind:key="key" 
      v-model="contactChannels[key]"
    />

    <button 
      type="button" 
      class="btn btn-primary" 
      v-on:click="addContactChannel()" 
      :disabled="channels.length > contactChannels.length"
    >
      <icon name="plus"/>
    </button>

    <div class="float-right">
      <button type="button" class="btn btn-primary" v-on:click="createOrganisationUnit()">
        <icon name="check"/>
      </button>
    </div>

    <!-- <div class="float-right">
        <button-submit v-on:click="createOrganisationUnit()"/>
      </div> -->
  </div>

</template>

<script>
  import Organisation from '../api/Organisation'
  import DatePicker from '../components/DatePicker'
  import DatePickerStartEnd from '../components/DatePickerStartEnd'
  import ButtonSubmit from '../components/ButtonSubmit'
  import AddressSearch from '../components/AddressSearch'
  import ContactChannel from '../components/ContactChannelInput'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import UnitTypeSelect from '../components/OrganisationUnitTypeSelect'

  export default {
    name: 'OrganisationUnitCreate',
    components: {
      DatePicker,
      DatePickerStartEnd,
      ButtonSubmit,
      AddressSearch,
      ContactChannel,
      OrganisationUnitPicker,
      UnitTypeSelect
    },
    data () {
      return {
        channels: ['ContactChannel'],
        contactChannels: [],
        dateStartEnd: {},
        superUnit: {},
        orgUnit: {
          'valid-to': '',
          'valid-from': '',
          name: '',
          type: {},
          org: '',
          parent: '',
          locations: [{
            location: '',
            name: '',
            'contact-channels': []
          }]
        }
      }
    },
    updated () {
      this.orgUnit['valid-from'] = this.dateStartEnd.startDate
      this.orgUnit['valid-to'] = this.dateStartEnd.endDate !== '' ? this.dateStartEnd.endDate : 'infinity'
    },
    created () {},
    methods: {
      addContactChannel: function () {
        this.channels.push('ContactChannel')
      },
      createOrganisationUnit: function () {
        this.orgUnit.org = this.superUnit.org
        this.orgUnit.parent = this.superUnit.uuid
        this.orgUnit['user-key'] = 'NULL'
        this.orgUnit.locations[0].primaer = true
        this.orgUnit.locations[0]['contact-channels'] = this.contactChannels

        Organisation.createOrganisationUnit(this.orgUnit).then(function (response) {
          console.log(response)
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>