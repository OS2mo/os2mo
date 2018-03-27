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
  import MoOrganisationUnitEntry from './MoOrganisationUnit/MoOrganisationUnitEntry'

  export default {
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
      this.$root.$on('bv::modal::hidden', resetData => {
        Object.assign(this.$data, this.$options.data())
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
