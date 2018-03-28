<template>
  <b-modal 
    id="orgUnitTerminate"
    ref="orgUnitTerminate"  
    size="lg" 
    hide-footer 
    title="Afslut enhed"
    lazy
  >
    <div class="form-row">
      <organisation-unit-picker 
        label="Enhed" 
        class="col"
        v-model="org_unit"
      />
      <date-picker 
        label="Slutdato"
        v-model="terminate.validity.from"
        required
      />
    </div>
    <div class="float-right">
      <button-submit
      :is-disabled="!formValid"
      :is-loading="isLoading"
      :on-click-action="endOrganisationUnit"
      />
    </div>
  </b-modal>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import DatePicker from '../components/DatePicker'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    $_veeValidate: {
      validator: 'new'
    },
    components: {
      DatePicker,
      OrganisationUnitPicker,
      ButtonSubmit
    },
    data () {
      return {
        org_unit: {},
        terminate: {
          validity: {}
        },
        isLoading: false
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
    mounted () {
      this.$root.$on('bv::modal::hidden', resetData => {
        Object.assign(this.$data, this.$options.data())
      })
    },
    methods: {
      endOrganisationUnit () {
        let vm = this
        vm.isLoading = true
        OrganisationUnit.terminate(this.org_unit.uuid, this.terminate)
          .then(response => {
            vm.isLoading = false
            vm.$refs.orgUnitTerminate.hide()
          })
      }
    }
  }
</script>
