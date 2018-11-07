const Organisation = () => import('./')
const OrganisationLandingPage = () => import('./OrganisationLandingPage')
const OrganisationDetail = () => import('./OrganisationDetail')

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
