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
      action: {
        type: String,
        required: true,
        validator (value) {
          if (value === 'EDIT' || value === 'CREATE') return true
          console.warn('Action must be either EDIT or CREATE')
          return false
        }
      },
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
        org: {},
        isLoading: false
      }
    },
    computed: {
      idLabel () {
        return 'moCreate' + this._uid
      },
      formValid () {
        // loop over all contents of the fields object and check if they exist and valid.
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      },
      disableOrgUnitPicker () {
        return this.type === 'ORG_UNIT' && this.action === 'EDIT'
      },

      iconLabel () {
        switch (this.action) {
          case 'CREATE':
            return 'plus'
          case 'EDIT':
            return 'edit'
        }
      },

      modalTitle () {
        switch (this.action) {
          case 'CREATE':
            return 'Opret'
          case 'EDIT':
            return 'Rediger'
        }
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
      this.$root.$off(['bv::modal::hidden'])
      this.$root.$off(['bv::modal::shown'])
    },
    methods: {
      handleContent (content) {
        this.entry = JSON.parse(JSON.stringify(content))
        this.original = JSON.parse(JSON.stringify(content))
      },

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

      createEmployee (data) {
        let vm = this
        Employee.create(this.uuid, [data])
          .then(response => {
            vm.isLoading = false
            vm.$refs['moCreate' + vm._uid].hide()
          })
      },

      editEmployee (data) {
        let vm = this
        return Employee.edit(this.uuid, [data])
          .then(response => {
            vm.isLoading = false
            vm.$refs['moCreate' + vm._uid].hide()
          })
      },

      createOrganisationUnit (data) {
        let vm = this
        return OrganisationUnit.createEntry(this.uuid, data)
          .then(response => {
            vm.isLoading = false
            vm.$refs['moCreate' + vm._uid].hide()
          })
      },

      editOrganisationUnit (data) {
        let vm = this
        return OrganisationUnit.edit(this.uuid, data)
          .then(response => {
            vm.isLoading = false
            vm.$refs['moCreate' + vm._uid].hide()
          })
      }
    }
  }
</script>
