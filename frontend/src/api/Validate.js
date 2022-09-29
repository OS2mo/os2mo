// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import axios from "axios"
import keycloak from "@/main"

/**
 * Defines the base url and headers for validate http calls
 */

const Validate = axios.create({
  baseURL: "/service/validate",
  headers: {
    "X-Requested-With": "XMLHttpRequest",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, PUT",
  },
})

Validate.interceptors.request.use(function (config) {
  config.headers["Authorization"] = "Bearer " + keycloak.token
  return config
})

const createErrorPayload = (err) => {
  return {
    valid: false,
    data: err.response.data,
  }
}

export default {
  cpr(cpr, orgUuid) {
    const payload = {
      cpr_no: cpr,
      org: {
        uuid: orgUuid,
      },
    }
    return Validate.post("/cpr/", payload).then(
      (result) => {
        return true
      },
      (err) => {
        return createErrorPayload(err)
      }
    )
  },

  orgUnit(orgUnitUuid, validity) {
    const payload = {
      org_unit: {
        uuid: orgUnitUuid,
      },
      validity: validity,
    }
    return Validate.post("/org-unit/", payload).then(
      (result) => {
        return true
      },
      (err) => {
        return createErrorPayload(err)
      }
    )
  },

  employee(employee, validity) {
    const payload = {
      person: employee,
      validity: validity,
    }
    return Validate.post("/employee/", payload).then(
      (result) => {
        return true
      },
      (err) => {
        return createErrorPayload(err)
      }
    )
  },

  activeEngagements(employee, validity) {
    const payload = {
      person: employee,
      validity: validity,
    }
    return Validate.post("/active-engagements/", payload).then(
      (result) => {
        return true
      },
      (err) => {
        return createErrorPayload(err)
      }
    )
  },

  candidateParentOrgUnit(orgUnit, parent, validity) {
    const payload = {
      org_unit: orgUnit,
      parent: parent,
      validity: validity,
    }
    return Validate.post("/candidate-parent-org-unit/", payload).then(
      (result) => {
        return true
      },
      (err) => {
        return createErrorPayload(err)
      }
    )
  },

  address(value, addressType) {
    const payload = {
      value: value,
      address_type: addressType,
    }
    return Validate.post("/address/", payload).then(
      (result) => {
        return true
      },
      (err) => {
        return createErrorPayload(err)
      }
    )
  },

  existingEngagementAssociations(orgUnit, validity, associationUuid) {
    const payload = {
      org_unit: orgUnit,
      validity: validity,
      uuid: associationUuid,
    }
    return Validate.post("/existing-associations/", payload).then(
      (result) => {
        return true
      },
      (err) => {
        return createErrorPayload(err)
      }
    )
  },
}
