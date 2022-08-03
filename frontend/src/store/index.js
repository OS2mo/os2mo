// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"
import Vuex from "vuex"
import conf from "./modules/conf"
import employee from "./modules/employee"
import engagement from "./modules/engagement"
import log from "./modules/log"
import organisation from "./modules/organisation"
import organisationUnit from "./modules/organisationUnit"
import facet from "./modules/facet"
import atDate from "./modules/atDate"
import { Employee } from "./actions/employee"
import { Engagement } from "./actions/engagement"
import { OrganisationUnit } from "./actions/organisationUnit"
import { Facet } from "./actions/facet"
import { Organisation } from "./actions/organisation"
import { Conf } from "./actions/conf"
import { AtDate } from "./actions/atDate"

Vue.use(Vuex)

export default new Vuex.Store({
  // strict: true,
  modules: {
    [AtDate.NAMESPACE]: atDate,
    [Conf.NAMESPACE]: conf,
    [Employee.NAMESPACE]: employee,
    [Engagement.NAMESPACE]: engagement,
    log: log,
    [Organisation.NAMESPACE]: organisation,
    [OrganisationUnit.NAMESPACE]: organisationUnit,
    [Facet.NAMESPACE]: facet,
  },
})
