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
    }
  ]
}

const PageNotFoundRouter = {
  path: '*',
  name: 'PageNotFound',
  component: PageNotFound
}

BaseRouter.children.push(employeeRouter[0])
BaseRouter.children.push(organisationRouter[0])
BaseRouter.children.push(timeMachineRouter[0])
// important page not found is last otherwise it overwrites all other routes
BaseRouter.children.push(PageNotFoundRouter)

const routes = GlobalRouter.concat([BaseRouter])

export default new Router({
  mode: 'history',
  routes
})
