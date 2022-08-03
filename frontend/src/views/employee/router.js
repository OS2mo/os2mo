// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

const Employee = () => import(/* webpackChunkName: "employee" */ "./")
const MoEmployeeList = () =>
  import(/* webpackChunkName: "employee" */ "./MoEmployeeList")
const EmployeeDetail = () =>
  import(/* webpackChunkName: "employee" */ "./EmployeeDetail")

export default {
  path: "/medarbejder",
  name: "Employee",
  component: Employee,
  redirect: { name: "EmployeeList" },

  children: [
    {
      path: "liste",
      name: "EmployeeList",
      component: MoEmployeeList,
    },
    {
      path: ":uuid",
      name: "EmployeeDetail",
      component: EmployeeDetail,
    },
  ],
}
