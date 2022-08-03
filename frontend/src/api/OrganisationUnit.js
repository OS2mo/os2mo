// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "./HttpCommon"
import { EventBus, Events } from "@/EventBus"
import store from "@/store"
import URLSearchParams from "@ungap/url-search-params"
import i18n from "../i18n.js"

export default {
  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Object} organisation unit object
   */
  get(uuid, atDate) {
    if (atDate instanceof Date) atDate = atDate.toISOString().split("T")[0]
    return Service.get(`/ou/${uuid}/?at=${atDate}`)
      .then((response) => {
        EventBus.$emit(Events.ORGANISATION_CHANGED, response.data.org)
        return response.data
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response })
      })
  },

  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Array} organisation unit children
   */
  getChildren(uuid, atDate, extra) {
    if (atDate instanceof Date) atDate = atDate.toISOString().split("T")[0]

    const params = new URLSearchParams()

    if (atDate) {
      params.append("at", atDate)
    }

    if (extra !== undefined) {
      for (const key in extra) {
        params.append(key, extra[key])
      }
    }

    return Service.get(`/ou/${uuid}/children?${params}`)
      .then((response) => {
        return response.data.sort((a, b) => (a.name > b.name ? 1 : -1))
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response })
      })
  },

  /**
   * Get an organisation unit
   * @param {Array|String} uuids - organisation unit uuid
   * @returns {Array} organisation unit children
   */
  getAncestorTree(uuids, atDate, extra) {
    if (atDate instanceof Date) atDate = atDate.toISOString().split("T")[0]

    if (!(uuids instanceof Array)) {
      uuids = [uuids]
    }

    const params = new URLSearchParams()

    if (atDate) {
      params.append("at", atDate)
    }

    for (const uuid of uuids) {
      params.append("uuid", uuid)
    }

    if (extra !== undefined) {
      for (const key in extra) {
        params.append(key, extra[key])
      }
    }

    return Service.get(`/ou/ancestor-tree?${params}`).then((response) => {
      return response.data
    })
  },

  /**
   * Get organisation unit details
   * @see getDetail
   */
  getUnitDetails(uuid, validity) {
    return this.getDetail(uuid, "unit", validity)
  },

  /**
   * Get address for organisation unit details
   * @see getDetail
   */
  getAddressDetails(uuid, validity) {
    return this.getDetail(uuid, "address", validity).then((response) => {
      response.forEach((addr) => {
        delete addr.validity
      })
      return response
    })
  },

  /**
   * Base call for getting details.
   * @param {String} uuid - organisation unit uuid
   * @param {String} detail - Name of the detail
   * @param {String} validity - Can be either past, present or future
   * @returns {Array} A list of options for the detail
   */
  getDetail(uuid, detail, validity, atDate) {
    validity = validity || "present"
    if (atDate instanceof Date) atDate = atDate.toISOString().split("T")[0]
    return Service.get(
      `/ou/${uuid}/details/${detail}?validity=${validity}&at=${atDate}`
    )
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response })
      })
  },

  /**
   * Create a new organisation unit
   * @param {Object} orgUnit - new organisation unit
   * @param {Array} create - A list of elements to create
   * @returns {Object} organisation unit uuid
   */
  create(create) {
    return Service.post("/ou/create", create)
      .then((response) => {
        EventBus.$emit(Events.UPDATE_TREE_VIEW)
        store.commit("log/newWorkLog", {
          type: "ORGANISATION_CREATE",
          value: {
            name: create.name,
            parent: create.parent
              ? create.parent.name
              : i18n.t("shared.main_organisation"),
          },
        })
        return response.data
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response.data })
        return error.response.data
      })
  },

  /**
   * Create a new organisation unit entry
   * @param {Object} orgUnit - new organisation unit
   * @param {String} uuid - organisation uuid
   * @param {Array} create - A list of elements to create
   * @returns {Object} organisation unit uuid
   */
  createEntry(create) {
    return Service.post("/details/create", create)
      .then((response) => {
        EventBus.$emit(Events.ORGANISATION_UNIT_CHANGED)
        return response.data
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response })
        return error.response.data
      })
  },

  /**
   * Edit an organisation unit
   * @returns {Object} organisation unit uuid
   */
  editEntry(edit) {
    return Service.post("/details/edit", edit)
      .then((response) => {
        EventBus.$emit(Events.UPDATE_TREE_VIEW)
        EventBus.$emit(Events.ORGANISATION_UNIT_CHANGED)
        return response
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response })
        return error.response
      })
  },

  edit(edit) {
    return this.editEntry(edit).then((response) => {
      return response.data
    })
  },

  /**
   * Rename a new organisation unit
   * @returns {Object} organisation unit uuid
   * @see edit
   */
  rename(edit) {
    return this.editEntry(edit).then((response) => {
      return response.data
    })
  },

  /**
   * Move a new organisation unit
   * @param {Object} edit - containing the move-specs
   * @param {string} human_readable_name - name of the moving unit
   * @param {string} human_readable_new_parent - name of the new parent of the moving unit
   * @returns {Object} organisation unit uuid
   * @see edit
   */
  move(edit, human_readable_name, human_readable_new_parent) {
    return this.editEntry(edit).then((response) => {
      if (response.data.error) {
        return response.data
      }
      EventBus.$emit(Events.UPDATE_TREE_VIEW)
      store.commit("log/newWorkLog", {
        type: "ORGANISATION_MOVE",
        value: { name: human_readable_name, parent: human_readable_new_parent },
      })
      return response.data
    })
  },

  /**
   * Terminate a organisation unit
   * @param {Object} uuid - the organisation unit to end
   * @param {Object} terminate - the date on which the organisation unit shall end
   * @param {String} human_readable_name - the name corresponding to the uuid
   * @returns {Object} organisation unit uuid
   */
  terminate(uuid, terminate, human_readable_name) {
    return Service.post(`/ou/${uuid}/terminate`, terminate)
      .then((response) => {
        EventBus.$emit(Events.UPDATE_TREE_VIEW)
        EventBus.$emit(Events.ORGANISATION_UNIT_CHANGED)
        console.log(terminate)
        store.commit("log/newWorkLog", {
          type: "ORGANISATION_TERMINATE",
          value: { name: human_readable_name, terminate: terminate.validity.to },
        })
        return response.data
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response.data })
        return error.response.data
      })
  },
}
