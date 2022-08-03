// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { getField, updateField } from "vuex-map-fields"
import moment from "moment"
import Service from "@/api/HttpCommon"

const defaultState = () => {
  return {
    employee: {},
    engagement: [],
    address: [],
    association: [],
    role: [],
    itSystem: [],
    manager: [],
    owner: [],
    organisation: {},
    backendValidationError: null,
  }
}

const state = defaultState

const actions = {
  CREATE_EMPLOYEE({ commit, state }) {
    let create = [].concat(
      state.engagement,
      state.address,
      state.association,
      state.role,
      state.itSystem,
      state.manager
    )

    let defaultValidity = {
      from: moment(new Date()).format("YYYY-MM-DD"),
    }

    create.forEach((e) => {
      if (!e.validity) {
        e.validity = defaultValidity
      }
    })

    let newEmployee = {
      name: state.employee.name,
      nickname_givenname: state.employee.nickname_givenname,
      nickname_surname: state.employee.nickname_surname,
      seniority: state.employee.seniority,
      cpr_no: state.employee.cpr_no,
      org: state.organisation,
      details: create,
    }

    return Service.post("/e/create", newEmployee)
      .then((response) => {
        if (response.data.error) {
          return response.data
        }
        let employeeUuid = response.data
        if (Array.isArray(response.data)) {
          employeeUuid = response.data[0]
        }
        commit(
          "log/newWorkLog",
          {
            type: "EMPLOYEE_CREATE",
            value: {
              name: newEmployee.name,
              org_name: newEmployee.org.name,
            },
          },
          { root: true }
        )
        return employeeUuid
      })
      .catch((error) => {
        commit(
          "log/newError",
          {
            type: "ERROR",
            value: error.response.data,
          },
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
