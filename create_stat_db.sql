-- Stats DB setup stuff

-- TABLES --

-- no indexes for raw data table, and store in memory
CREATE TABLE `raw` (
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `func` enum('SUM','AVG','MIN','MAX') NOT NULL,
  `stat` varchar(100) NOT NULL,
  `data` float NOT NULL
) ENGINE=MEMORY DEFAULT CHARSET=ascii;

-- metadata table, uniq stat/func map
CREATE TABLE `_meta` (
  `stat` varchar(100) NOT NULL,
  `func` enum('SUM','AVG','MIN','MAX') NOT NULL,
  PRIMARY KEY (`stat`,`func`)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

-- 2 indexes on each of these:
-- one for rolling up to next-largest bucket
-- one for selecting stats by timerange
CREATE TABLE `minute_summary` (
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ts_h` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `ts_d` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `func` enum('SUM','AVG','MIN','MAX') NOT NULL,
  `stat` varchar(100) NOT NULL,
  `data` float NOT NULL,
  PRIMARY KEY (`stat`,`ts`),
  KEY `ts_h` (`ts_h`)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE `hour_summary` (
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ts_d` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `func` enum('SUM','AVG','MIN','MAX') NOT NULL,
  `stat` varchar(100) NOT NULL,
  `data` float NOT NULL,
  PRIMARY KEY (`stat`,`ts`),
  KEY `ts_d` (`ts_h`)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;

CREATE TABLE `day_summary` (
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `func` enum('SUM','AVG','MIN','MAX') NOT NULL,
  `stat` varchar(100) NOT NULL,
  `data` float NOT NULL,
  PRIMARY KEY (`stat`,`ts`),
  KEY `func` (`func`)
) ENGINE=InnoDB DEFAULT CHARSET=ascii;


-- FUNCTIONS --
-- UDFs to "round" timestamps to minute/hour/day resolution
DROP FUNCTION IF EXISTS TRUNC_TO_MINUTE;
CREATE FUNCTION TRUNC_TO_MINUTE(ts TIMESTAMP)
RETURNS TIMESTAMP
COMMENT 'Truncate timestamp to minute resolution'
DETERMINISTIC
CONTAINS SQL
SQL SECURITY INVOKER
RETURN FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(ts)/60)*60);

DROP FUNCTION IF EXISTS TRUNC_TO_HOUR;
CREATE FUNCTION TRUNC_TO_HOUR(ts TIMESTAMP)
RETURNS TIMESTAMP
COMMENT 'Truncate timestamp to hour resolution'
DETERMINISTIC
CONTAINS SQL
SQL SECURITY INVOKER
RETURN FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(ts)/3600)*3600);

DROP FUNCTION IF EXISTS TRUNC_TO_DAY;
CREATE FUNCTION TRUNC_TO_DAY(ts TIMESTAMP)
RETURNS TIMESTAMP
COMMENT 'Truncate timestamp to day resolution'
DETERMINISTIC
CONTAINS SQL
SQL SECURITY INVOKER
RETURN FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(ts)/86400)*86400);

-- sweet, done!


