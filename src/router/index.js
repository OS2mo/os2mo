import Vue from 'vue'
import Router from 'vue-router'
import MoBase from '@/MoBase'
import HelloWorld from '@/components/HelloWorld'
import LoginPage from '@/login/LoginPage'
import Organisation from '@/organisation/Organisation'
import OrganisationLandingPage from '@/organisation/OrganisationLandingPage'
import OrganisationDetail from '@/organisation/OrganisationDetail'
import OrganisationDetailContact from '@/organisation/OrganisationDetailContact'
import OrganisationDetailEngagement from '@/organisation/OrganisationDetailEngagement'
import OrganisationDetailLocation from '@/organisation/OrganisationDetailLocation'
import OrganisationDetailUnit from '@/organisation/OrganisationDetailUnit'
import Employee from '@/employee/Employee'
import EmployeeList from '@/employee/EmployeeList'
import EmployeeDetail from '@/employee/EmployeeDetail'
import EmployeeDetailContact from '@/employee/EmployeeDetailContact'
import EmployeeDetailEngagement from '@/employee/EmployeeDetailEngagement'
import EmployeeDetailIt from '@/employee/EmployeeDetailIt'
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
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginPage
    },
    {
      path: '/',
      name: 'base',
      component: MoBase,
      redirect: { name: 'home' },
      children: [
        {
          path: '',
          name: 'home',
          component: HelloWorld
        },
        {
          path: '/organisation',
          name: 'organisation',
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
                },
                {
                  path: 'engagement',
                  name: 'OrganisationDetailEngagement',
                  component: OrganisationDetailEngagement
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
                },
                {
                  path: 'it',
                  name: 'EmployeeDetailIt',
                  component: EmployeeDetailIt
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
    }
  ]
})
