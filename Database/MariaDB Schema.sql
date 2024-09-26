-- --------------------------------------------------------
-- Host:                         localhost
-- Server version:               10.4.11-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             10.3.0.5771
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for CubCar
DROP DATABASE IF EXISTS `CubCar`;
CREATE DATABASE IF NOT EXISTS `cubcar` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `CubCar`;

-- Dumping structure for table CubCar.backlognotes
DROP TABLE IF EXISTS `backlognotes`;
CREATE TABLE IF NOT EXISTS `backlognotes` (
  `IssueID` int(11) NOT NULL AUTO_INCREMENT,
  `BacklogEnhanceBug` varchar(255) DEFAULT NULL,
  `BacklogDescription` varchar(1000) DEFAULT NULL,
  `BacklogDetails` varchar(1000) DEFAULT NULL,
  `BacklogResolved` bit(1) DEFAULT NULL,
  `BacklogResolvedDate` datetime DEFAULT NULL,
  PRIMARY KEY (`IssueID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for view CubCar.globaltracklaneslist
DROP VIEW IF EXISTS `globaltracklaneslist`;
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `globaltracklaneslist` (
	`TrackID` INT(11) NULL,
	`TrackName` VARCHAR(100) NULL COLLATE 'utf8_general_ci',
	`TrackNumber` INT(11) NULL,
	`Lane` INT(11) NULL
) ENGINE=MyISAM;

-- Dumping structure for table CubCar.packnames
DROP TABLE IF EXISTS `packnames`;
CREATE TABLE IF NOT EXISTS `packnames` (
  `ID` int(11) NOT NULL DEFAULT 0,
  `PackName` varchar(100) DEFAULT '0',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.pitcrewmembers
DROP TABLE IF EXISTS `pitcrewmembers`;
CREATE TABLE IF NOT EXISTS `pitcrewmembers` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PitCrewMemberName` varchar(255) NOT NULL DEFAULT '0',
  `PitCrewMemberGroup` int(11) NOT NULL DEFAULT 0,
  `PitCrewMemberActive` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.raceclasses
DROP TABLE IF EXISTS `raceclasses`;
CREATE TABLE IF NOT EXISTS `raceclasses` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Class` varchar(100) NOT NULL DEFAULT '0',
  `ClassDescription` varchar(255) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.raceresults
DROP TABLE IF EXISTS `raceresults`;
CREATE TABLE IF NOT EXISTS `raceresults` (
  `RowKey` int(11) NOT NULL AUTO_INCREMENT,
  `RacerID` int(11) DEFAULT NULL COMMENT 'FK to RacerInfo PK',
  `RaceCounter` int(11) DEFAULT NULL COMMENT 'Count of Races Run',
  `RaceCarNumber` int(11) DEFAULT NULL COMMENT 'Optional Race car # from RacerInfo',
  `Unit` int(11) DEFAULT NULL COMMENT 'What timer provided this information',
  `Heat` int(11) DEFAULT NULL COMMENT 'What heat are you in',
  `Lane` int(11) DEFAULT NULL COMMENT 'Which lane on the track was the car on',
  `CarName` varchar(255) DEFAULT NULL COMMENT 'From RacerInfo what is the car name',
  `Pack` varchar(120) DEFAULT NULL COMMENT 'What pack is this racer from',
  `RaceTime` time(6) DEFAULT NULL COMMENT 'How long was the race?',
  `Placing` int(11) DEFAULT NULL COMMENT 'What place did the racer come in?',
  `Status` varchar(10) DEFAULT NULL COMMENT 'What is the status of this race? ',
  `RacerRFID` varchar(50) DEFAULT NULL COMMENT 'RFID of the car from racerInfo',
  `RacerFirstName` varchar(60) DEFAULT NULL COMMENT 'First Name from RacerInfo',
  `RacerLastName` varchar(60) DEFAULT NULL COMMENT 'Last Name from RacerInfo',
  `RaceDate` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`RowKey`)
) ENGINE=InnoDB AUTO_INCREMENT=325 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.racerinfo
DROP TABLE IF EXISTS `racerinfo`;
CREATE TABLE IF NOT EXISTS `racerinfo` (
  `RacerID` int(11) NOT NULL AUTO_INCREMENT,
  `RacerFirstName` varchar(50) DEFAULT NULL,
  `RacerLastName` varchar(50) DEFAULT NULL,
  `RacerPack` int(11) DEFAULT NULL,
  `RacerRFID` varchar(60) DEFAULT NULL,
  `RacerCarName` varchar(255) DEFAULT NULL,
  `RacerCarNumber` int(11) DEFAULT NULL,
  `RacerInclude` int(11) DEFAULT 1 COMMENT 'MS-Access does not support BIT Datatype',
  `RacerCarChecked` int(11) DEFAULT NULL COMMENT 'MS-Access does not support BIT datatype',
  `RacerPitCrewName` int(11) DEFAULT NULL,
  `RacerCarWeight` decimal(10,2) DEFAULT NULL,
  `RacerCarClass` int(11) DEFAULT NULL,
  PRIMARY KEY (`RacerID`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.racescheduledetails
DROP TABLE IF EXISTS `racescheduledetails`;
CREATE TABLE IF NOT EXISTS `racescheduledetails` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `RaceNumber` int(11) NOT NULL DEFAULT 0,
  `LaneID` int(11) NOT NULL DEFAULT 0,
  `CarID` int(11) NOT NULL DEFAULT 0,
  `CarRFID` varchar(60) NOT NULL DEFAULT '0',
  `Racepoints` int(11) NOT NULL DEFAULT 0,
  `RacerRace` int(11) NOT NULL DEFAULT 0,
  `WeightedPoints` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.racescheduleheader
DROP TABLE IF EXISTS `racescheduleheader`;
CREATE TABLE IF NOT EXISTS `racescheduleheader` (
  `RaceNumber` int(11) NOT NULL AUTO_INCREMENT,
  `RaceRound` int(11) DEFAULT NULL,
  `TrackID` int(11) DEFAULT NULL,
  `RaceStatus` int(11) DEFAULT NULL,
  PRIMARY KEY (`RaceNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.refracestatus
DROP TABLE IF EXISTS `refracestatus`;
CREATE TABLE IF NOT EXISTS `refracestatus` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.switchboard items
DROP TABLE IF EXISTS `switchboard items`;
CREATE TABLE IF NOT EXISTS `switchboard items` (
  `SwitchboardID` int(11) DEFAULT NULL,
  `ItemNumber` int(11) DEFAULT NULL,
  `ItemText` varchar(255) DEFAULT NULL,
  `Command` int(11) DEFAULT NULL,
  `Argument` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.tallytable
DROP TABLE IF EXISTS `tallytable`;
CREATE TABLE IF NOT EXISTS `tallytable` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Tally` int(11) DEFAULT 0,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.trackheat
DROP TABLE IF EXISTS `trackheat`;
CREATE TABLE IF NOT EXISTS `trackheat` (
  `TrackID` int(11) DEFAULT NULL,
  `Heat` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table CubCar.trackinformation
DROP TABLE IF EXISTS `trackinformation`;
CREATE TABLE IF NOT EXISTS `trackinformation` (
  `TrackID` int(11) DEFAULT NULL,
  `TrackName` varchar(100) DEFAULT NULL,
  `TrackNumber` int(11) DEFAULT NULL,
  `TrackLanes` int(11) DEFAULT NULL,
  `TrackInclude` bit(1) DEFAULT NULL,
  `TrackDigital` bit(1) DEFAULT NULL,
  `TrackControllerIP` varchar(25) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for procedure CubCar.UpdateRFID
DROP PROCEDURE IF EXISTS `UpdateRFID`;
DELIMITER //
CREATE PROCEDURE `UpdateRFID`(
	IN `OldRFID` VARCHAR(60),
	IN `NewRFID` VARCHAR(60)
)
    COMMENT 'In the event that an RFID sticker is lost, assign a new one and update related tables. '
BEGIN
UPDATE racerinfo 
	Set RFID = NewRFID
WHERE RFID = OldRFID ;

UPDATE raceresults
	SET RFID = NewRFID
WHERE RFID = OldRFID ;


END//
DELIMITER ;

-- Dumping structure for view CubCar.globaltracklaneslist
DROP VIEW IF EXISTS `globaltracklaneslist`;
-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `globaltracklaneslist`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY INVOKER VIEW `globaltracklaneslist` AS SELECT 
TI.TrackID,
TI.TrackName,
TI.TrackNumber,		
TT.Tally AS Lane
 FROM trackinformation TI
 INNER JOIN tallytable TT
 ON TT.Tally <= TI.TrackLanes
 ORDER BY TI.TrackNumber, TI.TrackName, TT.Tally ;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
