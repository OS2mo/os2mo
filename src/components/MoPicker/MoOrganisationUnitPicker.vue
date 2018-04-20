<template>
  <div class="form-group">
    <label for="">{{ label }}</label>
    <input 
      :name="nameId"
      data-vv-as="Enhed" 
      ref="orgUnitPicker"
      type="text" 
      class="form-control" 
      placeholder="Vælg enhed"
      v-model="orgName"
      @click.stop="toggleTree()"
      :disabled="isDisabled"
      v-validate="{required: !isDisabled}"
    >
    <div 
      class="mo-input-group" 
      v-show="showTree"
    >
      <mo-tree-view 
        v-model="selectedSuperUnit"
        :org-uuid="orgUuid" 
      />
    </div>
    <span v-show="errors.has(nameId)" class="text-danger">{{ errors.first(nameId) }}</span>
  </div>
</template>

<script>
  import OrganisationUnit from '@/api/OrganisationUnit'
  import MoTreeView from '@/components/MoTreeView/MoTreeView'
  import { mapGetters } from 'vuex'

  export default {
    name: 'MoOrganisationUnitPicker',
    components: {
      MoTreeView
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
        selectedSuperUnit: {},
        showTree: false,
        orgName: ''
      }
    },
    computed: {
      ...mapGetters({
        orgUuid: 'organisation/getUuid'
      }),

      nameId () {
        return 'org-unit-' + this._uid
      }
    },
    watch: {
      selectedSuperUnit (newVal) {
        this.orgName = newVal.name
        this.$validator.validate(this.nameId)
        this.$refs.orgUnitPicker.blur()

        this.$emit('input', newVal)
        this.showTree = false
      }
    },
    mounted () {
      this.selectedSuperUnit = this.value || this.selectedSuperUnit
    },
    methods: {
      getSelectedOrganistionUnit () {
        this.orgUnit = OrganisationUnit.getSelectedOrganistionUnit()
      },

      toggleTree () {
        this.showTree = !this.showTree
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