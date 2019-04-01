# mo-confirm-checkbox 

A confirm checkbox component. 

## props 

- `entry-date` ***ArrayExpression*** (*optional*) 

  Defines a entry date. 

- `engagement-name` ***String*** (*optional*) 

  Defines a entry name. 

- `employee-name` ***String*** (*optional*) 

  Defines a entry name. 

- `entry-org-name` ***String*** (*optional*) 

  Defines a entry OrgName. 

## data 

- `confirm` 

  The confirm component value.
  Used to detect changes and restore the value. 

**initial value:** `false` 

## computed properties 

- `nameId` 

  Get default name. 
- `alertEngagementData` 

   **dependencies:** `engagementName`, `entryOrgName`, `entryDate` 

- `alertEmployeeData` 

   **dependencies:** `employeeName`, `entryDate` 


