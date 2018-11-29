<template>
  <b-modal 
    id="orgUnitMove"
    ref="orgUnitMove"
    size="lg" 
    :title="$t('workflows.organisation.move_unit')"
    @hidden="resetData"
    hide-footer 
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="moveOrganisationUnit">
      <div class="form-row">
        <div class="col">
          <mo-organisation-unit-picker
            v-model="original" 
            :label="$t('input_fields.select_unit')"
            :date="move.data.validity.from"
            required
          />
        </div>

        <div class="form-group col">
          <label>{{$t('input_fields.current_super_unit')}}</label>
          <input 
            type="text" 
            class="form-control" 
            :value="parentUnit"
            disabled
          >
        </div>
      </div>

      <mo-organisation-unit-picker
        class="parentUnit"
        v-model="move.data.parent" 
        :label="$t('input_fields.select_new_super_unit')"
        :date="move.data.validity.from"
        required
      />
      
      <div class="form-row">
        <mo-date-picker
          class="moveDate"
          :label="$t('input_fields.move_date')"
          v-model="move.data.validity.from"
          required
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
   * A organisation unit move component.
   */

  import OrganisationUnit from '@/api/OrganisationUnit'
  import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
  import MoDatePicker from '@/components/atoms/MoDatePicker'
  import ButtonSubmit from '@/components/ButtonSubmit'
  import ValidateForm from '@/mixins/ValidateForm'
  import ModalBase from '@/mixins/ModalBase'
  import '@/filters/GetProperty'

  export default {
    mixins: [ValidateForm, ModalBase],

    components: {
      MoOrganisationUnitPicker,
      MoDatePicker,
      ButtonSubmit
    },

    data () {
      return {
        /**
         * The move, parentUnit, uuid, original, isLoading, backendValidationError component value.
         * Used to detect changes and restore the value.
         */
        parentUnit: '',
        original: null,
        move: {
          type: 'org_unit',
          data: {
            uuid: '',
            validity: {}
          }
        },
        isLoading: false,
        backendValidationError: null
      }
    },

    watch: {
      /**
       * If original exist show its parent.
       */
      original: {
        handler (newVal) {
          if (this.original) {
            this.move.data.uuid = newVal.uuid
            return this.getCurrentUnit(newVal.uuid)
          }
        },
        deep: true
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
       * Move a organisation unit and check if the data fields are valid.
       * Then throw a error if not.
       */
      moveOrganisationUnit (evt) {
        evt.preventDefault()
        if (this.formValid) {
          let vm = this
          vm.isLoading = true

          OrganisationUnit.move(this.move)
            .then(response => {
              vm.isLoading = false
              if (response.error) {
                vm.backendValidationError = response.error_key
              } else {
                vm.$refs.orgUnitMove.hide()
              }
            })
        } else {
          this.$validator.validateAll()
        }
      },

      /**
       * Get current organisation unit.
       */
      getCurrentUnit (unitUuid) {
        let vm = this
        if (!unitUuid) return
        OrganisationUnit.get(unitUuid)
          .then(response => {
            vm.parentUnit = response.parent ? response.parent.name : ''
          })
      }
    }
  }
</script>
