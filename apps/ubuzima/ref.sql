-- phpMyAdmin SQL Dump
-- version 3.3.7deb5build0.10.10.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Aug 01, 2011 at 05:40 PM
-- Server version: 5.1.49
-- PHP Version: 5.3.3-1ubuntu9.5

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `ubuzima`
--

-- --------------------------------------------------------

--
-- Table structure for table `ubuzima_refusal`
--

CREATE TABLE IF NOT EXISTS `ubuzima_refusal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reporter_id` int(11) NOT NULL,
  `refid` longtext NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ubuzima_refusal_7dce1e39` (`reporter_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=9 ;

--
-- Dumping data for table `ubuzima_refusal`
--

INSERT INTO `ubuzima_refusal` (`id`, `reporter_id`, `refid`, `created`) VALUES
(1, 2560, '0788800511220711', '2011-08-01 14:30:35'),
(2, 2560, '0788800511220711', '2011-08-01 14:30:35'),
(3, 336, '078532001930071101', '2011-08-01 14:30:35'),
(4, 164, '07853200743107111', '2011-08-01 14:30:35'),
(5, 164, '07853200743107112', '2011-08-01 14:30:35'),
(6, 164, '07853200743107112', '2011-08-01 14:30:35'),
(7, 345, '0785156498310711', '2011-08-01 14:30:35'),
(8, 2560, '0788800511220711', '2011-08-01 14:30:35');
