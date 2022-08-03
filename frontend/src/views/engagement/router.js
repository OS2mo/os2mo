// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

const Engagement = () => import(/* webpackChunkName: "engagement" */ "./")
const EngagementDetail = () =>
  import(/* webpackChunkName: "engagement" */ "./EngagementDetail")

export default {
  path: "/engagement",
  name: "Engagement",
  component: Engagement,
  redirect: { name: "EngagementList" },

  children: [
    {
      path: ":uuid",
      name: "EngagementDetail",
      component: EngagementDetail,
    },
  ],
}
