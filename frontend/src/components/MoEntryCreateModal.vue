<template>
  <div v-if="hasEntryComponent">
    <button
      class="btn btn-outline-primary"
      v-b-modal="nameId"
    >
      <icon name="plus" />
      {{$t('buttons.create_new')}}
    </button>

    <b-modal
      :id="nameId"
      size="lg"
      hide-footer
      :title="$t('common.create')"
      :ref="nameId"
      lazy
    >
    <form @submit.stop.prevent="create">
      <component
        :is="entryComponent"
        v-model="entry"
        :hide-org-picker="hideOrgPicker"
        :hide-employee-picker="hideEmployeePicker"
      />

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError)}}
      </div>

      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
      </div>
    </form>
    </b-modal>
  </div>
</template>

<script>
/**
 * A entry create modal component.
 */

import Employee from '@/api/Employee'
import OrganisationUnit from '@/api/OrganisationUnit'
import ButtonSubmit from '@/components/ButtonSubmit'
import ValidateForm from '@/mixins/ValidateForm'
import ModalBase from '@/mixins/ModalBase'
import bModalDirective from 'bootstrap-vue/es/directives/modal/modal'

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    ButtonSubmit
  },
  directives: {
    'b-modal': bModalDirective
  },

  props: {
    /**
     * Defines a uuid.
     */
    uuid: String,

    /**
     * Defines a entryComponent.
     */
    entryComponent: Object,

    /**
     * Defines a required type - employee or organisation unit.
     */
    type: {
      type: String,
      required: true,
      validator (value) {
        if (value === 'EMPLOYEE' || value === 'ORG_UNIT') return true
        console.warn('Action must be either EMPLOYEE or ORG_UNIT')
        return false
      }
    }
  },

  data () {
    return {
      /**
       * The entry, isLoading, backendValidationError component value.
       * Used to detect changes and restore the value.
       */
      entry: {},
      isLoading: false,
      backendValidationError: null
    }
  },

  computed: {
    /**
     * Get name `moCreate`.
     */
    nameId () {
      return 'moCreate' + this._uid
    },

    /**
     * If it has a entry component.
     */
    hasEntryComponent () {
      return this.entryComponent !== undefined
    },

    /**
     * Get hideOrgPicker type.
     */
    hideOrgPicker () {
      return this.type === 'ORG_UNIT'
    },

    /**
     * Get hideEmployeePicker type.
     */
    hideEmployeePicker () {
      return this.type === 'EMPLOYEE'
    }
  },

  mounted () {
    /**
     * Whenever it changes, reset data.
     */
    this.$root.$on('bv::modal::hidden', () => {
      Object.assign(this.$data, this.$options.data())
    })
  },

  beforeDestroy () {
    /**
     * Called right before a instance is destroyed.
     */
    this.$root.$off(['bv::modal::hidden'])
  },

  methods: {
    /**
     * Create a employee or organisation entry.
     */
    create () {
      if (!this.formValid) {
        this.$validator.validateAll()
        return
      }

      this.isLoading = true

      this.entry.org = this.$store.getters['organisation/GET_ORGANISATION']

      switch (this.type) {
        case 'EMPLOYEE':
          this.entry.person = { uuid: this.uuid }
          this.createEmployee(this.entry)
          break
        case 'ORG_UNIT':
          this.entry.org_unit = { uuid: this.uuid }
          this.createOrganisationUnit(this.entry)
          break
      }
    },

    /**
     * Create a employee and check if the data fields are valid.
     * Then throw a error if not.
     */
    createEmployee (data) {
      let vm = this
      Employee.create([data])
        .then(response => {
          vm.isLoading = false
          if (response.error) {
            vm.backendValidationError = response.error_key
          } else {
            vm.$refs[this.nameId].hide()
          }
        })
    },

    /**
     * Create a organisation unit and check if the data fields are valid.
     * Then throw a error if not.
     */
    createOrganisationUnit (data) {
      let vm = this
      return OrganisationUnit.createEntry(data)
        .then(response => {
          vm.isLoading = false
          if (response.error) {
            vm.backendValidationError = response.error_key
          } else {
            vm.$refs[this.nameId].hide()
          }
        })
    }
  }
}
</script>
