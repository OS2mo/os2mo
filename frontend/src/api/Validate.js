import axios from 'axios'

/**
 * Defines the base url and headers for validate http calls
 */

const Validate = axios.create({
  baseURL: '/service/validate',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, PUT'
  }
})

const createErrorPayload = err => {
  return {
    valid: false,
    data: err.response.data.error_key
  }
}

export default {
  cpr (cpr, org) {
    const payload = {
      'cpr_no': cpr,
      'org': {
        'uuid': org[0]
      }
    }
    return Validate
      .post('/cpr/', payload).then(result => {
        return true
      }, err => {
        return createErrorPayload(err)
      })
  },

  orgUnit (orgUnit, validity) {
    const payload = {
      'org_unit': {
        'uuid': orgUnit
      },
      'validity': validity
    }
    return Validate
      .post('/org-unit/', payload).then(result => {
        return true
      }, err => {
        return createErrorPayload(err)
      })
  },

  employee (employee, validity) {
    const payload = {
      'person': employee,
      'validity': validity
    }
    return Validate
      .post('/employee/', payload).then(result => {
        return true
      }, err => {
        return createErrorPayload(err)
      })
  },

  activeEngagements (employee, validity) {
    const payload = {
      'person': employee,
      'validity': validity
    }
    return Validate
      .post('/active-engagements/', payload).then(result => {
        return true
      }, err => {
        return createErrorPayload(err)
      })
  },

  candidateParentOrgUnit (orgUnit, parent, validity, associationUuid) {
    const payload = {
      'org_unit': orgUnit,
      'parent': parent,
      'validity': validity
    }
    return Validate
      .post('/candidate-parent-org-unit/', payload).then(result => {
        return true
      }, err => {
        return createErrorPayload(err)
      })
  }
}
