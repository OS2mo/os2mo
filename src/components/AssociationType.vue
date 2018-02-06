<template>
  <div class="form-group col">
    <label>Tilknytningstype</label>
    <select 
      class="form-control col" 
      v-model="type"
      placeholder="Vælg enhed"
      @change="updateAssociationTypes()"
    >
      <option disabled>Tilknytningstype</option>
      <option 
        v-for="atype in associationTypes" 
        v-bind:key="atype.uuid"
        :value="atype"
      >
        {{atype.name}}
      </option>
    </select>
  </div>
</template>

<script>
  import Facet from '../api/Facet'

  export default {
    name: 'AssociationType',
    props: {
      value: Object,
      orgUuid: String
    },
    data () {
      return {
        type: String,
        associationTypes: []
      }
    },
    watch: {
      orgUuid () {
        this.getassociationTypes()
      }
    },
    methods: {
      getassociationTypes () {
        let vm = this
        Facet.associationTypes(this.orgUuid)
        .then(response => {
          vm.associationTypes = response
        })
      },

      updateAssociationTypes () {
        this.$emit('input', this.type)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>