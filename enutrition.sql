-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema e_nutrition
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `e_nutrition` ;

-- -----------------------------------------------------
-- Schema e_nutrition
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `e_nutrition` DEFAULT CHARACTER SET utf8 ;
USE `e_nutrition` ;

-- -----------------------------------------------------
-- Table `e_nutrition`.`food`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `e_nutrition`.`food` ;

CREATE TABLE IF NOT EXISTS `e_nutrition`.`food` (
  `food_id` INT(11) NOT NULL AUTO_INCREMENT,
  `food_name` VARCHAR(150) NULL DEFAULT NULL,
  `food_calories` INT(11) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`food_id`))
ENGINE = InnoDB
AUTO_INCREMENT = 10
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `e_nutrition`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `e_nutrition`.`users` ;

CREATE TABLE IF NOT EXISTS `e_nutrition`.`users` (
  `user_id` INT(11) NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(100) NULL DEFAULT NULL,
  `last_name` VARCHAR(100) NULL DEFAULT NULL,
  `email` VARCHAR(100) NULL DEFAULT NULL,
  `password` VARCHAR(255) NULL DEFAULT NULL,
  `user_level` INT(1) NULL DEFAULT NULL,
  `file_path` VARCHAR(255) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`))
ENGINE = InnoDB
AUTO_INCREMENT = 38
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `e_nutrition`.`posts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `e_nutrition`.`posts` ;

CREATE TABLE IF NOT EXISTS `e_nutrition`.`posts` (
  `post_id` INT(11) NOT NULL AUTO_INCREMENT,
  `post_name` VARCHAR(150) NULL DEFAULT NULL,
  `post_content` TEXT NULL DEFAULT NULL,
  `author` INT(11) NOT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`post_id`),
  INDEX `fk_posts_users_idx` (`author` ASC) VISIBLE,
  CONSTRAINT `fk_posts_users`
    FOREIGN KEY (`author`)
    REFERENCES `e_nutrition`.`users` (`user_id`))
ENGINE = InnoDB
AUTO_INCREMENT = 14
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `e_nutrition`.`liked_posts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `e_nutrition`.`liked_posts` ;

CREATE TABLE IF NOT EXISTS `e_nutrition`.`liked_posts` (
  `users_id` INT(11) NOT NULL,
  `posts_id` INT(11) NOT NULL,
  PRIMARY KEY (`users_id`, `posts_id`),
  INDEX `fk_users_has_posts_posts1_idx` (`posts_id` ASC) VISIBLE,
  INDEX `fk_users_has_posts_users1_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_posts_posts1`
    FOREIGN KEY (`posts_id`)
    REFERENCES `e_nutrition`.`posts` (`post_id`),
  CONSTRAINT `fk_users_has_posts_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `e_nutrition`.`users` (`user_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
