<template>
  <b-modal 
    id="orgUnitCreate" 
    size="lg" 
    hide-footer 
    title="Opret enhed"
    ref="orgUnitCreate"
  >
    <date-picker-start-end v-model="dateStartEnd"/>

    <div class="form-row">
      <div class="form-group col">
        <label for="">Navn</label>
        <input 
          name="name"
          data-vv-as="Navn"
          v-model="orgUnit.name" 
          type="text" 
          class="form-control" 
          v-validate="{ required: true }" 
        >
        <span v-show="errors.has('name')" class="text-danger">{{ errors.first('name') }}</span>
      </div>

      <organisation-unit-type-picker 
        v-model="orgUnit.type" 
        :orgUuid="org.uuid"
      />
    </div>

    <organisation-unit-picker v-model="superUnit"/>

    <address-search 
      :org="org"
      v-model="orgUnit.locations[0]"
    />
    
    <component 
      v-for="(channel, key) in channels" 
      v-bind:is="channel" 
      v-bind:key="key" 
      v-model="contactChannels[key]"
      :orgUuid="org.uuid"
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
        <button-submit
        :disabled="errors.any() || !isCompleted" 
        @click.native="createOrganisationUnit"
        />
      </div>
  </b-modal>

</template>

<script>
  import Organisation from '../api/Organisation'
  import OrganisationUnit from '../api/OrganisationUnit'
  import { EventBus } from '../EventBus'
  import DatePicker from '../components/DatePicker'
  import DatePickerStartEnd from '../components/DatePickerStartEnd'
  import ButtonSubmit from '../components/ButtonSubmit'
  import AddressSearch from '../components/AddressSearch'
  import ContactChannel from '../components/ContactChannelInput'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import OrganisationUnitTypePicker from '../components/OrganisationUnitTypePicker'

  export default {
    name: 'OrganisationUnitCreate',
    components: {
      DatePicker,
      DatePickerStartEnd,
      ButtonSubmit,
      AddressSearch,
      ContactChannel,
      OrganisationUnitPicker,
      OrganisationUnitTypePicker
    },
    data () {
      return {
        channels: ['ContactChannel'],
        contactChannels: [],
        dateStartEnd: {},
        superUnit: {},
        org: {},
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
    computed: {
      isCompleted () {
        return this.dateStartEnd.from && this.orgUnit.name && this.superUnit
      }
    },
    updated () {
      this.orgUnit['valid-from'] = this.dateStartEnd.from
      this.orgUnit['valid-to'] = this.dateStartEnd.to !== '' ? this.dateStartEnd.to : 'infinity'
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
      addContactChannel () {
        this.channels.push('ContactChannel')
      },

      createOrganisationUnit () {
        this.orgUnit.org = this.superUnit.org
        this.orgUnit.parent = this.superUnit.uuid
        this.orgUnit['user-key'] = 'NULL'
        this.orgUnit.locations[0].primaer = true
        this.orgUnit.locations[0]['contact-channels'] = this.contactChannels

        let vm = this
        OrganisationUnit.create(this.orgUnit)
        .then(response => {
          vm.$refs.orgUnitCreate.hide()
          console.log(response)
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>