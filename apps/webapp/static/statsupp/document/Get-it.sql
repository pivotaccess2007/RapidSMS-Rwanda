-- phpMyAdmin SQL Dump
-- version 3.4.5deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Feb 16, 2012 at 10:08 PM
-- Server version: 5.1.58
-- PHP Version: 5.3.6-13ubuntu3.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `Get-it`
--

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_425ae3c4` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `auth_message`
--

CREATE TABLE IF NOT EXISTS `auth_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_message_403f60f` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_1bb8f392` (`content_type_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=52 ;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add permission', 1, 'add_permission'),
(2, 'Can change permission', 1, 'change_permission'),
(3, 'Can delete permission', 1, 'delete_permission'),
(4, 'Can add group', 2, 'add_group'),
(5, 'Can change group', 2, 'change_group'),
(6, 'Can delete group', 2, 'delete_group'),
(7, 'Can add user', 3, 'add_user'),
(8, 'Can change user', 3, 'change_user'),
(9, 'Can delete user', 3, 'delete_user'),
(10, 'Can add message', 4, 'add_message'),
(11, 'Can change message', 4, 'change_message'),
(12, 'Can delete message', 4, 'delete_message'),
(13, 'Can add content type', 5, 'add_contenttype'),
(14, 'Can change content type', 5, 'change_contenttype'),
(15, 'Can delete content type', 5, 'delete_contenttype'),
(16, 'Can add session', 6, 'add_session'),
(17, 'Can change session', 6, 'change_session'),
(18, 'Can delete session', 6, 'delete_session'),
(19, 'Can add site', 7, 'add_site'),
(20, 'Can change site', 7, 'change_site'),
(21, 'Can delete site', 7, 'delete_site'),
(22, 'Can add log entry', 8, 'add_logentry'),
(23, 'Can change log entry', 8, 'change_logentry'),
(24, 'Can delete log entry', 8, 'delete_logentry'),
(25, 'Can add location', 9, 'add_location'),
(26, 'Can change location', 9, 'change_location'),
(27, 'Can delete location', 9, 'delete_location'),
(28, 'Can add cuisine', 10, 'add_cuisine'),
(29, 'Can change cuisine', 10, 'change_cuisine'),
(30, 'Can delete cuisine', 10, 'delete_cuisine'),
(31, 'Can add special_serv', 11, 'add_special_serv'),
(32, 'Can change special_serv', 11, 'change_special_serv'),
(33, 'Can delete special_serv', 11, 'delete_special_serv'),
(34, 'Can add food', 12, 'add_food'),
(35, 'Can change food', 12, 'change_food'),
(36, 'Can delete food', 12, 'delete_food'),
(37, 'Can add menu', 13, 'add_menu'),
(38, 'Can change menu', 13, 'change_menu'),
(39, 'Can delete menu', 13, 'delete_menu'),
(40, 'Can add resto', 14, 'add_resto'),
(41, 'Can change resto', 14, 'change_resto'),
(42, 'Can delete resto', 14, 'delete_resto'),
(43, 'Can add comment', 15, 'add_comment'),
(44, 'Can change comment', 15, 'change_comment'),
(45, 'Can delete comment', 15, 'delete_comment'),
(46, 'Can add comm_list', 16, 'add_comm_list'),
(47, 'Can change comm_list', 16, 'change_comm_list'),
(48, 'Can delete comm_list', 16, 'delete_comm_list'),
(49, 'Can add contact message', 17, 'add_contactmessage'),
(50, 'Can change contact message', 17, 'change_contactmessage'),
(51, 'Can delete contact message', 17, 'delete_contactmessage');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

CREATE TABLE IF NOT EXISTS `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `auth_user`
--

INSERT INTO `auth_user` (`id`, `username`, `first_name`, `last_name`, `email`, `password`, `is_staff`, `is_active`, `is_superuser`, `last_login`, `date_joined`) VALUES
(1, 'getit', '', '', 'getit@getit-app.com', 'sha1$54e2b$99fc015b47e782072368ae89dbb92c2b67b75a1c', 1, 1, 1, '2012-02-16 13:06:58', '2012-02-16 13:06:58');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

CREATE TABLE IF NOT EXISTS `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_403f60f` (`user_id`),
  KEY `auth_user_groups_425ae3c4` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

CREATE TABLE IF NOT EXISTS `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_403f60f` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_comment`
--

CREATE TABLE IF NOT EXISTS `demo_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_resto` varchar(50) NOT NULL,
  `name_user` varchar(50) NOT NULL,
  `text_comment` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_comm_list`
--

CREATE TABLE IF NOT EXISTS `demo_comm_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_resto` varchar(50) NOT NULL,
  `name_user` varchar(50) NOT NULL,
  `text_comment` longtext NOT NULL,
  `date_rec` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_contactmessage`
--

CREATE TABLE IF NOT EXISTS `demo_contactmessage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_sender` varchar(50) NOT NULL,
  `tel_sender` varchar(15) NOT NULL,
  `email` varchar(50) NOT NULL,
  `country_sender` varchar(30) NOT NULL,
  `subject` varchar(100) NOT NULL,
  `message` longtext NOT NULL,
  `date_rec` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_cuisine`
--

CREATE TABLE IF NOT EXISTS `demo_cuisine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cuisine_type` varchar(17) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_food`
--

CREATE TABLE IF NOT EXISTS `demo_food` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `food_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_location`
--

CREATE TABLE IF NOT EXISTS `demo_location` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `province_name` varchar(15) NOT NULL,
  `district_name` varchar(15) NOT NULL,
  `sector_name` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_menu`
--

CREATE TABLE IF NOT EXISTS `demo_menu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `menu_acc` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_menu_food_acc_menu`
--

CREATE TABLE IF NOT EXISTS `demo_menu_food_acc_menu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `menu_id` int(11) NOT NULL,
  `food_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `menu_id` (`menu_id`,`food_id`),
  KEY `demo_menu_food_acc_menu_143efa3` (`menu_id`),
  KEY `demo_menu_food_acc_menu_3d259cc` (`food_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_resto`
--

CREATE TABLE IF NOT EXISTS `demo_resto` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `resto_name` varchar(50) NOT NULL,
  `tel_no` varchar(17) NOT NULL,
  `place_name_id` int(11) NOT NULL,
  `range_price` varchar(50) NOT NULL,
  `id_menu_id` int(11) NOT NULL,
  `other_specif` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `demo_resto_6ba73327` (`place_name_id`),
  KEY `demo_resto_32faeef0` (`id_menu_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_resto_cuisine_type`
--

CREATE TABLE IF NOT EXISTS `demo_resto_cuisine_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `resto_id` int(11) NOT NULL,
  `cuisine_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `resto_id` (`resto_id`,`cuisine_id`),
  KEY `demo_resto_cuisine_type_5db11c94` (`resto_id`),
  KEY `demo_resto_cuisine_type_76bd0a31` (`cuisine_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_resto_special_services`
--

CREATE TABLE IF NOT EXISTS `demo_resto_special_services` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `resto_id` int(11) NOT NULL,
  `special_serv_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `resto_id` (`resto_id`,`special_serv_id`),
  KEY `demo_resto_special_services_5db11c94` (`resto_id`),
  KEY `demo_resto_special_services_5e630830` (`special_serv_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `demo_special_serv`
--

CREATE TABLE IF NOT EXISTS `demo_special_serv` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_service` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_403f60f` (`user_id`),
  KEY `django_admin_log_1bb8f392` (`content_type_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=18 ;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `name`, `app_label`, `model`) VALUES
(1, 'permission', 'auth', 'permission'),
(2, 'group', 'auth', 'group'),
(3, 'user', 'auth', 'user'),
(4, 'message', 'auth', 'message'),
(5, 'content type', 'contenttypes', 'contenttype'),
(6, 'session', 'sessions', 'session'),
(7, 'site', 'sites', 'site'),
(8, 'log entry', 'admin', 'logentry'),
(9, 'location', 'demo', 'location'),
(10, 'cuisine', 'demo', 'cuisine'),
(11, 'special_serv', 'demo', 'special_serv'),
(12, 'food', 'demo', 'food'),
(13, 'menu', 'demo', 'menu'),
(14, 'resto', 'demo', 'resto'),
(15, 'comment', 'demo', 'comment'),
(16, 'comm_list', 'demo', 'comm_list'),
(17, 'contact message', 'demo', 'contactmessage');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `django_site`
--

CREATE TABLE IF NOT EXISTS `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `django_site`
--

INSERT INTO `django_site` (`id`, `domain`, `name`) VALUES
(1, 'example.com', 'example.com');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
