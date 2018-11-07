import Vue from 'vue'
import Router from 'vue-router'
import employeeRouter from '@/employee/router'
import organisationRouter from '@/organisation/router'
import timeMachineRouter from '@/modules/timeMachine/router'

const LoginPage = () => import('@/login/LoginPage')
const Landing = () => import('@/landing/LandingPage')
const MoBase = () => import('@/MoBase')
const PageNotFound = () => import('@/components/PageNotFound')
const TheHelp = () => import('@/help/TheHelp')
const QueryList = () => import('@/modules/query/QueryList')

Vue.use(Router)

const GlobalRouter = [
  {
    path: '',
    name: 'Landing',
    component: Landing
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  }
]

const BaseRouter = {
  path: '/',
  name: 'Base',
  component: MoBase,
  children: [
    {
      path: '/hjaelp',
      name: 'Help',
      component: TheHelp
    },
    {
      path: '/forespoergsler',
      name: 'QueryList',
      component: QueryList
    }
  ]
}

const PageNotFoundRouter = {
  path: '*',
  name: 'PageNotFound',
  component: PageNotFound
}

BaseRouter.children.push(employeeRouter)
BaseRouter.children.push(organisationRouter)
BaseRouter.children.push(timeMachineRouter)
// important page not found is last otherwise it overwrites all other routes
BaseRouter.children.push(PageNotFoundRouter)

const routes = GlobalRouter.concat([BaseRouter])

export default new Router({
  mode: 'history',
  routes
})
