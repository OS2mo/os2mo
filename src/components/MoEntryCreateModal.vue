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
      title="Opret"
      :ref="nameId"
      lazy
    >
    <form @submit.stop.prevent="create">
      <component :is="entryComponent" v-model="entry"/>

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
  import ButtonSubmit from '@/components/ButtonSubmit'

  export default {
    $_veeValidate: {
      validator: 'new'
    },

    components: {
      ButtonSubmit
    },

    props: {
      uuid: String,
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
        isLoading: false,
        backendValidationError: null
      }
    },

    computed: {
      nameId () {
        return 'moCreate' + this._uid
      },
  
      formValid () {
        // loop over all contents of the fields object and check if they exist and valid.
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      },

      hasEntryComponent () {
        return this.entryComponent !== undefined
      }
    },

    mounted () {
      this.$root.$on('bv::modal::hidden', () => {
        Object.assign(this.$data, this.$options.data())
      })
    },

    beforeDestroy () {
      this.$root.$off(['bv::modal::hidden'])
    },

    methods: {
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

      createEmployee (data) {
        let vm = this
        Employee.create(this.uuid, [data])
          .then(response => {
            vm.isLoading = false
            if (response.error) {
              vm.backendValidationError = response.error_key
            } else {
              vm.$refs[this.nameId].hide()
            }
          })
      },

      createOrganisationUnit (data) {
        let vm = this
        return OrganisationUnit.createEntry(this.uuid, data)
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
