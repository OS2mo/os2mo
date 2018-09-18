<template>
  <b-modal 
    id="orgUnitTerminate"
    ref="orgUnitTerminate"  
    size="lg" 
    :title="$t('workflows.organisation.terminate_unit')"
    @hidden="resetData"
    hide-footer 
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="endOrganisationUnit">
      <div class="form-row">
        <mo-organisation-unit-picker 
          :label="$tc('input_fields.unit', 1)" 
          class="col" 
          v-model="org_unit"
          required
        />

        <mo-date-picker
          :label="$t('input_fields.end_date')"
          :valid-dates="validDates"
          v-model="terminate.validity.to"
          required
        />
      </div>

      <div class="mb-3" v-if="org_unit">
        <p>Følgende vil blive afsluttet for enheden:</p>
        <mo-organisation-detail-tabs 
          :uuid="org_unit.uuid" 
          timemachine-friendly
        />
      </div>

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError)}}
      </div>

      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
      </div>
    </form>
  </b-modal>
</template>

<script>
  /**
   * A organisation unit terminate component.
   */

  import OrganisationUnit from '@/api/OrganisationUnit'
  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import MoOrganisationDetailTabs from '@/organisation/OrganisationDetailTabs'

  export default {
      /**
       * Requesting a new validator scope to its children.
       */
    $_veeValidate: {
      validator: 'new'
    },

    components: {
      MoDatePicker,
      MoOrganisationUnitPicker,
      ButtonSubmit,
      MoOrganisationDetailTabs
    },

    data () {
      return {
        /**
         * The terminate, org_unit, isLoading, backendValidationError component value.
         * Used to detect changes and restore the value.
         */
        org_unit: null,
        terminate: {
          validity: {}
        },
        isLoading: false,
        backendValidationError: null
      }
    },

    computed: {
      /**
       * Check if the organisation date are valid.
       */
      validDates () {
        return this.org_unit ? this.org_unit.validity : {}
      },

      /**
       * Loop over all contents of the fields object and check if they exist and valid.
       */
      formValid () {
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      }
    },

    methods: {
      /**
       * Resets the data fields.
       */
      resetData () {
        Object.assign(this.$data, this.$options.data())
      },

      /**
       * Terminate a organisation unit and check if the data fields are valid.
       * Then throw a error if not.
       */
      endOrganisationUnit (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          vm.isLoading = true
          OrganisationUnit.terminate(this.org_unit.uuid, this.terminate)
            .then(response => {
              vm.isLoading = false
              if (response.error) {
                vm.backendValidationError = response.error_key
              } else {
                vm.$refs.orgUnitTerminate.hide()
              }
            })
        } else {
          this.$validator.validateAll()
        }
      }
    }
  }
</script>
