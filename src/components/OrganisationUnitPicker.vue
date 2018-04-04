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
      v-validate="{ required: true }" 
      :disabled="isDisabled"
    >
    <span v-show="errors.has('unit')" class="text-danger">{{ errors.first('unit') }}</span>
    <div 
      class="mo-input-group" 
      v-show="showTree"
    >
      <tree-view 
        v-model="selectedSuperUnit"
        :org-uuid="orgUuid" 
      />
    </div>
  </div>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import TreeView from '../components/Treeview'
  import { mapGetters } from 'vuex'

  export default {
    components: {
      TreeView
    },
    inject: {
      $validator: '$validator'
    },
    props: {
      value: Object,
      label: {
        default: 'Angiv overenhed',
        type: String
      },
      isDisabled: Boolean
    },
    data () {
      return {
        selectedSuperUnit: {
          name: ''
        },
        showTree: false
      }
    },
    computed: {
      ...mapGetters({
        orgUuid: 'organisation/getUuid'
      })
    },
    watch: {
      selectedSuperUnit (newVal) {
        this.$refs.orgUnitPicker.blur()

        this.$emit('input', newVal)
        this.hide()
      }
    },
    mounted () {
      this.selectedSuperUnit = this.value || this.selectedSuperUnit
    },
    methods: {
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