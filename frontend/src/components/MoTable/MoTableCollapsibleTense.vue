<template>
  <div>
    <mo-table-collapsible
      title="Fremtid"
      :columns="columns"
      :content="content.future"
      :content-type="contentType"
      :is-loading="loading.future"
      :edit-component="editComponent"
      :uuid="uuid"
      :type="type"
      @shown="$emit('shown', 'future')"
    />

    <mo-table-collapsible
      title="Nutid"
      :columns="columns"
      :content="content.present"
      :content-type="contentType"
      :is-loading="loading.present"
      :edit-component="editComponent"
      :uuid="uuid"
      :type="type"
      initially-open
      @shown="$emit('shown', 'present')"
    />

    <mo-table-collapsible
      title="Fortid"
      :columns="columns"
      :content="content.past"
      :content-type="contentType"
      :is-loading="loading.past"
      :edit-component="editComponent"
      :uuid="uuid"
      :type="type"
      @shown="$emit('shown', 'past')"
    />
  </div>
</template>

<script>
  /**
   * A table collapsible tense component.
   */

  import MoTableCollapsible from './MoTableCollapsible'

  export default {
    components: {
      MoTableCollapsible
    },

    props: {
      /**
       * Defines columns.
       */
      columns: Array,

      /**
       * Defines the loading.
       */
      loading: Object,

      /**
       * Defines the editComponent.
       */
      editComponent: Object,

      /**
       * Defines the content.
       */
      content: Object,

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
    }
  }
</script>
