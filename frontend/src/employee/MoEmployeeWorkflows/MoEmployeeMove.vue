<template>
  <b-modal 
    id="employeeMove" 
    size="lg" 
    :title="$t('workflows.employee.move_engagement')"
    ref="employeeMove"
    hide-footer 
    lazy
    no-close-on-backdrop
    @hidden="$store.dispatch('employeeMove/resetFields')"
  >
    <form @submit.stop.prevent="moveEmployee">
      <mo-employee-picker 
        class="search-employee" 
        v-model="person" 
        required
      />

      <div class="form-row">
        <mo-engagement-picker 
          class="mt-3" 
          v-model="original" 
          :employee="person"
          required
        />
      </div>

      <div class="form-row">
        <mo-organisation-unit-picker
          :label="$t('input_fields.move_to')" 
          class="col" 
          v-model="org_unit"
          required
        />       
      </div>

      <div class="form-row">
        <mo-date-picker 
          class="col from-date"
          :label="$t('input_fields.move_date')" 
          v-model="from"
          :valid-dates="validDates"
          required
        />
      </div>

      <mo-confirm-checkbox
        :entry-date="from"
        :entry-name="original.engagement_type.name"
        :entry-org-name="original.org_unit.name"
        v-if="dateConflict" 
        required
      />

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
   * A employee move component.
   */

  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import MoEngagementPicker from '@/components/MoPicker/MoEngagementPicker'
  import MoEmployeePicker from '@/components/MoPicker/MoEmployeePicker'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import MoConfirmCheckbox from '@/components/MoConfirmCheckbox'
  import ValidateForm from '@/mixins/ValidateForm'
  import ModalBase from '@/mixins/ModalBase'
  import { mapFields } from 'vuex-map-fields'

  export default {
    mixins: [ValidateForm, ModalBase],

    components: {
      MoDatePicker,
      MoOrganisationUnitPicker,
      MoEngagementPicker,
      MoEmployeePicker,
      ButtonSubmit,
      MoConfirmCheckbox
    },

    props: {
      /**
       * Defines a engagement type name.
       */
      entryName: String,

      /**
       * Defines a from date.
       */
      entryDate: Date,

      /**
       * Defines a orgName.
       */
      entryOrgName: String
    },

    data () {
      return {
      /**
        * The isLoading component value.
        * Used to detect changes and restore the value.
        */
        isLoading: false
      }
    },

    computed: {
      /**
       * Get mapFields from vuex store.
       */
      ...mapFields('employeeMove', [
        'move',
        'move.data.person',
        'move.data.org_unit',
        'move.data.validity.from',
        'original',
        'backendValidationError'
      ]),

      /**
       * Check if the dates are valid.
       */
      dateConflict () {
        if (this.from && this.original) {
          if (this.original.validity.to == null) return true
          const newFrom = new Date(this.from)
          const originalTo = new Date(this.original.validity.to)
          if (newFrom <= originalTo) return true
        }
        return false
      },

      /**
       * Check if the organisation date are valid.
       */
      validDates () {
        return this.move.data.org_unit ? this.move.data.org_unit.validity : {}
      }
    },

    methods: {
      /**
       * Move a employee and check if the data fields are valid.
       * Then throw a error if not.
       */
      moveEmployee (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          vm.isLoading = true

          this.$store.dispatch('employeeMove/MOVE_EMPLOYEE')
            .then(response => {
              vm.isLoading = false
              if (response.error) {
                vm.backendValidationError = response.error_key
              } else {
                vm.$refs.employeeMove.hide()
              }
            })
        } else {
          this.$validator.validateAll()
        }
      }
    }
  }
</script>
