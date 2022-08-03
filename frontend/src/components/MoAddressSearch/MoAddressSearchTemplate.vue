SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <label>{{ item.location.name }}</label>
  </div>
</template>

<script>
/**
 * A address search template.
 */

export default {
  props: {
    /**
     * Item to display
     * @type {Object}
     */
    item: {
      type: Object,
      default: () => {
        return {
          location: {},
        }
      },
      required: true,
    },
  },
}
</script>
