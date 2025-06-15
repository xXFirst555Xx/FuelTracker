# Monthly Budget

Each vehicle can have a monthly fuel budget. Use
`StorageService.set_budget(vehicle_id, amount)` to store the value. When the
sum of all entries for the current month exceeds the budget a warning dialog and
a Windows toast notification will be shown.
