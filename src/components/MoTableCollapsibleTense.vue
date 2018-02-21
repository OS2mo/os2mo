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
    />

    <mo-table-collapsible
      title="Nutid"
      :columns="columns"
      :content="content.present"
      :content-type="contentType"
      :is-loading="loading.present"
      :edit-component="editComponent"
      :uuid="uuid"
      initially-open
    />

    <mo-table-collapsible
      title="Fortid"
      :columns="columns"
      :content="content.past"
      :content-type="contentType"
      :is-loading="loading.past"
      :edit-component="editComponent"
      :uuid="uuid"
    />
  </div>
</template>


<script>
  import MoTableCollapsible from './MoTableCollapsible'

  export default {
    components: {
      MoTableCollapsible
    },
    props: {
      columns: Array,
      loading: Object,
      editComponent: Object,
      content: Object,
      contentType: String,
      uuid: {
        type: String,
        required: true
      }
    }
  }
</script>
