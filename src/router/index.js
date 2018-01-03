import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import LoginPage from '@/login/LoginPage'
import Organisation from '@/organisation/Organisation'
import OrganisationDetail from '@/organisation/OrganisationDetail'
import OrganisationDetailUnit from '@/organisation/OrganisationDetailUnit'
import OrganisationDetailLocation from '@/organisation/OrganisationDetailLocation'
import OrganisationDetailContact from '@/organisation/OrganisationDetailContact'
import Employee from '@/employee/Employee'
import EmployeeList from '@/employee/EmployeeList'
import EmployeeDetail from '@/employee/EmployeeDetail'
import EmployeeDetailEngagement from '@/employee/EmployeeDetailEngagement'
import EmployeeDetailContact from '@/employee/EmployeeDetailContact'
import EmployeeCreate from '@/employee/EmployeeCreate'
import EmployeeLeave from '@/employee/EmployeeLeave'
import EmployeeMove from '@/employee/EmployeeMove'
import EmployeeMoveMany from '@/employee/EmployeeMoveMany'
import EmployeeEnd from '@/employee/EmployeeEnd'
import PageNotFound from '@/components/PageNotFound'
import TheHelp from '@/help/TheHelp'
import TimeMachine from '@/timeMachine/TimeMachine'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'home',
      component: HelloWorld
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage
    },
    {
      path: '/organisation',
      name: 'organisation',
      component: Organisation,

      children: [
        {
          path: ':uuid',
          name: 'OrganisationDetail',
          component: OrganisationDetail,
          redirect: { name: 'OrganisationDetailUnit' },

          children: [
            {
              path: 'enhed',
              name: 'OrganisationDetailUnit',
              component: OrganisationDetailUnit
            },
            {
              path: 'lokation',
              name: 'OrganisationDetailLocation',
              component: OrganisationDetailLocation
            },
            {
              path: 'kontakt-kanal',
              name: 'OrganisationDetailContact',
              component: OrganisationDetailContact
            }
          ]
        }
      ]
    },
    {
      path: '/medarbejder',
      name: 'employee',
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
          component: EmployeeDetail,
          redirect: { name: 'EmployeeDetailEngagement' },

          children: [
            {
              path: 'engagement',
              name: 'EmployeeDetailEngagement',
              component: EmployeeDetailEngagement
            },
            {
              path: 'kontakt',
              name: 'EmployeeDetailContact',
              component: EmployeeDetailContact
            }
          ]
        },
        {
          path: 'ny-medarbejder',
          name: 'EmployeeCreate',
          component: EmployeeCreate
        },
        {
          path: 'meld-orlov',
          name: 'EmployeeLeave',
          component: EmployeeLeave
        },
        {
          path: 'flyt-engagement',
          name: 'EmployeeMove',
          component: EmployeeMove
        },
        {
          path: 'flyt-mange-engagementer',
          name: 'EmployeeMoveMany',
          component: EmployeeMoveMany
        },
        {
          path: 'afslut-medarbejder',
          name: 'EmployeeEnd',
          component: EmployeeEnd
        }
      ]
    },
    {
      path: '/hjaelp',
      name: 'help',
      component: TheHelp
    },
    {
      path: '/tidsmaskine',
      name: 'timemachine',
      component: TimeMachine
    },
    {
      path: '*',
      name: 'PageNotFound',
      component: PageNotFound
    }
  ]
})
