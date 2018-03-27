<template>
  <div v-if="hasEntryComponent">
    <button 
      class="btn btn-outline-primary" 
      v-b-modal="idLabel" 
    >
      <icon :name="iconLabel" />
      {{label}}
    </button>

    <b-modal
      :id="idLabel"
      size="lg"
      hide-footer 
      :title="modalTitle"
      :ref="idLabel"
      lazy
    >
      <component 
        :is="entryComponent"
        v-model="entry" 
        :org="org" 
        :disable-org-unit-picker="disableOrgUnitPicker"
      />
      <div class="float-right">
        <button-submit 
          :on-click-action="onClickAction" 
          :is-loading="isLoading" 
          :is-disabled="!formValid"
        />
      </div>
    </b-modal>
  </div>
</template>

<script>
  import Organisation from '../api/Organisation'
  import Employee from '../api/Employee'
  import ButtonSubmit from './ButtonSubmit'
  import OrganisationUnit from '../api/OrganisationUnit'

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
          this.entry = JSON.parse(JSON.stringify(newVal))
        },
        deep: true
      }
    },
    mounted () {
      if (this.action === 'CREATE') {
        this.$root.$on('bv::modal::hidden', resetData => {
          Object.assign(this.$data, this.$options.data())
        })
      }

      this.$root.$on('bv::modal::shown', data => {
        if (this.content) {
          this.entry = JSON.parse(JSON.stringify(this.content))
          this.original = JSON.parse(JSON.stringify(this.content))
        }
      })
    },
    created () {
      this.org = Organisation.getSelectedOrganisation()

      if (this.content) {
        this.entry = JSON.parse(JSON.stringify(this.content))
        this.original = JSON.parse(JSON.stringify(this.content))
      }
    },
    beforeDestroy () {
      this.$root.$off(['bv::modal::hidden'])
      this.$root.$off(['bv::modal::shown'])
    },
    methods: {
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
            this.createOrganisationUnit(this.entry)
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
        return OrganisationUnit.create(data)
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
