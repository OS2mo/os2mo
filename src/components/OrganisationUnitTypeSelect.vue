<template>
  <div class="form-group col">
    <label for="exampleFormControlSelect1">Enhedstype</label>
    <select class="form-control" id="" v-model="type" @change="updateUnitType()">
      <option 
        disabled 
        value=""
      >
      Vælg enhedstype
      </option>
      <option 
        v-for="unitType in orgUnitTypes" 
        :key="unitType.uuid"
        :value="unitType"
      >
        {{unitType.name}}
      </option>
    </select>
  </div>
</template>

<script>
  import Facet from '../api/Facet'

  export default {
    name: 'OrganisationUnitTypeSelect',
    props: {
      value: {
        default: {},
        type: Object
      },
      label: {
        default: 'Angiv overenhed',
        type: String
      },
      orgUuid: String
    },
    data () {
      return {
        type: String,
        orgUnitTypes: []
      }
    },
    watch: {
      orgUuid () {
        this.getOrgUnitTypes()
      }
    },
    methods: {
      getOrgUnitTypes: function () {
        let vm = this
        Facet.organisationUnitTypes(this.orgUuid)
        .then(response => {
          vm.orgUnitTypes = response
        })
      },
      updateUnitType () {
        this.$emit('input', this.type)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>