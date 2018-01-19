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
  <b-collapse :id="id" :visible="visible">
    <loading v-show="isLoading"/>
    <span v-show="!isLoading && content === undefined">Intet at vise</span>
    <table class="table table-striped" v-show="!isLoading && content !== undefined">
      <thead>
        <tr>
          <th 
            scope="col" 
            v-for="label in labels" 
            v-bind:key="label"
          >
            {{label}}
          </th>
        </tr>
      </thead>

      <tbody>
        <tr 
          v-for="unit in content" 
          v-bind:key="unit.uuid"
        >
          <td>{{unit.name}}</td>
          <td>
            <span v-if="unit.type">{{unit.type.name}}</span>
          </td>
          <td>
            <span v-if="unit['parent-object']">{{unit['parent-object'].name}}</span>
          </td>
          <td>{{unit['valid-from']}}</td>
          <td>{{unit['valid-to']}}</td>
        </tr>
      </tbody>
    </table>
  </b-collapse>
</div>
</template>

<script>
  import Loading from './Loading'

  export default {
    components: {
      Loading
    },
    props: {
      title: {
        type: String,
        default: 'Skift mig'
      },
      labels: Array,
      content: Array,
      visible: Boolean
    },
    watch: {
      content: function (newVal, oldVal) {
        this.isLoading = false
      }
    },
    created () {
      if (this.visible) {
        this.open = this.visible
      }
      if (this.content !== undefined && this.content.length > 0) {
        this.isLoading = false
      }
    },
    data () {
      return {
        id: 'collapse-' + this._uid,
        isLoading: true,
        open: false
      }
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

table {
  margin-top: 0;
}
</style>