<template>
<div class="wrapper">
  <div class="card" @click="open = !open">
    <div 
      class="card-header" 
      role="tab" 
      id="headingOne" 
      v-b-toggle="id" 
      aria-expanded="true" 
      :aria-controls="id">
        <icon :name="open ? 'caret-down' : 'caret-right'"/>
        <strong>{{title}}</strong>
    </div>
  </div>
  <b-collapse :id="id" :visible="open" @shown="$emit('shown')">
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
        id: 'collapse-' + this._uid,
        open: false
      }
    },
    created () {
      this.open = this.initiallyOpen
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .wrapper {
    margin-top: 1em;
  }

  .card-header {
    border-bottom: none;
    padding: 0.25rem 1.25rem;
  }
</style>