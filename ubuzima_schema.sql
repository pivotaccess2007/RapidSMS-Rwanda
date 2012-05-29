BEGIN;CREATE TABLE `ubuzima_fieldcategory` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(30) NOT NULL UNIQUE
)
;
CREATE TABLE `ubuzima_reporttype` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(30) NOT NULL UNIQUE
)
;
CREATE TABLE `ubuzima_fieldtype` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `key` varchar(32) NOT NULL UNIQUE,
    `description` longtext NOT NULL,
    `category_id` integer NOT NULL,
    `has_value` bool NOT NULL
)
;
ALTER TABLE `ubuzima_fieldtype` ADD CONSTRAINT `category_id_refs_id_64f88917` FOREIGN KEY (`category_id`) REFERENCES `ubuzima_fieldcategory` (`id`);
CREATE TABLE `ubuzima_patient` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `location_id` integer NOT NULL,
    `national_id` varchar(20) NOT NULL UNIQUE,
    `telephone` varchar(13)
)
;
ALTER TABLE `ubuzima_patient` ADD CONSTRAINT `location_id_refs_id_256a8fa3` FOREIGN KEY (`location_id`) REFERENCES `locations_location` (`id`);
CREATE TABLE `ubuzima_field` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `type_id` integer NOT NULL,
    `value` numeric(10, 5)
)
;
ALTER TABLE `ubuzima_field` ADD CONSTRAINT `type_id_refs_id_304b28c1` FOREIGN KEY (`type_id`) REFERENCES `ubuzima_fieldtype` (`id`);
CREATE TABLE `ubuzima_report_fields` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `report_id` integer NOT NULL,
    `field_id` integer NOT NULL,
    UNIQUE (`report_id`, `field_id`)
)
;
ALTER TABLE `ubuzima_report_fields` ADD CONSTRAINT `field_id_refs_id_5527c4cf` FOREIGN KEY (`field_id`) REFERENCES `ubuzima_field` (`id`);
CREATE TABLE `ubuzima_report` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `reporter_id` integer NOT NULL,
    `location_id` integer NOT NULL,
    `village` varchar(255),
    `patient_id` integer NOT NULL,
    `type_id` integer NOT NULL,
    `date_string` varchar(10),
    `date` date,
    `created` datetime NOT NULL
)
;
ALTER TABLE `ubuzima_report` ADD CONSTRAINT `location_id_refs_id_4632c383` FOREIGN KEY (`location_id`) REFERENCES `locations_location` (`id`);
ALTER TABLE `ubuzima_report` ADD CONSTRAINT `type_id_refs_id_a1f4b93` FOREIGN KEY (`type_id`) REFERENCES `ubuzima_reporttype` (`id`);
ALTER TABLE `ubuzima_report` ADD CONSTRAINT `patient_id_refs_id_4318cf97` FOREIGN KEY (`patient_id`) REFERENCES `ubuzima_patient` (`id`);
ALTER TABLE `ubuzima_report` ADD CONSTRAINT `reporter_id_refs_id_69ce47d5` FOREIGN KEY (`reporter_id`) REFERENCES `reporters_reporter` (`id`);
ALTER TABLE `ubuzima_report_fields` ADD CONSTRAINT `report_id_refs_id_299c860c` FOREIGN KEY (`report_id`) REFERENCES `ubuzima_report` (`id`);
CREATE TABLE `ubuzima_triggeredtext_triggers` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `triggeredtext_id` integer NOT NULL,
    `fieldtype_id` integer NOT NULL,
    UNIQUE (`triggeredtext_id`, `fieldtype_id`)
)
;
ALTER TABLE `ubuzima_triggeredtext_triggers` ADD CONSTRAINT `fieldtype_id_refs_id_375fd63c` FOREIGN KEY (`fieldtype_id`) REFERENCES `ubuzima_fieldtype` (`id`);
CREATE TABLE `ubuzima_triggeredtext` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(128) NOT NULL,
    `destination` varchar(3) NOT NULL,
    `description` longtext NOT NULL,
    `message_kw` varchar(160) NOT NULL,
    `message_fr` varchar(160) NOT NULL,
    `message_en` varchar(160) NOT NULL,
    `active` bool NOT NULL
)
;
ALTER TABLE `ubuzima_triggeredtext_triggers` ADD CONSTRAINT `triggeredtext_id_refs_id_7068e222` FOREIGN KEY (`triggeredtext_id`) REFERENCES `ubuzima_triggeredtext` (`id`);
CREATE TABLE `ubuzima_remindertype` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(255) NOT NULL,
    `message_kw` varchar(160) NOT NULL,
    `message_fr` varchar(160) NOT NULL,
    `message_en` varchar(160) NOT NULL
)
;
CREATE TABLE `ubuzima_reminder` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `reporter_id` integer NOT NULL,
    `report_id` integer,
    `type_id` integer NOT NULL,
    `date` datetime NOT NULL
)
;
ALTER TABLE `ubuzima_reminder` ADD CONSTRAINT `report_id_refs_id_562ce3db` FOREIGN KEY (`report_id`) REFERENCES `ubuzima_report` (`id`);
ALTER TABLE `ubuzima_reminder` ADD CONSTRAINT `reporter_id_refs_id_542beec7` FOREIGN KEY (`reporter_id`) REFERENCES `reporters_reporter` (`id`);
ALTER TABLE `ubuzima_reminder` ADD CONSTRAINT `type_id_refs_id_1fe64091` FOREIGN KEY (`type_id`) REFERENCES `ubuzima_remindertype` (`id`);
CREATE TABLE `ubuzima_healthtarget` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` longtext NOT NULL,
    `description` longtext NOT NULL,
    `positive` bool NOT NULL,
    `target` integer NOT NULL
)
;
CREATE TABLE `ubuzima_locationshorthand` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `original_id` integer NOT NULL,
    `district_id` integer NOT NULL,
    `province_id` integer NOT NULL
)
;
ALTER TABLE `ubuzima_locationshorthand` ADD CONSTRAINT `original_id_refs_id_3ff6a1c2` FOREIGN KEY (`original_id`) REFERENCES `locations_location` (`id`);
ALTER TABLE `ubuzima_locationshorthand` ADD CONSTRAINT `district_id_refs_id_3ff6a1c2` FOREIGN KEY (`district_id`) REFERENCES `locations_location` (`id`);
ALTER TABLE `ubuzima_locationshorthand` ADD CONSTRAINT `province_id_refs_id_3ff6a1c2` FOREIGN KEY (`province_id`) REFERENCES `locations_location` (`id`);
CREATE TABLE `ubuzima_refusal` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `reporter_id` integer NOT NULL,
    `refid` longtext NOT NULL,
    `created` datetime NOT NULL
)
;
ALTER TABLE `ubuzima_refusal` ADD CONSTRAINT `reporter_id_refs_id_2c87365e` FOREIGN KEY (`reporter_id`) REFERENCES `reporters_reporter` (`id`);
CREATE TABLE `ubuzima_errortype` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(255) NOT NULL,
    `description` longtext NOT NULL
)
;
CREATE TABLE `ubuzima_errornote` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `errmsg` longtext NOT NULL,
    `type_id` integer NOT NULL,
    `errby_id` integer,
    `identity` varchar(13),
    `created` datetime NOT NULL
)
;
ALTER TABLE `ubuzima_errornote` ADD CONSTRAINT `errby_id_refs_id_515b7cd6` FOREIGN KEY (`errby_id`) REFERENCES `reporters_reporter` (`id`);
ALTER TABLE `ubuzima_errornote` ADD CONSTRAINT `type_id_refs_id_73d15121` FOREIGN KEY (`type_id`) REFERENCES `ubuzima_errortype` (`id`);
CREATE TABLE `ubuzima_userlocation` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `location_id` integer NOT NULL
)
;
ALTER TABLE `ubuzima_userlocation` ADD CONSTRAINT `location_id_refs_id_14eca323` FOREIGN KEY (`location_id`) REFERENCES `locations_location` (`id`);
ALTER TABLE `ubuzima_userlocation` ADD CONSTRAINT `user_id_refs_id_7f120426` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `ubuzima_triggeredalert` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `reporter_id` integer NOT NULL,
    `report_id` integer,
    `trigger_id` integer NOT NULL,
    `date` datetime NOT NULL,
    `response` varchar(3) NOT NULL
)
;
ALTER TABLE `ubuzima_triggeredalert` ADD CONSTRAINT `trigger_id_refs_id_238a9d6b` FOREIGN KEY (`trigger_id`) REFERENCES `ubuzima_triggeredtext` (`id`);
ALTER TABLE `ubuzima_triggeredalert` ADD CONSTRAINT `report_id_refs_id_1a0a2802` FOREIGN KEY (`report_id`) REFERENCES `ubuzima_report` (`id`);
ALTER TABLE `ubuzima_triggeredalert` ADD CONSTRAINT `reporter_id_refs_id_4d6b318` FOREIGN KEY (`reporter_id`) REFERENCES `reporters_reporter` (`id`);
CREATE INDEX `ubuzima_fieldtype_42dc49bc` ON `ubuzima_fieldtype` (`category_id`);
CREATE INDEX `ubuzima_patient_319d859` ON `ubuzima_patient` (`location_id`);
CREATE INDEX `ubuzima_field_777d41c8` ON `ubuzima_field` (`type_id`);
CREATE INDEX `ubuzima_report_7dce1e39` ON `ubuzima_report` (`reporter_id`);
CREATE INDEX `ubuzima_report_319d859` ON `ubuzima_report` (`location_id`);
CREATE INDEX `ubuzima_report_2582c080` ON `ubuzima_report` (`patient_id`);
CREATE INDEX `ubuzima_report_777d41c8` ON `ubuzima_report` (`type_id`);
CREATE INDEX `ubuzima_reminder_7dce1e39` ON `ubuzima_reminder` (`reporter_id`);
CREATE INDEX `ubuzima_reminder_29fa1030` ON `ubuzima_reminder` (`report_id`);
CREATE INDEX `ubuzima_reminder_777d41c8` ON `ubuzima_reminder` (`type_id`);
CREATE INDEX `ubuzima_locationshorthand_533ede81` ON `ubuzima_locationshorthand` (`original_id`);
CREATE INDEX `ubuzima_locationshorthand_1f903cfa` ON `ubuzima_locationshorthand` (`district_id`);
CREATE INDEX `ubuzima_locationshorthand_37751324` ON `ubuzima_locationshorthand` (`province_id`);
CREATE INDEX `ubuzima_refusal_7dce1e39` ON `ubuzima_refusal` (`reporter_id`);
CREATE INDEX `ubuzima_errornote_777d41c8` ON `ubuzima_errornote` (`type_id`);
CREATE INDEX `ubuzima_errornote_684841ad` ON `ubuzima_errornote` (`errby_id`);
CREATE INDEX `ubuzima_userlocation_403f60f` ON `ubuzima_userlocation` (`user_id`);
CREATE INDEX `ubuzima_userlocation_319d859` ON `ubuzima_userlocation` (`location_id`);
CREATE INDEX `ubuzima_triggeredalert_7dce1e39` ON `ubuzima_triggeredalert` (`reporter_id`);
CREATE INDEX `ubuzima_triggeredalert_29fa1030` ON `ubuzima_triggeredalert` (`report_id`);
CREATE INDEX `ubuzima_triggeredalert_3735711d` ON `ubuzima_triggeredalert` (`trigger_id`);COMMIT;
