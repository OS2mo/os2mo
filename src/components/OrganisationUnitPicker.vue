<template>
  <div class="form-group">
    <label for="">{{ label }}</label>
    <input 
      name="unit"
      type="text" 
      class="form-control" 
      placeholder="Vælg enhed"
      ref="orgUnitPicker"
      :value="selectedSuperUnit.name"
      @click.stop="show"
      @focus="getSelectedOrganisation()"
      v-validate="{ required: true }" 
    >
    <span v-show="errors.has('unit')" class="text-danger">{{ errors.first('unit') }}</span>
    <div 
      class="mo-input-group" 
      v-show="showTree" 
      v-click-outside="hide"
    >
      <tree-view 
        v-model="selectedSuperUnit" 
        v-click-outside="hide"
        :orgUuid="org.uuid" 
      />
    </div>
  </div>
</template>

<script>
  import Organisation from '../api/Organisation'
  import OrganisationUnit from '../api/OrganisationUnit'
  import ClickOutside from '../directives/ClickOutside'
  import TreeView from '../components/Treeview'

  export default {
    components: {
      TreeView
    },
    props: {
      value: Object,
      label: {
        default: 'Angiv overenhed',
        type: String
      },
      preselected: {
        type: Object,
        default: null
      }
    },
    data () {
      return {
        org: {},
        selectedSuperUnit: {},
        showTree: false
      }
    },
    directives: {
      ClickOutside
    },
    watch: {
      selectedSuperUnit (newVal, oldVal) {
        this.$refs.orgUnitPicker.blur()

        this.$emit('input', newVal)
        this.hide()
      },
      preselected (newVal, oldVal) {
        this.selectedSuperUnit = newVal
      }
    },
    methods: {
      getSelectedOrganisation () {
        this.org = Organisation.getSelectedOrganisation()
      },

      getSelectedOrganistionUnit () {
        this.orgUnit = OrganisationUnit.getSelectedOrganistionUnit()
      },

      show () {
        this.showTree = true
      },

      hide () {
        this.showTree = false
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .form-group {
    position: relative;
  }
  .mo-input-group {
    z-index: 999;
    background-color: #fff;
    width: 100%;
    padding: 0.375rem 0.75rem;
    position: absolute;
    border: 1px solid #ced4da;
    border-radius: 0 0 0.25rem;
    transition: border-color ease-in-out 0.15s, box-shadow ease-in-out 0.15s;
  }
</style>