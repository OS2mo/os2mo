SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <span>{{ item.name }}</span>
  </div>
</template>

<script>
/**
 * A searchbar template component.
 */

export default {
  props: {
    /**
     * Defines a required item name.
     */
    item: { required: true }
  }
}
</script>
