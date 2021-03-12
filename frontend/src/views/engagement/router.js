// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

const Engagement = () => import(/* webpackChunkName: "engagement" */ './')
const MoEmployeeList = () => import(/* webpackChunkName: "engagement" */ './MoEmployeeList')
const EngagementDetail = () => import(/* webpackChunkName: "engagement" */ './EngagementDetail')

export default {
  path: '/engagement',
  name: 'Engagement',
  component: Engagement,
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
