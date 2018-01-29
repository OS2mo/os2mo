<template>
  <div>
    <li class="item">
        <span @click="toggle">
          <icon class="icon" v-if="hasChildren" :name="open ? 'caret-down' : 'caret-right'"/>
        </span>

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
        
        @click="selectOrgUnit(model)">
          <icon class="icon" name="users"/>
          {{model.name}}
        </span>

      <ul v-show="open">
        <loading v-show="loading"/>
        <tree-view-item
          v-for="model in model.children"
          v-bind:key="model.uuid"
          v-model="selected"
          @click="selectOrgUnit(selected)"
          :model="model"
          :linkable="linkable">
        </tree-view-item>
      </ul>
    </li>
  </div>
</template>

<script>
  // import Organisation from '../api/Organisation'
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
      atDate: Date
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
      selected: function (newVal, oldVal) {
        this.selectOrgUnit(newVal)
      }
    },
    created () {
      if (this.firstOpen) {
        this.loadChildren()
      }
      this.open = this.firstOpen
    },
    methods: {
      toggle () {
        this.open = !this.open
        this.loadChildren()
      },

      selectOrgUnit (org) {
        this.$emit('input', org)
      },

      loadChildren () {
        let vm = this
        OrganisationUnit.getChildren(vm.model.uuid, vm.atDate)
        .then(response => {
          vm.model.children = response
          vm.loading = false
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
