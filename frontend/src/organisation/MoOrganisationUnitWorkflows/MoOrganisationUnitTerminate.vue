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
          :label="$t('input_fields.select_unit')"
          class="col"
          v-model="org_unit"
          required
        />

        <mo-input-date
          class="from-date"
          :label="$t('input_fields.end_date')"
          :valid-dates="validDates"
          v-model="terminate.validity.to"
          required
        />
      </div>

      <div class="mb-3" v-if="org_unit">
        <p>{{$t('workflows.organisation.messages.following_will_be_terminated')}}</p>
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
import { MoInputDate } from '@/components/MoInput'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import ButtonSubmit from '@/components/ButtonSubmit'
import MoOrganisationDetailTabs from '@/organisation/OrganisationDetailTabs'
import ValidateForm from '@/mixins/ValidateForm'
import ModalBase from '@/mixins/ModalBase'

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    MoInputDate,
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
