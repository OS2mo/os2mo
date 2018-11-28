<template>
  <div>
    <mo-loader v-show="isLoading"/>
    <ul v-show="!isLoading">
      <mo-tree-view-item
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
/**
   * A tree view component.
   */

import { EventBus } from '@/EventBus'
import Organisation from '@/api/Organisation'
import MoTreeViewItem from './MoTreeViewItem'
import MoLoader from '@/components/atoms/MoLoader'

export default {
  components: {
    MoTreeViewItem,
    MoLoader
  },

  props: {
    /**
       * Create two-way data bindings with the component.
       */
    value: Object,

    /**
       * Defines a orgUuid.
       */
    orgUuid: String,

    /**
       * This boolean property defines a able link.
       */
    linkable: Boolean,

    /**
       * Defines a atDate.
       */
    atDate: [Date, String]
  },

  data () {
    return {
      /**
       * The children, selectedOrgUnit, isLoading component value.
       * Used to detect changes and restore the value.
       */
      children: [],
      selectedOrgUnit: {},
      isLoading: false
    }
  },

  watch: {
    /**
       * When orgUnit change, get children.
       */
    orgUuid () {
      this.getChildren()
    },

    /**
       * When atDate change, get children.
       */
    atDate () {
      this.getChildren()
    },

    /**
       * Whenever selectedOrgUnit change, update val.
       */
    selectedOrgUnit (val) {
      this.$emit('input', val)
    }
  },

  mounted () {
    /**
       * Whenever tree view change, update children.
       */
    this.getChildren()

    EventBus.$on('update-tree-view', () => {
      this.getChildren()
    })
  },

  methods: {
    /**
       * Get organisation children.
       */
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
