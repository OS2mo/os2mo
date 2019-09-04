# mo-input-date 

A date picker component. 

## props 

- `valid-dates` ***Object*** (*optional*) `default: null` 

  Set valid date interval 

## data 

- `da` 

  Danish language translation for date picker 

**initial value:** `'da'` 

## computed properties 

- `initialValue` 

  The initially focused value. Use either the current value or the
  closest allowed value. 

   **dependencies:** `internalValue`, `internalValue`, `disabledDates` 

- `disabledDates` 

  Date interval to disable.
  We flip the validTo dates, as we want to disable anything outside of the range. 

   **dependencies:** `validDates`, `validDates`, `validDates`, `validDates`, `validDates`, `validDates` 


