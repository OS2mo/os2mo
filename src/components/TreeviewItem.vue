<template>
    <li>
      <div class="" :class="{bold: isFolder}">
        <span 
          v-if="model.uuid" 
          @click="selectOrgUnit(model)"
        >
          <icon v-if="isFolder" :name="open ? 'folder-open' : 'folder'"/>
          <icon v-if="!isFolder" name="file"/>
          {{model.name}}
        </span>
        <span @click="toggle" v-if="isFolder">[{{open ? '-' : '+'}}]</span>
      </div>

      <ul v-show="open" v-if="isFolder">
        <tree-view-item
          class="item"
          v-for="model in model.children"
          v-bind:key="model.uuid"
          v-model="selected"
          @click="selectOrgUnit(selected)"
          :model="model">
        </tree-view-item>
      </ul>
    </li>
</template>

<script>
  export default {
    name: 'treeViewItem',
    props: {
      value: Object,
      model: Object
    },
    data () {
      return {
        selected: {},
        open: false
      }
    },
    computed: {
      isFolder () {
        return this.model.hasChildren
      }
    },
    watch: {
      selected: function (newVal, oldVal) {
        this.selectOrgUnit(newVal)
      }
    },
    methods: {
      toggle () {
        if (this.isFolder) {
          this.open = !this.open
        }
      },

      selectOrgUnit (org) {
        this.$emit('input', org)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  ul {
    padding-left: 1rem;
  }
  .item {
    cursor: pointer;
    list-style-type: none;
  }
  .nav-link {
    display: inline-block;
  }
  .bold {
    font-weight: bold;
  }
</style>
