// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

const Employee = () => import(/* webpackChunkName: "employee" */ './')
const MoEmployeeList = () => import(/* webpackChunkName: "employee" */ './MoEmployeeList')
const EngagementDetail = () => import(/* webpackChunkName: "employee" */ './EngagementDetail')

export default {
  path: '/engagement',
  name: 'Engagement',
  component: Employee,
  redirect: { name: 'EngagementList' },

  children: [
    {
      path: 'liste',
      name: 'EngagementList',
      component: MoEmployeeList
    },
    {
      path: ':uuid',
      name: 'EngagementDetail',
      component: EngagementDetail
    }
  ]
}
