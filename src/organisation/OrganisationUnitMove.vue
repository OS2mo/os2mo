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
      v-model="move.data.validity.from"
      />
    </div>

    <div class="form-row">
      <div class="col">
        <organisation-unit-picker 
          v-model="move.original"
          label="Fremsøg enhed"
        />
      </div>

      <div class="form-group col">
        <label for="">Nuværende overenhed</label>
        <input 
          type="text" 
          class="form-control" 
          :value="currentUnit" 
          disabled
        >
      </div>
    </div>

    <organisation-unit-picker 
      v-model="move.data.parent"
      label="Angiv ny overenhed"
    />

    <div class="float-right">
      <button-submit 
      :disabled="errors.any() || isDisabled"
      :on-click-action="moveOrganisationUnit"
      />
    </div> 
  </b-modal>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
  import DatePicker from '../components/DatePicker'
  import ButtonSubmit from '../components/ButtonSubmit'
  import '../filters/GetProperty'

  export default {
    components: {
      OrganisationUnitPicker,
      DatePicker,
      ButtonSubmit
    },
    computed: {
      isDisabled () {
        if (this.move.data.validity.from === null || this.move.original === undefined || this.move.data.parent === undefined) return true
      }
    },
    data () {
      return {
        currentUnit: '',
        move: {
          data: {
            validity: {}
          }
        }
      }
    },
    watch: {
      move: {
        handler (newVal) {
          if (!newVal) return
          this.getCurrentUnit(newVal.original.uuid | this.Getproperty)
        }
      },
      deep: true
    },
    methods: {
      moveOrganisationUnit () {
        let vm = this
        vm.isLoading = true

        OrganisationUnit.edit(this.move.original.uuid, this.move)
        .then(response => {
          vm.$refs.orgUnitMove.hide()
        })
        .catch(err => {
          console.log(err)
          vm.isLoading = false
        })
      },

      getCurrentUnit (unitUuid) {
        let vm = this
        if (!unitUuid) return
        OrganisationUnit.get(unitUuid)
        .then(response => {
          console.log(response)
          vm.currentUnit = response.parent.name
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>