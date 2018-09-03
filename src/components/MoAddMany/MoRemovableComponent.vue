<template>
  <div v-if="!removed">
    <div class="row">
      <div class="col">
        <component 
          :is="entryComponent"
          v-model="entryValue"
          :validity-hidden="validityHidden"
        />
      </div>

      <div class="col-1 v-center">
        <button @click="remove()" type="button" class="btn btn-outline-danger" :class="smallButtons ? 'btn-sm' : ''">
          <icon name="minus"/>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      value: Object,
      entryComponent: {
        type: Object,
        required: true
      },
      smallButtons: Boolean,
      validityHidden: Boolean
    },

    data () {
      return {
        entryValue: {},
        removed: false
      }
    },

    updated () {
      this.$emit('input', this.entryValue)
    },

    created () {
      this.entryValue = this.value
    },

    methods: {
      remove () {
        this.entryValue = {}
        this.removed = true
      }
    }
  }
</script>

<style scoped>
  .v-center {
    margin-bottom: auto;
    margin-top: auto;
  }
</style>
