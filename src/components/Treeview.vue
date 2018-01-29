<template>
  <div>
    <ul>
      <tree-item
      v-for="c in children"
      v-bind:key="c.uuid"
      v-model="selectedOrgUnit"
      :model="c"
      :linkable="linkable"
      :at-date="atDate"
      first-open
      />
    </ul>
    <loading v-show="!children"/>
  </div>
</template>

<script>
  import Organisation from '../api/Organisation'
  import TreeItem from './TreeviewItem'
  import Loading from './Loading'

  export default {
    components: {
      TreeItem,
      Loading
    },
    props: {
      value: Object,
      orgUuid: String,
      linkable: Boolean,
      atDate: Date
    },
    data () {
      return {
        children: null,
        selectedOrgUnit: {}
      }
    },
    watch: {
      orgUuid () {
        this.getChildren()
      },

      atDate () {
        this.getChildren()
      },

      selectedOrgUnit (newVal, oldVal) {
        this.$emit('input', newVal)
      }
    },
    methods: {
      getChildren () {
        if (!this.orgUuid) return

        let vm = this
        Organisation.getChildren(this.orgUuid, this.atDate)
        .then(response => {
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
