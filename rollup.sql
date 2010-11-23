/*
    Within a single SQL statement, NOW() is guaranteed to evaluate to the same value for N invocations
    There is no such guarantee for a transaction or set of transactions, so we need to improvise
*/
SET @atomic_now = DATE_SUB(NOW(), INTERVAL 1 MINUTE);

-- before doing summary, capture meta info
INSERT IGNORE INTO _meta SELECT DISTINCT stat, func FROM raw;
INSERT INTO raw value(NOW(), 'SUM', 'stat_created', ROW_COUNT());

-- special case for SUM, only keep non-zero entries
-- keeps from tracking tons of empty stat_created entries through minute/hour/day tables
DELETE FROM raw WHERE func = 'SUM' AND data = 0;

-- minute summary grouping
SET @atomic_now = TRUNC_TO_MINUTE(@atomic_now);
START TRANSACTION;
REPLACE minute_summary SELECT TRUNC_TO_MINUTE(ts) t, TRUNC_TO_HOUR(ts) ts_h, TRUNC_TO_DAY(ts) ts_d, func, stat, SUM(data) FROM raw WHERE func = 'SUM' AND ts < @atomic_now GROUP BY t, stat;
REPLACE minute_summary SELECT TRUNC_TO_MINUTE(ts) t, TRUNC_TO_HOUR(ts) ts_h, TRUNC_TO_DAY(ts) ts_d, func, stat, AVG(data) FROM raw WHERE func = 'AVG' AND ts < @atomic_now GROUP BY t, stat;
REPLACE minute_summary SELECT TRUNC_TO_MINUTE(ts) t, TRUNC_TO_HOUR(ts) ts_h, TRUNC_TO_DAY(ts) ts_d, func, stat, MIN(data) FROM raw WHERE func = 'MIN' AND ts < @atomic_now GROUP BY t, stat;
REPLACE minute_summary SELECT TRUNC_TO_MINUTE(ts) t, TRUNC_TO_HOUR(ts) ts_h, TRUNC_TO_DAY(ts) ts_d, func, stat, MAX(data) FROM raw WHERE func = 'MAX' AND ts < @atomic_now GROUP BY t, stat;
-- clear out raw table so we don't double-count anything
DELETE FROM raw WHERE ts < @atomic_now;
COMMIT;

-- hour summary grouping
SET @atomic_now = TRUNC_TO_HOUR(@atomic_now);
START TRANSACTION;
REPLACE hour_summary SELECT ts_h, ts_d, func, stat, SUM(data) FROM minute_summary WHERE func = 'SUM' AND ts < @atomic_now GROUP BY ts_h, stat;
REPLACE hour_summary SELECT ts_h, ts_d, func, stat, AVG(data) FROM minute_summary WHERE func = 'AVG' AND ts < @atomic_now GROUP BY ts_h, stat;
REPLACE hour_summary SELECT ts_h, ts_d, func, stat, MIN(data) FROM minute_summary WHERE func = 'MIN' AND ts < @atomic_now GROUP BY ts_h, stat;
REPLACE hour_summary SELECT ts_h, ts_d, func, stat, MAX(data) FROM minute_summary WHERE func = 'MAX' AND ts < @atomic_now GROUP BY ts_h, stat;
COMMIT;

-- day summary grouping
SET @atomic_now = TRUNC_TO_DAY(@atomic_now);
START TRANSACTION;
REPLACE day_summary SELECT ts_d, func, stat, SUM(data) FROM hour_summary WHERE func = 'SUM' AND ts < @atomic_now GROUP BY ts_d, stat;
REPLACE day_summary SELECT ts_d, func, stat, AVG(data) FROM hour_summary WHERE func = 'AVG' AND ts < @atomic_now GROUP BY ts_d, stat;
REPLACE day_summary SELECT ts_d, func, stat, MIN(data) FROM hour_summary WHERE func = 'MIN' AND ts < @atomic_now GROUP BY ts_d, stat;
REPLACE day_summary SELECT ts_d, func, stat, MAX(data) FROM hour_summary WHERE func = 'MAX' AND ts < @atomic_now GROUP BY ts_d, stat;
COMMIT;

-- cleanup old entries in minute/hour table
-- remove minute-summary after 2 days, hour_summary after 31 (should be 7?)
DELETE FROM minute_summary WHERE ts < DATE_SUB(@atomic_now, INTERVAL 2 DAY);
DELETE FROM hour_summary WHERE ts < DATE_SUB(@atomic_now, INTERVAL 31 DAY);

-- disable for now, should just be run every once-in-a-while
-- no-op ALTER will rebuild InnoDB index
-- massive overkill? probably, but it's < 10k rows - should be awesomely fast
-- ALTER TABLE minute_summary ENGINE=InnoDB;
-- ALTER TABLE hour_summary ENGINE=InnoDB;
