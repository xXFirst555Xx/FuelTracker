# Exporting Reports

The `Exporter` service can create monthly reports for all entries in a given
month. Two formats are supported:

* **CSV** via `Exporter.monthly_csv(month, year, path)`
* **PDF** via `Exporter.monthly_pdf(month, year, path)`

Both methods take the month and year numbers plus a destination `Path` object.
