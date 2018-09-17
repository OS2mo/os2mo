<template>
  <div class="wrapper">
    <div class="card" @click="open = !open">
      <div 
        class="card-header" 
        v-b-toggle="nameId" 
        aria-expanded="true" 
        :aria-controls="nameId"
      >
        <icon :name="open ? 'caret-down' : 'caret-right'"/>
        <strong>{{title}}</strong>
      </div>
    </div>

    <b-collapse :id="nameId" :visible="open" @shown="$emit('shown')">
      <slot>
        Put some content here
      </slot>
    </b-collapse>
  </div>
</template>

<script>
  export default {
    props: {
      title: {
        type: String,
        required: true
      },
      initiallyOpen: Boolean
    },

    data () {
      return {
        open: false
      }
    },

    computed: {
      nameId () {
        return 'mo-collapse-' + this._uid
      }
    },

    created () {
      this.open = this.initiallyOpen
    }
  }
</script>

<style scoped>
  .wrapper {
    margin-top: 1em;
  }
  
  .card-header {
    border-bottom: none;
    padding: 0.25rem 1.25rem;
  }
</style>
