// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"
export const EventBus = new Vue()

export const Events = {
  EMPLOYEE_CHANGED: "employee-changed",
  ENGAGEMENT_CHANGED: "engagement-changed",
  ORGANISATION_CHANGED: "organisation-changed",
  UPDATE_TREE_VIEW: "update-tre-view",
  ORGANISATION_UNIT_CHANGED: "organisation-unit-changed",
}
