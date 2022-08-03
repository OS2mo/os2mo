// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"
import { getField, updateField } from "vuex-map-fields"
import Service from "@/api/HttpCommon"
import { EventBus, Events } from "@/EventBus"
import moment from "moment"

const defaultState = () => {
  return {
    employee: null,
    endDate: moment(new Date()).format("YYYY-MM-DD"),
    details: {},
    isLoading: false,
    backendValidationError: null,
  }
}

const state = defaultState

const actions = {
  terminateEmployee({ state, commit }) {
    let payload = {
      validity: {
        to: state.endDate,
      },
    }

    commit("updateIsLoading", true)

    return Service.post(`/e/${state.employee.uuid}/terminate`, payload)
      .then((response) => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        commit(
          "log/newWorkLog",
          { type: "EMPLOYEE_TERMINATE", value: { name: state.employee.name } },
          { root: true }
        )
        commit("resetFields")
        return response.data
      })
      .catch((error) => {
        commit("updateIsLoading", false)
        commit("updateError", error.response.data)
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
        return error
      })
  },

  // TODO: copypaste from the employee module. Need to be refactored
  setDetails({ state, commit }, payload) {
    payload.validity = payload.validity || "present"
    let uuid = payload.uuid || state.employee.uuid
    return Service.get(
      `/e/${uuid}/details/${payload.detail}?validity=${payload.validity}`
    )
      .then((response) => {
        let content = {
          key: payload.detail,
          validity: payload.validity,
          value: response.data,
        }
        commit("setDetail", content)
      })
      .catch((error) => {
        console.error(error)
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

  // todo: copy paste from employee module. need to be refactored
  setDetail(state, payload) {
    if (!state.details[payload.key]) {
      Vue.set(state.details, payload.key, {})
    }
    Vue.set(state.details[payload.key], payload.validity, payload.value)
  },
}

const getters = {
  getField,
  getDetails: (state) => state.details,
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
}
