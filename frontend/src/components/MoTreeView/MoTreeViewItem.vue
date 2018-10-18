<template>
  <li class="item">
      <span @click="toggle()">
        <icon class="icon" v-if="hasChildren" :name="open ? 'caret-down' : 'caret-right'"/>
      </span>
      <span class="icon" v-if="!hasChildren"/>

      <span class="link-color" @click="$emit('input', item)">
        <icon class="icon" name="users"/>
        {{item.name}}
      </span>

    <ul v-show="open">
      <mo-tree-view-item
        v-for="child in item.children"
        :key="child.uuid"
        :item="child"
        @show-children="$emit('show-children', $event)"
        @click="$emit('input', $event)"
      />
    </ul>
  </li>
</template>

<script>
  export default {
    name: 'MoTreeViewItem',

    props: {
      item: Object,
      unfold: Boolean
    },

    data () {
      return {
        open: false
      }
    },

    computed: {
      hasChildren () {
        return this.item.child_count > 0
      }
    },
    mounted () {
      if (this.unfold) {
        this.open = this.unfold
        this.$emit('show-children', this.item)
      }
    },

    methods: {
      toggle () {
        this.open = !this.open
        if (this.open && this.item.children === undefined) this.$emit('show-children', this.item)
      }
    }
  }
</script>

<style scoped>
  ul {
    padding-left: 1.25rem;
  }

  .item {
    cursor: pointer;
    list-style-type: none;
    display: block;
    white-space: nowrap;
  }

  .icon {
    color: #343a40;
    width: 1rem;
    display: inline-block;
  }

  .link-color {
    color: #212529;
    text-decoration: none;
  }

  .link-color:hover {
    color: #007bff;
  }

  .link-active {
    color:#007bff;
    font-weight: bold;
  }
</style>
