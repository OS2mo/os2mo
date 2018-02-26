<template>
  <b-modal 
    id="orgUnitRename"
    ref="orgUnitRename"  
    size="lg" 
    hide-footer 
    title="Omdøb enhed">
    <div class="form-row">
      <organisation-unit-picker 
        label="Enhed" 
        class="col"
        v-model="rename.original"
        :preselected="preselectedUnit"
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
      :disabled="errors.any() || !isCompleted"
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
    components: {
      DatePickerStartEnd,
      OrganisationUnitPicker,
      ButtonSubmit
    },
    data () {
      return {
        orgUnit: {},
        preselectedUnit: {},
        rename: {
          data: {
            name: '',
            validity: {}
          }
        }
      }
    },
    computed: {
      isDisabled () {
        if (this.rename.data.validity.from === undefined || this.rename.original === undefined || this.rename.data.name === '') return true
      }
    },
    mounted () {
      EventBus.$on('organisation-unit-changed', selectedUnit => {
        this.preselectedUnit = selectedUnit
      })
    },
    methods: {
      renameOrganisationUnit () {
        let vm = this
        vm.isLoading = true

        OrganisationUnit.edit(this.rename.original.uuid, this.rename)
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

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>