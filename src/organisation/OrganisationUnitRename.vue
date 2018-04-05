<template>
  <b-modal 
    id="orgUnitRename"
    ref="orgUnitRename"  
    size="lg" 
    hide-footer 
    title="Omdøb enhed"
    lazy
  >
    <div class="form-row">
      <organisation-unit-picker 
        label="Enhed" 
        class="col"
        v-model="original"
        :preselected="preselectedUnit"
        required
      />
    </div>

    <div class="form-row">
      <div class="form-group col">
        <label for="exampleFormControlInput1">Nyt navn</label>
        <input 
          name="name"
          type="text"
          class="form-control"
          v-model="rename.data.name"
          v-validate="{required: true}"
        >
      </div>
    </div>

    <div class="form-row">
      <date-picker-start-end 
        class="col"
        v-model="rename.data.validity"
      />
    </div>

    <div class="float-right">
      <button-submit 
      :is-disabled="!formValid"
      :is-loading="isLoading"
      :on-click-action="renameOrganisationUnit"
      />
    </div>
  </b-modal>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import { EventBus } from '../EventBus'
  import DatePickerStartEnd from '../components/DatePickerStartEnd'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import ButtonSubmit from '../components/ButtonSubmit'
  
  export default {
    $_veeValidate: {
      validator: 'new'
    },
    components: {
      DatePickerStartEnd,
      OrganisationUnitPicker,
      ButtonSubmit
    },
    data () {
      return {
        orgUnit: {},
        preselectedUnit: {},
        original: {},
        rename: {
          data: {
            name: '',
            validity: {}
          }
        },
        isLoading: false
      }
    },
    computed: {
      formValid () {
        // loop over all contents of the fields object and check if they exist and valid.
        return Object.keys(this.fields).every(field => {
          return this.fields[field] && this.fields[field].valid
        })
      }
    },
    mounted () {
      EventBus.$on('organisation-unit-changed', selectedUnit => {
        this.preselectedUnit = selectedUnit
      })
      this.$root.$on('bv::modal::hidden', resetData => {
        Object.assign(this.$data, this.$options.data())
      })
    },
    methods: {
      renameOrganisationUnit () {
        let vm = this
        vm.isLoading = true

        OrganisationUnit.rename(this.original.uuid, this.rename)
          .then(response => {
            vm.$refs.orgUnitRename.hide()
          })
          .catch(err => {
            console.log(err)
            vm.isLoading = false
          })
      }
    }
  }
</script>
