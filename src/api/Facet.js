import { Service } from './HttpCommon'

export default {
  /**
   * Get a list of all available facets
   * @param {String} orgUuid - organisation uuid
   * @returns {Array} a list of all available facets
   */
  getAll (orgUuid) {
    return Service.get(`/o/${orgUuid}/f/`)
    .then(response => {
      return response.data
    })
  },

  organisationUnitTypes (orgUuid) {
    return Service.get(`/o/${orgUuid}/f/org_unit_type/`)
    .then(response => {
      return response.data
    })
  },

  addressTypes (orgUuid) {
    return Service.get(`/o/${orgUuid}/f/address_type/`)
    .then(response => {
      return response.data
    })
  },

  associationTypes (orgUuid) {
    return Service.get(`/o/${orgUuid}/f/association_type/`)
    .then(response => {
      return response.data
    })
  },

  engagementTypes (orgUuid) {
    return Service.get(`/o/${orgUuid}/f/engagement_type/`)
    .then(response => {
      return response.data
    })
  },

  jobFunctions (orgUuid) {
    return Service.get(`/o/${orgUuid}/f/job_function/`)
    .then(response => {
      return response.data
    })
  },

  roleTypes (orgUuid) {
    return Service.get(`/o/${orgUuid}/f/role_type/`)
    .then(response => {
      return response.data
    })
  }
}
