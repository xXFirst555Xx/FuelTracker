# Maintenance Scheduler

Use the maintenance scheduler to track upcoming tasks for each vehicle.
Create `Maintenance` objects via `StorageService.add_maintenance` with a due odometer or date.
When a new fuel entry is added that reaches a task's due mileage or date, a notification will appear and overdue items are highlighted in the "Maintenance" panel.
