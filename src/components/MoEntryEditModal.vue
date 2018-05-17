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
  import Employee from '@/api/Employee'
  import OrganisationUnit from '@/api/OrganisationUnit'
  import ButtonSubmit from './ButtonSubmit'

  export default {
    $_veeValidate: {
      validator: 'new'
    },
    components: {
      ButtonSubmit
    },
    props: {
      uuid: String,
      label: String,
      content: Object,
      contentType: String,
      entryComponent: Object,
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
        entry: {},
        original: {},
        isLoading: false,
        backendValidationError: null
      }
    },
    computed: {
      nameId () {
        return 'moEdit' + this._uid
      },
      formValid () {
        // loop over all contents of the fields object and check if they exist and valid.
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      },
      disableOrgUnitPicker () {
        return this.type === 'ORG_UNIT'
      },

      hasEntryComponent () {
        return this.entryComponent !== undefined
      }
    },
    watch: {
      content: {
        handler (newVal) {
          this.handleContent(newVal)
        },
        deep: true
      }
    },
    mounted () {
      this.handleContent(this.content)

      this.$root.$on('bv::modal::shown', data => {
        if (this.content) {
          this.handleContent(this.content)
        }
      })
    },
    beforeDestroy () {
      this.$root.$off(['bv::modal::shown'])
    },
    methods: {
      handleContent (content) {
        this.entry = JSON.parse(JSON.stringify(content))
        this.original = JSON.parse(JSON.stringify(content))
      },

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
