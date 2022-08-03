// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { getField, updateField } from "vuex-map-fields"
import Service from "@/api/HttpCommon"
import { EventBus, Events } from "@/EventBus"

const defaultState = () => {
  return {
    leave: {
      person: null,
    },
    isLoading: false,
    backendValidationError: null,
  }
}

const state = defaultState

const actions = {
  leaveEmployee({ commit, state }) {
    let payload = state.leave

    commit("updateIsLoading", true)

    /**
     * @todo: all create calls are shared now. refactor to one central handler
     */
    return Service.post("/details/create", payload)
      .then((response) => {
        if (response.data.error) {
          commit("updateIsLoading", false)
          commit("updateError", response.data)
          return response.data
        }
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        commit("resetFields")

        commit(
          "log/newWorkLog",
          {
            type: "EMPLOYEE_LEAVE",
            value: { name: payload.person.name, leave_type: payload.leave_type.name },
          },
          { root: true }
        )
        return response.data
      })
      .catch((error) => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        commit("updateIsLoading", false)
        commit("updateError", error.response.data)
        commit(
          "log/newError",
          { type: "ERROR", value: error.response.data },
          { root: true }
        )
        return error.response.data
      })
  },

  resetFields({ commit }) {
    commit("resetFields")
  },
}

const mutations = {
  updateField,

  updateError(state, error) {
    state.backendValidationError = error
  },

  updateIsLoading(state, isLoading) {
    state.isLoading = isLoading
  },

  resetFields(state) {
    Object.assign(state, defaultState())
  },
}

const getters = {
  getField,
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
}
