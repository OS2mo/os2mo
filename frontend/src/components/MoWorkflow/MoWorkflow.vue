SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div id="mo-workflow">
    <slot></slot>
  </div>
</template>

<style scoped>
#mo-workflow {
  position: fixed;
  right: -240px;
  top: 100px;
  z-index: 1;
}
</style>
