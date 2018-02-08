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
      org: {
        type: Object,
        required: true
      },
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
      org (newOrg) {
        this.getChildren(newOrg)
      },

      atDate () {
        this.getChildren()
      },

      selectedOrgUnit (newVal, oldVal) {
        this.$emit('input', newVal)
      }
    },
    created () {
      this.getChildren(this.org)
    },
    methods: {
      getChildren (org) {
        let vm = this
        if (org.uuid === undefined) return
        Organisation.getChildren(org.uuid, this.atDate)
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
