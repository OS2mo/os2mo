import Vue from 'vue'
export const EventBus = new Vue()

export const Events = {
  EMPLOYEE_CHANGED: 'employee-changed',
  ORGANISATION_CHANGED: 'organisation-changed',
  UPDATE_TREE_VIEW: 'update-tre-view',
  ORGANISATION_UNIT_CHANGED: 'organisation-unit-changed'
}
