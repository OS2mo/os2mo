<template>
  <div v-if="hasEntryComponent">
    <button 
      class="btn btn-outline-primary" 
      v-b-modal="'moCreate'+_uid" 
    >
      <icon :name="iconLabel" />
      {{label}}
    </button>

    <b-modal
      :id="'moCreate'+_uid"
      size="lg"
      hide-footer 
      title="Opret"
      :ref="'moCreate'+_uid"
      lazy
    >
      <component 
        :is="entryComponent"
        v-model="entry" 
        :org="org" 
        @is-valid="isValid"
      />

      <div class="float-right">
        <button-submit 
          :on-click-action="onClickAction" 
          :is-loading="isLoading" 
          :is-disabled="isDisabled"
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
        org: Object,
        isLoading: false,
        valid: false
      }
    },
    computed: {
      isDisabled () {
        return !this.valid
      },

      iconLabel () {
        switch (this.action) {
          case 'CREATE':
            return 'plus'
          case 'EDIT':
            return 'edit'
        }
      },

      hasEntryComponent () {
        return this.entryComponent !== undefined
      }
    },
    created () {
      this.org = Organisation.getSelectedOrganisation()

      if (this.content) {
        this.entry = JSON.parse(JSON.stringify(this.content))
        this.original = JSON.parse(JSON.stringify(this.content))
      }
    },
    methods: {
      isValid (val) {
        this.valid = val
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
          vm.entry = {}
          vm.$refs['moCreate' + vm._uid].hide()
        })
      },

      editEmployee (data) {
        let vm = this
        return Employee.edit(this.uuid, [data])
        .then(response => {
          vm.isLoading = false
          vm.entry = {}
          vm.$refs['moCreate' + vm._uid].hide()
        })
      },

      createOrganisationUnit (data) {
        let vm = this
        return OrganisationUnit.create(data)
        .then(response => {
          vm.isLoading = false
          vm.entry = {}
          vm.$refs['moCreate' + vm._uid].hide()
        })
      },

      editOrganisationUnit (data) {
        let vm = this
        return OrganisationUnit.edit(this.uuid, data)
        .then(response => {
          vm.isLoading = false
          vm.entry = {}
          vm.$refs['moCreate' + vm._uid].hide()
        })
      }
    }
  }
</script>
