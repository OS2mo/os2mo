<template>
  <div>
    <mo-loader v-show="isLoading"/>
    <ul v-show="!isLoading">
      <mo-tree-view-item
        v-for="item in children"
        :key="item.uuid"
        v-model="selectedOrgUnit"
        :item="item"
        @show-children="getOrgUnitChildren($event)"
        unfold
      />
    </ul>
  </div>
</template>

<script>
  import { EventBus } from '@/EventBus'
  import Organisation from '@/api/Organisation'
  import OrganisationUnit from '@/api/OrganisationUnit'
  import MoTreeViewItem from './MoTreeViewItem'
  import MoLoader from '@/components/atoms/MoLoader'

  export default {
    components: {
      MoTreeViewItem,
      MoLoader
    },

    props: {
      value: Object,
      orgUuid: String
    },

    data () {
      return {
        children: [],
        selectedOrgUnit: {},
        isLoading: false
      }
    },

    watch: {
      orgUuid () {
        this.getRootChildren()
      },

      atDate () {
        this.getRootChildren()
      },

      selectedOrgUnit: {
        handler (val) {
          this.$emit('input', val)
        },
        deep: true
      }
    },

    mounted () {
      this.getRootChildren()

      EventBus.$on('update-tree-view', () => {
        this.getRootChildren()
      })
    },

    methods: {
      /**
       * Get organisation children.
       */
      getRootChildren () {
        if (this.orgUuid === undefined) return
        let vm = this
        vm.isLoading = true
        Organisation.getChildren(this.orgUuid, this.atDate)
          .then(response => {
            vm.isLoading = false
            vm.children = response
          })
      },

      getOrgUnitChildren (event) {
        // let vm = this
        // vm.loading = true
        // vm.model.children = []
        OrganisationUnit.getChildren(event.uuid, this.atDate)
          .then(response => {
            console.log(response)
            // vm.loading = false
            // vm.model.children = response
          })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}
</style>
