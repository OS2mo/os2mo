// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import isEqual from "lodash.isequal"
import moment from "moment"
import Service from "@/api/HttpCommon"

const state = {
  origin: undefined,
  destination: [],
  raw_destination: [],
}

const actions = {
  MAP_ORGANISATIONS({ commit, dispatch, state }) {
    Service.post(`/ou/${state.origin}/map`, {
      destination: state.destination,
      validity: {
        from: moment().format("YYYY-MM-DD"),
      },
    })
      .then((result) => {
        let names = new Set()
        // init names
        state.raw_destination.map((element) => {
          element.org_unit.map((unit) => {
            names.add(unit.name)
          })
        })

        dispatch("GET_ORGANISATION_MAPPINGS").then((response) => {
          // final names
          state.raw_destination.map((element) =>
            element.org_unit.map((unit) => names.add(unit.name))
          )
          for (const name of names) {
            commit(
              "log/newWorkLog",
              { type: "ORGANISATION_EDIT", value: { name: name } },
              { root: true }
            )
          }
        }) // catch outside
      })
      .catch((error) => {
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
        return error
      })
  },

  GET_ORGANISATION_MAPPINGS({ state, commit }) {
    return new Promise((resolve, reject) =>
      Service.get(`/ou/${state.origin}/details/related_unit`).then(
        (response) => {
          commit("SET_RAW_DESTINATION", response.data)
          resolve()
        },
        (error) => {
          reject(error)
        }
      )
    )
  },
}

const mutations = {
  SET_ORIGIN(state, uuid) {
    state.origin = uuid
  },

  SET_RAW_DESTINATION(state, response) {
    state.raw_destination = response
    state.destination = response.flatMap((func) =>
      func.org_unit.map((ou) => ou.uuid).filter((id) => id !== state.origin)
    )
  },

  SET_DESTINATION(state, uuidList) {
    state.destination = Array.from(uuidList)
  },
}

const getters = {
  origin: (state) => state.origin,
  destination: (state) => state.destination,
  isDirty: (state) => {
    let orig = new Set(
      state.raw_destination.flatMap((func) =>
        func.org_unit.map((ou) => ou.uuid).filter((id) => id !== state.origin)
      )
    )
    return !isEqual(new Set(state.destination), orig)
  },
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
}
