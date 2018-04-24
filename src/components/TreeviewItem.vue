<template>
  <li class="item">
      <span @click="toggle">
        <icon class="icon" v-if="hasChildren" :name="open ? 'caret-down' : 'caret-right'"/>
      </span>
        <icon class="icon" v-if="!hasChildren"/>

      <router-link 
        v-if="linkable"
        class="link-color" 
        :to="{ name: 'OrganisationDetail', params: { uuid: model.uuid } }"
      >
        <icon class="icon-color" name="users"/>
        {{model.name}}
      </router-link>

      <span 
        class="link-color"
        v-if="!linkable"
        @click="selectOrgUnit(model)"
      >
        <icon class="icon" name="users"/>
        {{model.name}}
      </span>

    <ul v-show="open">
      <loading v-show="loading"/>
      <tree-view-item
        v-for="(model, index) in model.children"
        :key="index"
        v-model="selected"
        :model="model"
        :at-date="atDate"
        :linkable="linkable"
      >
      </tree-view-item>
    </ul>
  </li>
</template>

<script>
  import OrganisationUnit from '../api/OrganisationUnit'
  import Loading from './Loading'

  export default {
    name: 'treeViewItem',
    components: {
      Loading
    },
    props: {
      value: Object,
      model: Object,
      firstOpen: Boolean,
      linkable: Boolean,
      atDate: [Date, String]
    },
    data () {
      return {
        selected: {},
        open: false,
        loading: true
      }
    },
    computed: {
      hasChildren () {
        return this.model.child_count > 0
      }
    },
    watch: {
      model (val) {
        this.loadChildren()
      },

      selected (newVal) {
        this.selectOrgUnit(newVal)
      },

      atDate () {
        this.loadChildren()
      }
    },
    mounted () {
      if (this.firstOpen) {
        this.loadChildren()
      }
      this.open = this.firstOpen
    },
    methods: {
      toggle () {
        this.open = !this.open
        if (this.open && this.model.children === undefined) this.loadChildren()
      },

      selectOrgUnit (org) {
        this.$emit('input', org)
      },

      loadChildren () {
        let vm = this
        vm.loading = true
        vm.model.children = []
        OrganisationUnit.getChildren(vm.model.uuid, vm.atDate)
          .then(response => {
            vm.loading = false
            vm.model.children = response
          })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  ul {
    padding-left: 1.25rem;
  }
  .extra-padding {
    padding-left: 0.05rem;
  }
  .item {
    cursor: pointer;
    list-style-type: none;
    display: block;
  }
  .nav-link {
    display: inline-block;
  }
  .icon {
    color: #343a40;
    width: 1rem;
  }
  .link-color{
    color: #212529;
    text-decoration: none;
  }
  .link-color:hover{
    color: #007bff;
  }
  .router-link-active{
    color:#007bff;
  }
</style>
