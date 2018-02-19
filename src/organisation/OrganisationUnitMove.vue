<template>
  <b-modal 
    id="orgUnitMove"
    ref="orgUnitMove"
    size="lg" 
    hide-footer 
    title="Flyt enhed">
    <div class="form-row">
      <date-picker 
      label="Dato for flytning"
      v-model="date"
      />
    </div>

    <div class="form-row">
      <div class="col">
        <organisation-unit-picker 
          v-model="unit"
          label="Fremsøg enhed"
          :preselected="unit"
        />
      </div>

      <div class="form-group col">
        <label for="">Nuværende overenhed</label>
        <input 
          type="text" 
          class="form-control" 
          id="" 
          :value="currentSuperUnit.name" 
          disabled
        >
      </div>
    </div>

    <organisation-unit-picker 
      v-model="newSuperUnit"
      label="Angiv ny overenhed"
    />

    <div class="float-right">
      <button-submit 
      :disabled="errors.any() || !isCompleted"
      :on-click-action="moveUnit"
      />
    </div> 
  </b-modal>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import DatePicker from '../components/DatePicker'
  import ButtonSubmit from '../components/ButtonSubmit'
  import { EventBus } from '../EventBus'

  export default {
    components: {
      OrganisationUnitPicker,
      DatePicker,
      ButtonSubmit
    },
    data () {
      return {
        unit: {},
        date: null,
        newSuperUnit: {},
        currentSuperUnit: {}
      }
    },
    computed: {
      isCompleted () {
        return this.date && this.unit && this.newSuperUnit
      }
    },
    watch: {
      unit (newVal, oldVal) {
        this.getCurrentSuperUnit(newVal.parent)
      }
    },
    mounted () {
      EventBus.$on('organisation-unit-changed', selectedUnit => {
        this.unit = selectedUnit
      })
    },
    methods: {
      moveUnit () {
        let vm = this
        OrganisationUnit.move(vm.unit, vm.newSuperUnit.uuid, vm.date)
        .then(response => {
          vm.$refs.orgUnitMove.hide()
        })
      },

      getCurrentSuperUnit (unitUuid) {
        let vm = this
        if (!unitUuid) return
        OrganisationUnit.get(unitUuid)
        .then(response => {
          console.log(response)
          vm.currentSuperUnit = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>