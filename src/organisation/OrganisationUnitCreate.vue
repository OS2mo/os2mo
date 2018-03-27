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
    />

    <div class="float-right">
      <button-submit
      :is-disabled="!formValid"
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
  import MoOrganisationUnitEntry from './MoOrganisationUnit/MoOrganisationUnitEntry'

  export default {
    $_veeValidate: {
      validator: 'new'
    },
    name: 'OrganisationUnitCreate',
    components: {
      ButtonSubmit,
      MoOrganisationUnitEntry
    },
    data () {
      return {
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
      formValid () {
        // loop over all contents of the fields object and check if they exist and valid.
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      }
    },
    created () {
      this.org = Organisation.getSelectedOrganisation()
    },
    mounted () {
      EventBus.$on('organisation-changed', newOrg => {
        this.org = newOrg
      })
      this.$root.$on('bv::modal::hidden', resetData => {
        Object.assign(this.$data, this.$options.data())
      })
    },
    methods: {
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
