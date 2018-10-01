<template>
  <div v-if="hasEntryComponent">
    <button 
      class="btn btn-outline-primary" 
      v-b-modal="nameId" 
    >
      <icon name="edit" />
    </button>

    <b-modal
      :id="nameId"
      size="lg"
      hide-footer 
      title="Rediger"
      :ref="nameId"
      lazy
    >
    <form @submit.stop.prevent="edit">
      <component 
        :is="entryComponent"
        v-model="entry" 
        :disable-org-unit-picker="disableOrgUnitPicker"
      />

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError)}}
      </div>

      <div class="float-right">
        <button-submit :is-loading="isLoading" :is-disabled="!formValid"/>
      </div>
    </form>
    </b-modal>
  </div>
</template>

<script>
  /**
   * A entry edit modal component.
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
       * The entry, original, isLoading, backendValidationError component value.
       * Used to detect changes and restore the value.
       */
        entry: {},
        original: {},
        isLoading: false,
        backendValidationError: null
      }
    },

    computed: {
      /**
       * Get name `moEdit`.
       */
      nameId () {
        return 'moEdit' + this._uid
      },

      /**
       * Get disableOrgUnitPicker type.
       */
      disableOrgUnitPicker () {
        return this.type === 'ORG_UNIT'
      },

      /**
       * If it has a entry component.
       */
      hasEntryComponent () {
        return this.entryComponent !== undefined
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
      this.handleContent(this.content)

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
       * Edit a employee or organisation entry.
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
            this.editEmployee(data)
            break
          case 'ORG_UNIT':
            this.editOrganisationUnit(data)
            break
        }
      },

      /**
       * Edit a employee and check if the data fields are valid.
       * Then throw a error if not.
       */
      editEmployee (data) {
        let vm = this
        return Employee.edit(this.uuid, [data])
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
       * Edit a organisation and check if the data fields are valid.
       * Then throw a error if not.
       */
      editOrganisationUnit (data) {
        let vm = this
        return OrganisationUnit.edit(this.uuid, data)
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
