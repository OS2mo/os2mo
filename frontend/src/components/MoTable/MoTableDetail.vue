SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-collapse
      class="detail-future"
      :title="$t('common.future')"
      @show="$emit('show', 'future')"
    >
      <mo-table
        class="detail-future"
        :columns="columns"
        :content="contentStore.future"
        :content-type="contentType"
        :edit-component="entryComponent"
        :edit-uuid="uuid"
        :type="type"
        @update="$emit('show', 'future')"
      />
    </mo-collapse>

    <mo-collapse
      class="detail-present"
      :title="$t('common.present')"
      visible
      @show="$emit('show', 'present')"
    >
      <mo-table
        :columns="columns"
        :content="contentStore.present"
        :content-type="contentType"
        :edit-component="entryComponent"
        :edit-uuid="uuid"
        :type="type"
        @update="$emit('show', 'present')"
      />
    </mo-collapse>

    <mo-collapse
      class="detail-past"
      :title="$t('common.past')"
      @show="$emit('show', 'past')"
    >
      <mo-table
        :columns="columns"
        :content="contentStore.past"
        :content-type="contentType"
        :edit-component="entryComponent"
        :edit-uuid="uuid"
        :type="type"
        @update="$emit('show', 'past')"
      />
    </mo-collapse>

    <mo-entry-create-modal
      :type="type"
      class="mt-3"
      :uuid="uuid"
      :entry-component="entryComponent"
      v-if="!hideCreate"
    />
  </div>
</template>

<script>
/**
 * A employeedetail component.
 */

import MoTable from "@/components/MoTable/MoTable"
import MoCollapse from "@/components/atoms/MoCollapse"
import MoEntryCreateModal from "@/components/MoEntryCreateModal"

export default {
  components: {
    MoTable,
    MoCollapse,
    MoEntryCreateModal,
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
    entryComponent: Object,

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
      required: true,
    },

    /**
     * Defines a required type.
     */
    type: {
      type: String,
      required: true,
    },

    hideCreate: Boolean,
  },
  computed: {
    contentStore() {
      return this.content || {}
    },
  },
}
</script>
