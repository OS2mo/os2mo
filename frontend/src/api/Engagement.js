// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "./HttpCommon"
import { EventBus, Events } from "@/EventBus"
import store from "@/store"

export default {
  /**
   * Create a new engagement detail
   */
  createEntry(create) {
    return Service.post("/details/create", create)
      .then((response) => {
        EventBus.$emit(Events.ENGAGEMENT_CHANGED)
        return response
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response })
        console.log("mw", error.response.data)
        return error.response.data
      })
  },

  /**
   * Edit an engagement detail
   */
  edit(edit) {
    return Service.post("/details/edit", edit)
      .then((response) => {
        EventBus.$emit(Events.ENGAGEMENT_CHANGED)
        return response.data
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response.data })
        return error.response.data
      })
  },
}
