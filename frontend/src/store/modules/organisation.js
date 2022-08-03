// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "@/api/HttpCommon"
import { EventBus, Events } from "@/EventBus"
import { _organisation } from "../actions/organisation"

const state = {
  name: undefined,
  user_key: undefined,
  uuid: undefined,
}

const actions = {
  [_organisation.actions.SET_ORGANISATION]({ commit }, payload) {
    let url
    if (payload == undefined) {
      url = "/o/"
    } else {
      url = `/o/${payload}/`
    }
    return Service.get(url)
      .then((response) => {
        commit(_organisation.mutations.SET_ORGANISATION, response.data)
        EventBus.$emit(Events.ORGANISATION_CHANGED, response.data)
      })
      .catch((error) => {
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
      })
  },
}

const mutations = {
  [_organisation.mutations.SET_ORGANISATION](state, payload) {
    // Fix bug (?) where 'payload' is a 1-item array rather than an object
    if (payload[0] !== undefined) {
      payload = payload[0]
    }
    state.name = payload.name
    state.user_key = payload.user_key
    state.uuid = payload.uuid
  },
}

const getters = {
  [_organisation.getters.GET_UUID]: (state) => state.uuid,
  [_organisation.getters.GET_ORGANISATION]: (state) => state,
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
}
