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
  import Property from '../api/Property'

  export default {
    components: {},
    props: {
      value: {
        default: {},
        type: Object
      },
      label: {
        default: 'Angiv overenhed',
        type: String
      }
    },
    data () {
      return {
        type: String,
        orgUnitTypes: []
      }
    },
    created: function () {
      this.getOrgUnitTypes()
    },
    methods: {
      getOrgUnitTypes: function () {
        var vm = this
        Property.getOrganisationUnitTypes().then(function (response) {
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