// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "./HttpCommon"
import { EventBus, Events } from "@/EventBus"
import store from "@/store"

const identfyItAssociationData = function (data) {
  // When creating an IT association, we must scrub the data to conform to
  // the special snowflake API request format that is supported by the backend.

  if (Array.isArray(data) && data[0].it) {
    // Probably data for creating a new IT association
    return data.map((d) => {
      return {
        type: "association",
        person: { uuid: d.person.uuid },
        org_unit: { uuid: d.org_unit.uuid },
        org: { uuid: d.org.uuid },
        primary: { uuid: d.primary.uuid },
        validity: { from: d.validity.from, to: d.validity.to },
        job_function: { uuid: d.job_function.uuid },
        it: { uuid: d.it.uuid },
      }
    })
  } else if (data.data && data.data.it) {
    // Probably data for editing an IT association

    var it_user_uuid
    if (Array.isArray(data.data.it) && data.data.it[0]) {
      it_user_uuid = data.data.it[0].uuid
    } else {
      it_user_uuid = data.data.it.uuid
    }

    return {
      type: "association",
      uuid: data.data.uuid,
      data: {
        person: { uuid: data.data.person.uuid },
        job_function: { uuid: data.data.job_function.uuid },
        org_unit: { uuid: data.data.org_unit.uuid },
        it: { uuid: it_user_uuid },
        validity: { from: data.data.validity.from, to: data.data.validity.to },
        primary: { uuid: data.data.primary.uuid },
      },
    }
  } else {
    // Nothing special. Just patch it through.
    return data
  }
}

export default {
  /**
   * Get engagement details for employee
   * @param {String} uuid - employee uuid
   * @see getDetail
   */
  getEngagementDetails(uuid, validity) {
    return this.getDetail(uuid, "engagement", validity)
  },

  /**
   * Base call for getting details.
   * @param {String} uuid - employee uuid
   * @param {String} detail - Name of the detail
   * @returns {Array} A list of options for the detail
   */
  getDetail(uuid, detail, validity) {
    validity = validity || "present"
    return Service.get(`/e/${uuid}/details/${detail}?validity=${validity}`)
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response })
      })
  },

  /**
   * Create a new employee
   * @param {String} uuid - employee uuid
   * @param {Array} create - A list of elements to create
   * @returns {Object} employee uuid
   */
  createEntry(create) {
    return Service.post("/details/create", create)
      .then((response) => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        return response
      })
      .catch((error) => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        store.commit("log/newError", { type: "ERROR", value: error.response })
        return error.response
      })
  },

  create(create) {
    return this.createEntry(identfyItAssociationData(create)).then((response) => {
      if (response.data.error) {
        return response.data
      }
      return response.data
    })
  },

  /**
   * Edit an employee
   * @param {String} uuid - employee uuid
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} employeee uuid
   */
  edit(edit) {
    let editData = identfyItAssociationData(edit)
    return Service.post("/details/edit", editData)
      .then((response) => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        return response.data
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response.data })
        return error.response.data
      })
  },
}
