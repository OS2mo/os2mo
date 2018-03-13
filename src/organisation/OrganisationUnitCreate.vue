<template>
  <b-modal 
    id="orgUnitCreate" 
    size="lg" 
    hide-footer 
    title="Opret enhed"
    ref="orgUnitCreate"
    lazy
  >
    <mo-organisation-unit-entry
      :org="org" 
      v-model="orgUnit" 
      @is-valid="isOrgUnitValid"
    />

    <!--<address-search 
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
    </button>-->

    <div class="float-right">
        <button-submit
        :is-disabled="isDisabled"
        :on-click-action="createOrganisationUnit"
        />
      </div>
  </b-modal>

</template>

<script>
  import Organisation from '../api/Organisation'
  import OrganisationUnit from '../api/OrganisationUnit'
  import { EventBus } from '../EventBus'
  import ButtonSubmit from '../components/ButtonSubmit'
  import AddressSearch from '../components/AddressSearch'
  import ContactChannel from '../components/ContactChannelInput'
  import MoOrganisationUnitEntry from './MoOrganisationUnit/MoOrganisationUnitEntry'

  export default {
    name: 'OrganisationUnitCreate',
    components: {
      ButtonSubmit,
      AddressSearch,
      ContactChannel,
      MoOrganisationUnitEntry
    },
    data () {
      return {
        channels: ['ContactChannel'],
        contactChannels: [],
        org: {},
        orgUnit: {
          validity: {}
        },
        valid: {
          orgUnit: false
        }
      }
    },
    computed: {
      isDisabled () {
        return !this.valid.orgUnit
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
      isOrgUnitValid (val) {
        this.valid.orgUnit = val
      },

      createOrganisationUnit () {
        let vm = this
        this.isLoading = true

        OrganisationUnit.create(this.orgUnit)
        .then(response => {
          vm.$refs.orgUnitCreate.hide()
          console.log(response)
        })
        .catch(err => {
          console.log(err)
          vm.isLoading = false
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>