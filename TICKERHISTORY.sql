SELECT *, cantidad * valor_actual 
 FROM iol_portfolio.ticker_history;
SELECT * FROM ticker_history;
#ALTER TABLE ticker_history ADD COLUMN cantidad DECIMAL(10, 2) AFTER simbolo;
CREATE DATABASE IF NOT EXISTS iol_portfolio;



SELECT simbolo, valor_actual, fecha
FROM ticker_history
WHERE simbolo = 'SPY'
ORDER BY fecha;

select simbolo, valor_actual , fecha
from ticker_history
where simbolo in ('VEA')
order by fecha;

select simbolo, valor_actual , fecha
from ticker_history
where simbolo in ('IEMG')
order by fecha;
