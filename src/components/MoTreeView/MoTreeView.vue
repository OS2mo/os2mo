<template>
  <div>
    <loading v-show="isLoading"/>
    <ul v-show="!isLoading">
      <tree-item
        v-for="(c, index) in children"
        :key="index"
        v-model="selectedOrgUnit"
        :model="c"
        :linkable="linkable"
        :at-date="atDate"
        first-open
      />
    </ul>
  </div>
</template>

<script>
  import Organisation from '@/api/Organisation'
  import TreeItem from './TreeviewItem'
  import Loading from '@/components/Loading'

  export default {
    components: {
      TreeItem,
      Loading
    },
    props: {
      value: Object,
      orgUuid: String,
      linkable: Boolean,
      atDate: [Date, String]
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
        this.getChildren()
      },

      atDate () {
        this.getChildren()
      },

      selectedOrgUnit (val) {
        this.$emit('input', val)
      }
    },
    mounted () {
      this.getChildren()
    },
    methods: {
      getChildren () {
        if (this.orgUuid === undefined) return
        let vm = this
        vm.isLoading = true
        Organisation.getChildren(this.orgUuid, this.atDate)
          .then(response => {
            vm.isLoading = false
            vm.children = response
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
