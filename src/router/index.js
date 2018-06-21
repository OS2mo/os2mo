import Vue from 'vue'
import Router from 'vue-router'
const LoginPage = () => import('@/login/LoginPage')
const MoBase = () => import('@/MoBase')
const Organisation = () => import('@/organisation/Organisation')
const OrganisationLandingPage = () => import('@/organisation/OrganisationLandingPage')
const OrganisationDetail = () => import('@/organisation/OrganisationDetail')
const Employee = () => import('@/employee/Employee')
const MoEmployeeList = () => import('@/employee/MoEmployeeList')
const EmployeeDetail = () => import('@/employee/EmployeeDetail')
const PageNotFound = () => import('@/components/PageNotFound')
const TheHelp = () => import('@/help/TheHelp')
const MoTimeMachine = () => import('@/timeMachine/MoTimeMachine')

Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: LoginPage
    },
    {
      path: '',
      redirect: { name: 'Login' }
    },
    {
      path: '/',
      name: 'Base',
      component: MoBase,
      children: [
        {
          path: '/organisation',
          name: 'Organisation',
          component: Organisation,
          redirect: { name: 'OrganisationLandingPage' },
          meta: { requiresAuth: true },

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
          meta: { requiresAuth: true },

          children: [
            {
              path: 'liste',
              name: 'EmployeeList',
              component: MoEmployeeList
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
          component: TheHelp,
          meta: { requiresAuth: true }
        },
        {
          path: '/tidsmaskine',
          name: 'Timemachine',
          component: MoTimeMachine,
          meta: { requiresAuth: true }
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

router.beforeEach(function (to, from, next) {
  // console.log('Global -- beforeEach - fired')
  if (to.matched.some(record => record.meta.requiresAuth)) {
  // re-route
    if (to.path === '/') {
      next('/')
    } else if (to.path === '/error') {
      var err = new Error('My Error Message')
    }
      // pass the error to onError() callback.
    next(err)
  } else {
    next()
  }
})

// Global beforeResolve
router.beforeResolve(function (to, from, next) {
  // console.log('Global -- beforeResolve - fired.')
  next()
})

// GLobal AFTER hooks:
router.afterEach(function (to, from) {
  // This fires after each route is entered.
  // console.log(`Global -- afterEach - Just moved from '${from.path}' to '${to.path}'`)
})

// Register an Error Handler:
router.onError(function (err) {
  console.error('Handling this error', err.message)
})

// router.beforeEach((to, from, next) => {
//   if (to.matched.some(record => record.meta.requiresAuth)) {
//     // this route requires auth, check if logged in
//     // if not, redirect to login page.
//     if (!auth.loggedIn()) {
//       next({
//         path: '/login',
//         query: { redirect: to.fullPath }
//       })
//     } else {
//       next()
//     }
//   } else {
//     next() // make sure to always call next()!
//   }
// })

export default router
