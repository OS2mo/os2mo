# mo-date-picker-range 

A date picker range component. 

## props 

- `value` ***Object*** (*optional*) 

  Create two-way data bindings with the component. 

- `initially-hidden` ***Boolean*** (*optional*) 

  This boolean property hides the date. 

- `disable-to-date` ***Boolean*** (*optional*) 

  This boolean property disable the to date. 

- `disabled-dates` ***Object*** (*optional*) 

  Defines disable dates. 

## data 

- `validFrom` 

  The validFrom, validTo, hidden component value.
  Used to detect changes and restore the value. 

**initial value:** `null` 

- `validTo` 

**initial value:** `null` 

- `hidden` 

**initial value:** `false` 

## computed properties 

- `validStartDateRange` 

  Disable the dates before the choosen start date. 

   **dependencies:** `disabledDates`, `disabledDates`, `disabledDates`, `disabledDates`, `disabledDates`, `disabledDates`, `validTo`, `validTo`, `validTo` 

- `validEndDateRange` 

  Disable the dates after the choosen end date. 

   **dependencies:** `disabledDates`, `disabledDates`, `disabledDates`, `disabledDates`, `disabledDates`, `disabledDates`, `validFrom`, `validFrom`, `validFrom` 


## events 

- `input` 

## methods 

- `updateDate()` 

  Update the from and to date. 

