<template>
  <div>
    <button 
      class="btn btn-outline-primary" 
      v-b-modal="'moCreate'+_uid" 
      @click="showModal=true"
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
    >
      <mo-association-entry 
        v-if="showModal" 
        v-model="entry" 
        :org="org" 
        @is-valid="isValid"
      />

      <div class="float-right">
        <button-submit 
          :on-click-action="action" 
          :is-loading="isLoading" 
          :is-disabled="isDisabled"
        />
      </div>
    </b-modal>
  </div>
</template>

<script>
  import Organisation from '../../api/Organisation'
  import Employee from '../../api/Employee'
  import MoAssociationEntry from './MoAssociationEntry'
  import ButtonSubmit from '../../components/ButtonSubmit'

  export default {
    components: {
      MoAssociationEntry,
      ButtonSubmit
    },
    props: {
      uuid: String,
      label: String,
      content: Object,
      type: {
        type: String,
        required: true,
        validator (value) {
          if (value === 'EDIT' || value === 'CREATE') return true
          console.warn('Type must be either EDIT or CREATE')
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
        showModal: false,
        valid: false
      }
    },
    computed: {
      isDisabled () {
        return !this.valid
      },

      iconLabel () {
        switch (this.type) {
          case 'CREATE':
            return 'plus'
          case 'EDIT':
            return 'edit'
        }
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

      action () {
        switch (this.type) {
          case 'CREATE':
            this.create()
            break
          case 'EDIT':
            this.edit()
            break
        }
      },

      create () {
        let vm = this
        vm.isLoading = true

        Employee.create(this.uuid, [this.entry])
        .then(response => {
          vm.isLoading = false
          vm.$refs['moCreate' + vm._uid].hide()
        })
      },

      edit () {
        let vm = this
        vm.isLoading = true

        let data = [{
          type: 'engagement',
          uuid: this.entry.uuid,
          original: this.original,
          data: this.entry
        }]

        Employee.edit(this.uuid, data)
        .then(response => {
          vm.isLoading = false
          vm.$refs['moCreate' + vm._uid].hide()
        })
      }
    }
  }
</script>
