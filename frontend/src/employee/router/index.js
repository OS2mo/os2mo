const Employee = () => import('../')
const MoEmployeeList = () => import('../MoEmployeeList')
const EmployeeDetail = () => import('../EmployeeDetail')

export default [
  {
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
]
