SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div class="card col">
    <div class="card-body d-flex flex-column">
      <h4 class="card-title">
        <icon name="flask" />
        {{ $tc("shared.admin_panel") }}
      </h4>
      <h5>
        <icon name="puzzle-piece" />
        {{ $tc("shared.feature_flag_title") }}
      </h5>
      ...
    </div>
  </div>
</template>

<script>
import "vue-awesome/icons/flask"
import "vue-awesome/icons/puzzle-piece"

export default {}
</script>
