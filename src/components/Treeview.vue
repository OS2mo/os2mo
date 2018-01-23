<template>
  <div>
    <ul>
      <tree-item
      v-for="c in children"
      v-bind:key="c.uuid"
      v-model="selectedOrgUnit"
      :model="c"
      :linkable="linkable"
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
      linkable: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        children: null,
        selectedOrgUnit: {}
      }
    },
    watch: {
      orgUuid (newVal, oldVal) {
        this.children = null
        this.getTree(newVal)
      },

      selectedOrgUnit (newVal, oldVal) {
        this.$emit('input', newVal)
      }
    },
    created () {
      this.getTree(this.orgUuid)
    },
    methods: {
      getTree (uuid) {
        var vm = this
        if (!uuid) {
          vm.children = {}
          return
        }
        Organisation.getChildren(uuid)
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
