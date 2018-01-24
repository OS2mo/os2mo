import { HTTP, Service } from './HttpCommon'
import { EventBus } from '../EventBus'

// let selectedOrgUnit = null

export default {

  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Object} organisation unit object
   */
  get (uuid) {
    return Service.get(`/ou/${uuid}`)
    .then(response => {
      return response.data
    })
    .catch(e => {
      console.log(e)
    })
  },

  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Array} organisation unit children
   */
  getChildren (uuid) {
    console.log('organisation unit get children')
    return Service.get(`/ou/${uuid}/children`)
    .then(response => {
      return response.data
    })
    .catch(e => {
      console.log(e)
    })
  },

    /**
   * Create a new organisation unit
   * @param {Object} orgUnit - new organisation unit
   * @returns {Object} organisation unit uuid
   */
  create (orgUnit) {
    return HTTP.post('/org-unit', orgUnit)
    .then(response => {
      EventBus.$emit('org-unit-create', response.data)
      return response.data
    })
  },

    /**
   * Rename an organisation unit
   * @param {Object} orgUnit - organisation unit to rename
   * @param {String} newName - new name of the organisation unit
   * @returns {Object} organisation unit uuid
   */
  rename (orgUnit, newName) {
    orgUnit.name = newName
    return HTTP.post(`/org-unit/${orgUnit.uuid}?rename=true`, orgUnit)
    .then(response => {
      EventBus.$emit('org-unit-rename', response.data)
      return response.data
    })
  },

    /**
   * Move an organisation unit
   * @param {Object} orgUnit - organisation unit to move
   * @param {String} toUuid - uuid for the new parent organisation unit
   * @param {String} date - the move date
   * @returns {Object} organisation unit uuid
   */
  move (orgUnit, toUuid, date) {
    var obj = {
      'moveDate': date,
      'newParentOrgUnitUUID': toUuid
    }

    return HTTP.post(`/org-unit/${orgUnit.uuid}/actions/move`, obj)
    .then(response => {
      EventBus.$emit('org-unit-move', response.data)
      return response.data
    })
  },

  /**
   * Terminate a organisation unit
   * @param {Object} orgUnit - the organisation unit to end
   * @param {String} endDate - the date on which the organisation unit shall end
   * @returns {Object} organisation unit uuid
   */
  terminate (orgUnit, endDate) {
    return HTTP.delete(`/org-unit/${orgUnit.uuid}?endDate=${endDate}`)
    .then(response => {
      EventBus.$emit('org-unit-end-date', response.data)
      return response.data
    })
  }
}
