# mo-date-picker 

A date picker component. 

## props 

- `value` ***ArrayExpression*** (*optional*) 

  Create two-way data bindings with the component. 

- `required` ***Boolean*** (*optional*) 

  This boolean property requires a date. 

- `no-label` ***Boolean*** (*optional*) 

  This boolean property hides the label. 

- `label` ***String*** (*optional*) `default: 'Dato'` 

  Defines the label. 

- `valid-dates` ***Object*** (*optional*) 

  Defines valid dates. 

- `disabled` ***Boolean*** (*optional*) 

  This boolean disable the dates. 

## data 

- `selected` 

  The selected, dateString, da component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `dateString` 

**initial value:** `null` 

- `da` 

**initial value:** `'da'` 

## computed properties 

- `nameId` 

  Get name `date-picker`. 

   **dependencies:** `_uid` 

- `disabledDates` 

  Disable the choosen from date and the to date. 

   **dependencies:** `validDates`, `validDates`, `validDates`, `validDates`, `validDates`, `validDates` 


