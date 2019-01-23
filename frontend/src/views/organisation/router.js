const Organisation = () => import(/* webpackChunkName: "organisation" */ './')
const OrganisationLandingPage = () => import(/* webpackChunkName: "organisation" */ './OrganisationLandingPage')
const OrganisationDetail = () => import(/* webpackChunkName: "organisation" */ './OrganisationDetail')

export default {
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
}
