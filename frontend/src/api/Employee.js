// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from './HttpCommon'
import { EventBus, Events } from '@/EventBus'
import store from '@/store'

const sanitizeData = function(data) {

  let sane_data = []
  
  if (!data[0].it) {
    sane_data = data
  } else {
    // IT association hack:
    // When creating an IT association, we must scrub the data to conform to 
    // the special API request format that is supported by the backend.
    for (let d of data) {
      sane_data.push({
        type: "association",
        person: { uuid: d.person.uuid },
        org_unit: { uuid: d.org_unit.uuid },
        org: { uuid: d.org.uuid },
        job_function: { uuid: d.job_function.uuid },
        it: { uuid: d.it.uuid },
        validity: { from: d.validity.from, to: d.validity.to },
        association_type: { uuid: d.association_type.uuid }
        // Primary missing
      })
    }
  }

  return sane_data
}

export default {

  /**
   * Get engagement details for employee
   * @param {String} uuid - employee uuid
   * @see getDetail
   */
  getEngagementDetails (uuid, validity) {
    return this.getDetail(uuid, 'engagement', validity)
  },

  /**
   * Base call for getting details.
   * @param {String} uuid - employee uuid
   * @param {String} detail - Name of the detail
   * @returns {Array} A list of options for the detail
   */
  getDetail (uuid, detail, validity) {
    validity = validity || 'present'
    return Service.get(`/e/${uuid}/details/${detail}?validity=${validity}`)
      .then(response => {
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', { type: 'ERROR', value: error.response })
      })
  },

  // new (employee) {
  //   return Service.post('/e/create', employee)
  //     .then(response => {
  //       let employeeUuid = response.data
  //       if (Array.isArray(response.data)) {
  //         employeeUuid = response.data[0]
  //       }
  //       if (response.data.error) {
  //         return response.data
  //       }
  //       store.commit('log/newWorkLog', { type: 'EMPLOYEE_CREATE', value: employeeUuid })
  //       return employeeUuid
  //     })
  //     .catch(error => {
  //       store.commit('log/newError', { type: 'ERROR', value: error.response.data })
  //       return error.response.data
  //     })
  // },

  /**
   * Create a new employee
   * @param {String} uuid - employee uuid
   * @param {Array} create - A list of elements to create
   * @returns {Object} employee uuid
   */
  createEntry (create) {
    return Service.post('/details/create', create)
      .then(response => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        return response
      })
      .catch(error => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        store.commit('log/newError', { type: 'ERROR', value: error.response })
        return error.response
      })
  },

  create (create) {

    return this.createEntry(sanitizeData(create))
      .then(response => {
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
  edit (edit) {
    return Service.post('/details/edit', edit)
      .then(response => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', { type: 'ERROR', value: error.response.data })
        return error.response.data
      })
  }
}
