// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { getField, updateField } from "vuex-map-fields"
import Service from "@/api/HttpCommon"
import OrganisationUnit from "@/api/OrganisationUnit"
import { EventBus, Events } from "@/EventBus"
import moment from "moment"

const defaultState = () => {
  return {
    employees: [],
    selected: [],
    moveDate: moment(new Date()).format("YYYY-MM-DD"),
    orgUnitSource: null,
    orgUnitDestination: null,
    backendValidationError: null,
    columns: [
      { label: "person", data: "person" },
      { label: "engagement_type", data: "engagement_type" },
      { label: "job_function", data: "job_function" },
    ],
  }
}

const state = defaultState

const actions = {
  moveManyEmployees({ commit, state }) {
    let moves = state.selected.map((engagement) => {
      return {
        type: "engagement",
        uuid: engagement.uuid,
        data: {
          org_unit: state.orgUnitDestination,
          validity: {
            from: state.moveDate,
          },
        },
      }
    })

    let human_readable_moves = state.selected.map((engagement) => {
      return {
        name: engagement.person.name,
        destination: state.orgUnitDestination.name,
      }
    })

    commit("updateIsLoading", true)

    return Service.post("/details/edit", moves)
      .then((response) => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        commit("resetFields")

        // attempt nice logging

        for (const move of human_readable_moves) {
          commit(
            "log/newWorkLog",
            { type: "EMPLOYEE_MOVE", value: move },
            { root: true }
          )
        }

        return response.data
      })
      .catch((error) => {
        commit("updateError", error.response.data)
        commit("updateIsLoading", false)
        commit(
          "log/newError",
          { type: "ERROR", value: error.response.data },
          { root: true }
        )
        return error.response.data
      })
  },

  getEmployees({ state, commit }) {
    if (!state.orgUnitSource) return
    let validity = undefined
    let atDate = state.moveDate
    OrganisationUnit.getDetail(state.orgUnitSource.uuid, "engagement", validity, atDate)
      .then((response) => {
        commit("updateEmployees", response)
      })
      .catch((error) => {
        commit(
          "log/newError",
          { type: "ERROR", value: error.response.data },
          { root: true }
        )
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

  updateOrgUnitSource(state, orgUnit) {
    state.orgUnitSource = orgUnit
  },

  updateEmployees(state, employees) {
    state.employees = employees
  },

  resetFields(state) {
    Object.assign(state, defaultState())
  },
}

const getters = {
  getField,

  employees: (state) => state.employees,
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
}
