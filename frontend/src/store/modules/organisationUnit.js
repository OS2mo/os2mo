// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"
import Service from "@/api/HttpCommon"
import { _organisationUnit as _orgUnit } from "../actions/organisationUnit"

const defaultState = () => {
  return {
    name: undefined,
    user_key: undefined,
    uuid: undefined,
    org: undefined,
    org_uuid: undefined,
    parents: [],
    location: undefined,
    user_settings: {},
    details: {},
    validity: {},
    isLoading: false,
  }
}

const state = defaultState
const relevantPerson = new Map([
  ["manager", (obj) => obj.person],
  ["owner", (obj) => obj.owner],
])

const ShowIfInherited = (orgUnitUuid, content) => {
  if (content.key === "manager" || content.key === "owner") {
    /* show if inherited */
    if (content.value) {
      let person_method = relevantPerson.get(content.key)
      content.value.forEach((element) => {
        if (element.org_unit.uuid !== orgUnitUuid) {
          let person = person_method(element)
          if (person) {
            person.name += " (*)"
            element.inherited = true
          }
        }
      })
    }
  }
  return content
}

const actions = {
  async [_orgUnit.actions.SET_ORG_UNIT]({ commit }, payload) {
    let atDate = payload.atDate
    if (atDate instanceof Date) atDate = atDate.toISOString().split("T")[0]
    const response = await Service.get(`/ou/${payload.uuid}/?at=${atDate}`)

    if (response) {
      commit(_orgUnit.mutations.SET_ORG_UNIT, response.data)
    } else {
      commit("log/newError", { type: "ERROR", value: response }, { root: true })
    }
    return response.data
  },

  [_orgUnit.actions.SET_DETAIL]({ state, commit }, payload) {
    payload.validity = payload.validity || "present"
    let uuid = payload.uuid || state.uuid
    let atDate = payload.atDate
    let inheritFlag = ""
    if (atDate instanceof Date) atDate = atDate.toISOString().split("T")[0]
    if (payload.detail === "manager" && state.user_settings.orgunit.inherit_manager) {
      inheritFlag = "&inherit_manager=1"
    } else if (payload.detail === "owner") {
      inheritFlag = "&inherit_owner=1"
    }
    return Service.get(
      `/ou/${uuid}/details/${payload.detail}?validity=${payload.validity}&at=${atDate}${inheritFlag}`
    )
      .then((response) => {
        let content = ShowIfInherited(state.uuid, {
          key: payload.detail,
          validity: payload.validity,
          value: response.data,
        })
        commit(_orgUnit.mutations.SET_DETAIL, content)
      })
      .catch((error) => {
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
      })
  },
}

const mutations = {
  [_orgUnit.mutations.SET_ORG_UNIT](state, payload) {
    state.uuid = payload.uuid
    state.name = payload.name
    state.user_key = payload.user_key
    state.org = payload.org
    state.org_uuid = payload.org.uuid
    state.location = payload.location
    state.user_settings = payload.user_settings
    state.validity = payload.validity
    state.parents = []

    for (let current = payload.parent; current; current = current.parent) {
      state.parents.push(current.uuid)
    }
  },

  [_orgUnit.mutations.RESET_ORG_UNIT](state) {
    Object.assign(state, defaultState())
  },

  [_orgUnit.mutations.SET_DETAIL](state, payload) {
    if (!state.details[payload.key]) {
      Vue.set(state.details, payload.key, {})
    }
    Vue.set(state.details[payload.key], payload.validity, payload.value)
  },
}

const getters = {
  [_orgUnit.getters.GET_ORG_UNIT]: (state) => state,
  [_orgUnit.getters.GET_ORG_UNIT_UUID]: (state) => state.uuid,
  [_orgUnit.getters.GET_DETAIL]: (state) => (id) => state.details[id] || {},
  [_orgUnit.getters.GET_DETAILS]: (state) => state.details || {},
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
}
