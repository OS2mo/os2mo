const Organisation = () => import(/* webpackChunkName: "organisation" */ './')
const OrganisationLandingPage = () => import(/* webpackChunkName: "organisationLandingPage" */ './OrganisationLandingPage')
const OrganisationDetail = () => import(/* webpackChunkName: "organisationDetail" */ './OrganisationDetail')

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
