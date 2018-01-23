<template>
    <li class="item" v-if="model.uuid">
        <span @click="toggle">
          <icon class="icon" v-if="isFolder" :name="open ? 'caret-down' : 'caret-right'"/>
        </span>
        <router-link 
          v-if="linkAble"
          class="link-color" 
          :to="{ name: 'OrganisationDetail', params: { uuid: model.uuid } }"
        >
          <icon class="icon-color" name="users"/>
          {{model.name}}
        </router-link>

        <span 
        class="link-color"
        v-if="!linkAble"
        
        @click="selectOrgUnit(model)">
          <icon class="icon" name="users"/>
          {{model.name}}
        </span>

      <ul v-show="open" v-if="isFolder">
        <loading v-show="model.children.length === 0"/>
        <tree-view-item
          v-for="model in model.children"
          v-bind:key="model.uuid"
          v-model="selected"
          @click="selectOrgUnit(selected)"
          :model="model"
          :link-able="linkAble">
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
      model: Object,
      firstOpen: {
        type: Boolean,
        default: false
      },
      linkAble: {
        type: Boolean,
        default: false
      }
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
    created () {
      this.open = this.firstOpen
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
