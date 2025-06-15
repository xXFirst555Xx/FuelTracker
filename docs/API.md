# OilPriceService Usage

`fetch_latest(session)` downloads the current fuel prices from the Thai-Oil-API and stores them in the `FuelPrice` table. It skips a day if prices already exist for that date.

Use `get_price(session, fuel_type, station, date)` to retrieve a `Decimal` price or `None` when no data is available.

If network errors occur, ensure your environment allows outbound HTTPS requests to `api.chnwt.dev`.
