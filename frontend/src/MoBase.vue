SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-navbar />
    <div>
      <router-view />
    </div>
  </div>
</template>

<script>
import MoNavbar from "@/components/MoNavbar"

export default {
  components: {
    MoNavbar,
  },

  name: "MoBase",
}
</script>
