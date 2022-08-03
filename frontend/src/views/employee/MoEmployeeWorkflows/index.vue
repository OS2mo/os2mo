SPDX-FileCopyrightText: 2017-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div
    v-shortkey="{
      employeeCreate: ['ctrl', 'shift', 'c'],
      employeeLeave: ['ctrl', 'shift', 'o'],
      employeeMove: ['ctrl', 'shift', 'm'],
      employeeMoveMany: ['ctrl', 'shift', 'y'],
      employeeTerminate: ['ctrl', 'shift', 'd'],
    }"
    @shortkey="shortcuts($event)"
  >
    <mo-workflow>
      <mo-workflow-button
        class="btn-employee-create"
        :label="$t('workflows.employee.new_employee')"
        icon="user-plus"
        v-b-modal.employeeCreate
      />

      <mo-workflow-button
        class="btn-employee-leave"
        :label="$t('workflows.employee.leave')"
        icon="user-md"
        v-b-modal.employeeLeave
      />

      <mo-workflow-button
        class="btn-employee-move"
        :label="$t('workflows.employee.move_engagement')"
        icon="user-tag"
        v-b-modal.employeeMove
      />

      <mo-workflow-button
        class="btn-employee-moveMany"
        :label="$t('workflows.employee.move_many_engagements')"
        icon="users"
        v-b-modal.employeeMoveMany
      />

      <mo-workflow-button
        class="btn-employee-terminate"
        :label="$t('workflows.employee.terminate_employee')"
        icon="user-times"
        v-b-modal.employeeTerminate
      />
    </mo-workflow>

    <!-- Modal Components -->
    <b-modal
      id="employeeCreate"
      size="lg"
      :title="$t('workflows.employee.new_employee')"
      ref="employeeCreate"
      hide-footer
      no-close-on-backdrop
      lazy
      v-model="showCreate"
    >
      <mo-employee-create :show="showCreate" @submitted="$refs.employeeCreate.hide()" />
    </b-modal>

    <b-modal
      id="employeeLeave"
      size="lg"
      :title="$t('workflows.employee.leave')"
      ref="employeeLeave"
      hide-footer
      lazy
      no-close-on-backdrop
      v-model="showLeave"
    >
      <mo-employee-leave :show="showLeave" @submitted="$refs.employeeLeave.hide()" />
    </b-modal>

    <b-modal
      id="employeeMove"
      size="lg"
      :title="$t('workflows.employee.move_engagement')"
      ref="employeeMove"
      hide-footer
      lazy
      no-close-on-backdrop
      v-model="showMove"
    >
      <mo-employee-move :show="showMove" @submitted="$refs.employeeMove.hide()" />
    </b-modal>

    <b-modal
      id="employeeMoveMany"
      size="lg"
      :title="$t('workflows.employee.move_many_engagements')"
      ref="employeeMoveMany"
      hide-footer
      lazy
      no-close-on-backdrop
      v-model="showMoveMany"
    >
      <mo-employee-move-many
        :show="showMoveMany"
        @submitted="$refs.employeeMoveMany.hide()"
      />
    </b-modal>

    <b-modal
      id="employeeTerminate"
      size="lg"
      :title="$t('workflows.employee.terminate_employee')"
      ref="employeeTerminate"
      hide-footer
      lazy
      no-close-on-backdrop
      v-model="showTerminate"
    >
      <mo-employee-terminate
        :show="showTerminate"
        @submitted="$refs.employeeTerminate.hide()"
      />
    </b-modal>
  </div>
</template>

<script>
/**
 * A Employee workflow component.
 */

import MoWorkflow from "@/components/MoWorkflow/MoWorkflow"
import MoWorkflowButton from "@/components/MoWorkflow/MoWorkflowButton"
import MoEmployeeCreate from "./MoEmployeeCreate"
import MoEmployeeLeave from "./MoEmployeeLeave"
import MoEmployeeMove from "./MoEmployeeMove"
import MoEmployeeMoveMany from "./MoEmployeeMoveMany"
import MoEmployeeTerminate from "./MoEmployeeTerminate"
import bModalDirective from "bootstrap-vue/es/directives/modal/modal"
import bModal from "bootstrap-vue/es/components/modal/modal"

export default {
  components: {
    MoWorkflow,
    MoWorkflowButton,
    MoEmployeeCreate,
    MoEmployeeLeave,
    MoEmployeeMove,
    MoEmployeeMoveMany,
    MoEmployeeTerminate,
    "b-modal": bModal,
  },
  directives: {
    "b-modal": bModalDirective,
  },

  data() {
    return {
      showCreate: false,
      showLeave: false,
      showMove: false,
      showMoveMany: false,
      showTerminate: false,
    }
  },
  methods: {
    /**
     * Trigger the popup workflows with the key shortcuts.
     */
    shortcuts(event) {
      this.$root.$emit("bv::show::modal", event.srcKey)
    },
  },
}
</script>
