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
        <loading v-show="model.children.length === 0"/>
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
  import Organisation from '../api/Organisation'
  import Loading from './Loading'

  export default {
    name: 'treeViewItem',
    components: {
      Loading
    },
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
          this.loadChildren()
        }
      },

      selectOrgUnit (org) {
        this.$emit('input', org)
      },

      loadChildren () {
        if (this.model.children.length === 0) {
          let vm = this
          Organisation.getFullHierachy(vm.model.org, vm.model.uuid)
          .then(response => {
            vm.model.children = response
          })
        }
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
