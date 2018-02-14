<template>
  <div class="form-group col">
    <label v-if="!noLabel">{{label}}</label>
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
  import Organisation from '../api/Organisation'
  import { EventBus } from '../EventBus'

  export default {
    name: 'AssociationType',
    props: {
      value: Object,
      noLabel: Boolean
    },
    data () {
      return {
        label: 'Tilknytningstype',
        type: {},
        associationTypes: []
      }
    },
    mounted () {
      EventBus.$on('organisation-changed', () => {
        this.getassociationTypes()
      })
    },
    created () {
      this.getassociationTypes()
      this.type = this.value
    },
    methods: {
      getassociationTypes () {
        let vm = this
        let org = Organisation.getSelectedOrganisation()
        if (org.uuid === undefined) return
        Facet.associationTypes(org.uuid)
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