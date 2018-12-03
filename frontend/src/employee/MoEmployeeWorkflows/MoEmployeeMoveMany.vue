<template>
  <b-modal
    id="employeeMoveMany"
    size="lg"
    :title="$t('workflows.employee.move_many_engagements')"
    ref="employeeMoveMany"
    hide-footer
    lazy
    no-close-on-backdrop
    @hidden="$store.dispatch(`employeeMoveMany/resetFields`)"
  >
    <form @submit.stop.prevent="moveMany">
      <div class="form-row">
        <mo-date-picker
          class="col"
          :label="$t('input_fields.move_date')"
          v-model="moveDate"
          required
        />

        <mo-organisation-unit-picker
          :is-disabled="dateSelected"
          :label="$t('input_fields.move_from')"
          v-model="orgUnitSource"
          class="col from-unit"
          required
        />

        <mo-organisation-unit-picker
          :is-disabled="dateSelected"
          :label="$t('input_fields.move_to')"
          v-model="orgUnitDestination"
          class="col to-unit"
          required
        />
      </div>

      <mo-table
        v-model="selected"
        v-if="orgUnitSource"
        :content="employees"
        :columns="columns"
        type="EMPLOYEE"
        multi-select
      />

      <input
        type="hidden"
        v-if="orgUnitSource"
        name="selected-employees-count"
        :value="selected.length"
        v-validate="{min_value: 1, required: true}"
      >

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
 * A employee move many component.
 */

import MoDatePicker from '@/components/atoms/MoDatePicker'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoTable from '@/components/MoTable/MoTable'
import ButtonSubmit from '@/components/ButtonSubmit'
import ValidateForm from '@/mixins/ValidateForm'
import ModalBase from '@/mixins/ModalBase'
import { mapFields } from 'vuex-map-fields'
import { mapGetters } from 'vuex'

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    MoDatePicker,
    MoOrganisationUnitPicker,
    MoTable,
    ButtonSubmit
  },

  data () {
    return {
      orgUnitSource: undefined
    }
  },

  computed: {
    /**
     * generate getter/setters from store
     */
    ...mapFields('employeeMoveMany', [
      'selected',
      'moveDate',
      'orgUnitDestination',
      'columns',
      'backendValidationError',
      'isLoading'
    ]),

    ...mapGetters('employeeMoveMany', [
      'employees'
    ]),

    /**
     * Set dateSelected to disable if moveDate is selected.
     */
    dateSelected () {
      return !this.moveDate
    }
  },

  watch: {
    /**
     * Whenever orgUnitSource changes, get employees.
     * @todo this could probably be improved. right now we need to reset orgUnitSource in the moveMany response.
     */
    orgUnitSource: {
      handler (newVal) {
        this.$store.commit(`employeeMoveMany/updateOrgUnitSource`, newVal)
        this.$store.dispatch(`employeeMoveMany/getEmployees`)
      },
      deep: true
    },

    selected (val) {
      if (this.fields['selected-employees-count']) {
        this.$validator.validate('selected-employees-count', val.length)
      }
    }
  },

  methods: {
    /**
     * Check if fields are valid, and move employees if they are.
     * Otherwise validate the fields.
     */
    moveMany () {
      let vm = this
      if (this.formValid) {
        this.$store.dispatch(`employeeMoveMany/moveManyEmployees`)
          .then(() => {
            vm.orgUnitSource = undefined
            vm.$refs.employeeMoveMany.hide()
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>
