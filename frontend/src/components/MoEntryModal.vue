<template>
  <div v-if="hasEntryComponent">
    <button
      class="btn btn-outline-primary"
      v-b-modal="idLabel"
    >
      <icon :name="iconLabel" />
      <span v-if="action === 'CREATE'">{{$t('buttons.create_new')}}</span>
    </button>

    <b-modal
      :id="idLabel"
      size="lg"
      hide-footer
      :title="modalTitle"
      :ref="idLabel"
      lazy
    >
    <form @submit.stop.prevent="onClickAction">
      <component
        :is="entryComponent"
        v-model="entry"
        :disable-org-unit-picker="disableOrgUnitPicker"
      />

      <div class="float-right">
        <button-submit :is-loading="isLoading" :is-disabled="!formValid"/>
      </div>
    </form>
    </b-modal>
  </div>
</template>

<script>
/**
 * A entry modal component.
 */

import Employee from '@/api/Employee'
import OrganisationUnit from '@/api/OrganisationUnit'
import ButtonSubmit from './ButtonSubmit'

export default {
  /**
   * Requesting a new validator scope to its children.
   */
  $_veeValidate: {
    validator: 'new'
  },

  components: {
    ButtonSubmit
  },

  props: {
    /**
     * Defines a uuid.
     */
    uuid: String,

    /**
     * Defines a label.
     */
    label: String,

    /**
     * Defines the content.
     */
    content: Object,

    /**
     * Defines the contentType.
     */
    contentType: String,

    /**
     * Defines the entryComponent.
     */
    entryComponent: Object,

    /**
     * Defines a required action - employee or organisation unit.
     */
    action: {
      type: String,
      required: true,
      validator (value) {
        if (value === 'EDIT' || value === 'CREATE') return true
        console.warn('Action must be either EDIT or CREATE')
        return false
      }
    },

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
       * The entry, original, org, isLoading component value.
       * Used to detect changes and restore the value.
       */
      entry: {},
      original: {},
      org: {},
      isLoading: false
    }
  },

  computed: {
    /**
     * Get idLabel `moCreate`.
     */
    idLabel () {
      return 'moCreate' + this._uid
    },

    /**
     * Loop over all contents of the fields object and check if they exist and valid.
     */
    formValid () {
      return Object.keys(this.fields).every(field => {
        return this.fields[field] && this.fields[field].valid
      })
    },

    /**
     * Get disableOrgUnitPicker type.
     */
    disableOrgUnitPicker () {
      return this.type === 'ORG_UNIT' && this.action === 'EDIT'
    },

    /**
     * Switch between create and edit iconLabel.
     */
    iconLabel () {
      switch (this.action) {
        case 'CREATE':
          return 'plus'
        case 'EDIT':
          return 'edit'
        default:
          return ''
      }
    },

    /**
     * Switch between create and edit modalTitle.
     */
    modalTitle () {
      switch (this.action) {
        case 'CREATE':
          return 'Opret'
        case 'EDIT':
          return 'Rediger'
        default:
          return ''
      }
    },

    /**
     * If it has a entry component.
     */
    hasEntryComponent () {
      return this.entryComponent !== undefined
    }
  },

  watch: {
    /**
     * Whenever content change, update newVal.
     */
    content: {
      handler (newVal) {
        this.handleContent(newVal)
      },
      deep: true
    }
  },

  mounted () {
    /**
     * Whenever content change preselected value.
     */
    this.org = this.$store.state.organisation

    if (this.content) {
      this.handleContent(this.content)
    }

    if (this.action === 'CREATE') {
      this.$root.$on('bv::modal::hidden', () => {
        Object.assign(this.$data, this.$options.data())
      })
    }

    this.$root.$on('bv::modal::shown', data => {
      if (this.content) {
        this.handleContent(this.content)
      }
    })
  },

  beforeDestroy () {
    /**
     * Called right before a instance is destroyed.
     */
    this.$root.$off(['bv::modal::hidden'])
    this.$root.$off(['bv::modal::shown'])
  },

  methods: {
    /**
     * Handle the entry and original content.
     */
    handleContent (content) {
      this.entry = JSON.parse(JSON.stringify(content))
      this.original = JSON.parse(JSON.stringify(content))
    },

    /**
     * Switch between create and edit on click action.
     */
    onClickAction () {
      switch (this.action) {
        case 'CREATE':
          this.create()
          break
        case 'EDIT':
          this.edit()
          break
      }
    },

    /**
     * Switch between employee and organisation create entry.
     */
    create () {
      this.isLoading = true

      switch (this.type) {
        case 'EMPLOYEE':
          this.createEmployee(this.entry)
          break
        case 'ORG_UNIT':
          this.entry.type = 'address'
          this.createOrganisationUnit([this.entry])
          break
      }
    },

    /**
     * Switch between employee and organisation edit.
     */
    edit () {
      this.isLoading = true

      let data = {
        type: this.contentType,
        uuid: this.entry.uuid,
        original: this.original,
        data: this.entry
      }

      switch (this.type) {
        case 'EMPLOYEE':
          data.person = { uuid: this.uuid }
          this.editEmployee(data)
          break
        case 'ORG_UNIT':
          data.org_unit = { uuid: this.uuid }
          this.editOrganisationUnit(data)
          break
      }
    },

    /**
     * Create a employee.
     */
    createEmployee (data) {
      return Employee.create([data]).then(this.handle.bind(this))
    },

    /**
     * Edit a employee.
     */
    editEmployee (data) {
      return Employee.edit([data]).then(this.handle.bind(this))
    },

    /**
     * Create organisation unit entry.
     */
    createOrganisationUnit (data) {
      return OrganisationUnit.createEntry(data).then(this.handle.bind(this))
    },

    /**
     * Edit organisation unit entry.
     */
    editOrganisationUnit (data) {
      return OrganisationUnit.edit([data]).then(this.handle.bind(this))
    },

    handle (response) {
      this.isLoading = false

      if (response.error) {
        let messages = this.$i18n.messages[this.$i18n.locale]

        this.backendValidationMessage =
            messages.alerts.error[response.error_key]

        if (!this.backendValidationMessage) {
          this.backendValidationMessage = this.$t('alerts.fallback',
            response)
        }
      } else {
        this.$refs['moCreate' + this._uid].hide()
      }
    }
  }
}
</script>
