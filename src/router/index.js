import Vue from 'vue'
import Router from 'vue-router'
import MoBase from '@/MoBase'
import HelloWorld from '@/components/HelloWorld'
import LoginPage from '@/login/LoginPage'
import Organisation from '@/organisation/Organisation'
import OrganisationLandingPage from '@/organisation/OrganisationLandingPage'
import OrganisationDetail from '@/organisation/OrganisationDetail'
import Employee from '@/employee/Employee'
import EmployeeList from '@/employee/EmployeeList'
import EmployeeDetail from '@/employee/EmployeeDetail'
import PageNotFound from '@/components/PageNotFound'
import TheHelp from '@/help/TheHelp'
import TimeMachine from '@/timeMachine/TimeMachine'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: LoginPage
    },
    {
      path: '/',
      name: 'Base',
      component: MoBase,
      redirect: { name: 'Home' },
      children: [
        {
          path: '',
          name: 'Home',
          component: HelloWorld
        },
        {
          path: '/organisation',
          name: 'Organisation',
          component: Organisation,
          redirect: { name: 'OrganisationLandingPage' },

          children: [
            {
              path: '',
              name: 'OrganisationLandingPage',
              component: OrganisationLandingPage
            },
            {
              path: ':uuid',
              name: 'OrganisationDetail',
              component: OrganisationDetail
            }
          ]
        },
        {
          path: '/medarbejder',
          name: 'Employee',
          component: Employee,
          redirect: { name: 'EmployeeList' },

          children: [
            {
              path: 'liste',
              name: 'EmployeeList',
              component: EmployeeList
            },
            {
              path: ':uuid',
              name: 'EmployeeDetail',
              component: EmployeeDetail
            }
          ]
        },
        {
          path: '/hjaelp',
          name: 'Help',
          component: TheHelp
        },
        {
          path: '/tidsmaskine',
          name: 'Timemachine',
          component: TimeMachine
        },
        {
          path: '*',
          name: 'PageNotFound',
          component: PageNotFound
        }
      ]
    }
  ]
})
