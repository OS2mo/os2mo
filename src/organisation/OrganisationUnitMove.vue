<template>
  <div>
    <div class="form-row">
      <date-picker 
      label="Dato for flytning"
      v-model="date"
      />
    </div>

    <div class="form-row">
      <div class="col">
        <organisation-unit-picker 
          label="Fremsøg enhed"
          v-model="unit"
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
      label="Angiv ny overenhed"
      v-model="newSuperUnit"
    />

    <div class="float-right">
      <button-submit @click.native="moveUnit"/>
    </div> 
  </div>
</template>

<script>
  import Organisation from '../api/Organisation'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import DatePicker from '../components/DatePicker'
  import ButtonSubmit from '../components/ButtonSubmit'

  export default {
    components: {
      OrganisationUnitPicker,
      DatePicker,
      ButtonSubmit
    },
    data () {
      return {
        unit: {},
        date: '',
        newSuperUnit: {},
        currentSuperUnit: {}
      }
    },
    watch: {
      unit (newVal, oldVal) {
        console.log(newVal)
        this.getCurrentSuperUnit(newVal.parent)
      }
    },
    created: function () {},
    methods: {
      moveUnit () {
        let vm = this
        Organisation.moveOrganisationUnit(vm.unit, vm.newSuperUnit.uuid, vm.date)
        .then(response => {
          console.log(response)
        })
      },

      getCurrentSuperUnit (unitUuid) {
        let vm = this
        if (unitUuid === null) return
        return Organisation.getUnitDetails(unitUuid)
        .then(response => {
          vm.currentSuperUnit = response[0]
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>