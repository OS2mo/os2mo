<template>
  <mo-collapse 
    :title="title" 
    :initially-open="initiallyOpen" 
    @shown="$emit('shown')"
  >
    <mo-table 
      :columns="columns"
      :content="content"
      :content-type="contentType"
      :is-loading="isLoading"
      :edit-component="editComponent"
      :edit-uuid="uuid"
      :type="type"
    />
  </mo-collapse>
</template>


<script>
  import MoCollapse from '@/components/atoms/MoCollapse'
  import MoTable from './MoTable'

  export default {
    components: {
      MoCollapse,
      MoTable
    },

    props: {
      title: String,
      columns: Array,
      isLoading: Boolean,
      initiallyOpen: Boolean,
      editComponent: Object,
      content: Array,
      contentType: String,
      uuid: {
        type: String,
        required: true
      },
      type: {
        type: String,
        required: true
      }
    },

    methods: {
      isCollapsed (val) {
        this.$emit('is-collapsed', val)
      }
    }
  }
</script>
