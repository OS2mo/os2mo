// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Router from "vue-router"
import employeeRouter from "@/views/employee/router"
import organisationRouter from "@/views/organisation/router"
import engagementRouter from "@/views/engagement/router"
import moduleRouters from "@/modules/router"

const MoBase = () => import("@/MoBase")
const Landing = () => import(/* webpackChunkName: "landingPage" */ "@/views/frontpage")
const PageNotFound = () => import("@/views/PageNotFound")

const GlobalRouter = [
  {
    path: "",
    name: "Landing",
    component: Landing,
  },
]

let BaseRouter = {
  path: "/",
  name: "Base",
  component: MoBase,
  children: [employeeRouter, organisationRouter, engagementRouter],
}

/**
 * Add all routers from modules
 */
BaseRouter.children = BaseRouter.children.concat(moduleRouters)

const PageNotFoundRouter = {
  path: "*",
  name: "PageNotFound",
  component: PageNotFound,
}

/**
 * IMPORTANT! Page not found is last otherwise it overwrites ALL other routes
 */
BaseRouter.children.push(PageNotFoundRouter)

const routes = GlobalRouter.concat([BaseRouter])

export default new Router({
  mode: "history",
  routes,
})
