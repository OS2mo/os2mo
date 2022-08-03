// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { getField, updateField } from "vuex-map-fields"
import moment from "moment"
import Service from "@/api/HttpCommon"
import { EventBus, Events } from "@/EventBus"

const defaultState = () => {
  return {
    original: null,
    move: {
      type: "engagement",
      data: {
        person: null,
        validity: {
          from: moment(new Date()).format("YYYY-MM-DD"),
        },
      },
    },
    backendValidationError: null,
  }
}

const state = defaultState

const actions = {
  MOVE_EMPLOYEE({ commit, state }) {
    state.move.uuid = state.original.uuid
    let human_readable_move = {
      name: state.move.data.person.name,
      destination: state.move.data.org_unit.name,
    }

    return Service.post("/details/edit", state.move)
      .then((response) => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        commit(
          "log/newWorkLog",
          { type: "EMPLOYEE_MOVE", value: human_readable_move },
          { root: true }
        )
        return response.data
      })
      .catch((error) => {
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
