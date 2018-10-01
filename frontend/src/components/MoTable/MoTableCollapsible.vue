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
  /**
   * A table collapsible component.
   */

  import MoCollapse from '@/components/atoms/MoCollapse'
  import MoTable from './MoTable'

  export default {
    components: {
      MoCollapse,
      MoTable
    },

    props: {
      /**
       * Defines title.
       */
      title: String,

      /**
       * Defines columns.
       */
      columns: Array,

      /**
       * This boolean property defines the loading.
       */
      isLoading: Boolean,

      /**
       * This boolean property defines the initiallyOpen.
       */
      initiallyOpen: Boolean,

      /**
       * Defines the editComponent.
       */
      editComponent: Object,

      /**
       * Defines the content.
       */
      content: Array,

      /**
       * Defines the contentType.
       */
      contentType: String,

      /**
       * Defines a required uuid.
       */
      uuid: {
        type: String,
        required: true
      },

      /**
       * Defines a required type.
       */
      type: {
        type: String,
        required: true
      }
    },

    methods: {
      /**
       * When isCollapsed change, update val.
       */
      isCollapsed (val) {
        this.$emit('is-collapsed', val)
      }
    }
  }
</script>
