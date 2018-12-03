const Employee = () => import(/* webpackChunkName: "employee" */ './')
const MoEmployeeList = () => import(/* webpackChunkName: "employeeList" */ './MoEmployeeList')
const EmployeeDetail = () => import(/* webpackChunkName: "employeeDetail" */ './EmployeeDetail')

export default {
  path: '/medarbejder',
  name: 'Employee',
  component: Employee,
  redirect: { name: 'EmployeeList' },

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
}
