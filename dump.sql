-- MySQL dump 10.16  Distrib 10.1.26-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: ipp
-- ------------------------------------------------------
-- Server version	10.1.26-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` int(11) NOT NULL,
  `leader` varchar(255) NOT NULL,
  `users` varchar(255) NOT NULL,
  `leader_id` bigint(64) NOT NULL,
  `user_id` varchar(255) NOT NULL,
  `isFull` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects` (
  `id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `img` varchar(255) NOT NULL,
  `sponsor` varchar(255) NOT NULL,
  `detail` longtext,
  `wish1` varchar(255) DEFAULT NULL,
  `wish2` varchar(255) DEFAULT NULL,
  `wish3` varchar(255) DEFAULT NULL,
  `views` int(11) NOT NULL,
  `chosen_num1` int(11) NOT NULL,
  `chosen_num2` int(11) NOT NULL,
  `chosen_num3` int(11) NOT NULL,
  `update_time` int(11) NOT NULL,
  `major` varchar(255) NOT NULL,
  `instructor` varchar(255) NOT NULL,
  `assigned` varchar(1) NOT NULL DEFAULT 'n',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projects`
--

LOCK TABLES `projects` WRITE;
/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
INSERT INTO `projects` VALUES (1,'Microsoft Kinect Development','image1.jpg','Mr. Fu','Kinect (codenamed Project Natal during development) is a line of motion sensing input devices by Microsoft for Xbox 360 and Xbox One video game consoles and Windows PCs.\nBased around a webcam-style add-on peripheral, it enables users to control and interact with their console/computer without the need for a game controller, through a natural user interface using gestures and spoken commands.[10] The first-generation Kinect was first introduced in November 2010 in an attempt to broaden Xbox 360\'s audience beyond its typical gamer base.[11] A version for Windows was released on February 1, 2012.[6] Kinect competes with several motion controllers on other home consoles, such as Wii Remote Plus for Wii and Wii U, PlayStation Move/PlayStation Eye for PlayStation 3, and PlayStation Camera for PlayStation 4. Microsoft released the Kinect software development kit for Windows 7 on June 16, 2011.[12][13][14] This SDK was meant to allow developers to write Kinecting apps in C++/CLI, C#, or Visual Basic .NET.[15][16]','515370910214','','',29,-1,-1,0,0,'ECE','S.Luke','y'),(3,'DOTA','1493180543.8290882.jpg','VALVE','CN DOTA, BEST DOTA','515370910258,515370910103','515370910214','',13,0,0,-1,0,'ECE','LUKE','y'),(4,'JIxiesai','1493180579.7570398.png','YLM','Love live xLuke','','515370910097','',9,0,-1,0,0,'All','Luke','n'),(5,'Strong','1491322295.9400535.png','Luke','How to be strong as luke?','','','515370910097',4,0,0,0,0,'ECE','Luke','n'),(6,'Hello','1493181814.9792676.jpg','asdf','**hello**','','','515370910214',3,0,0,0,0,'ece','sdF','n');
/*!40000 ALTER TABLE `projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `u_name` varchar(255) DEFAULT NULL,
  `role` varchar(255) DEFAULT NULL,
  `registed` varchar(255) DEFAULT NULL,
  `pwd` varchar(255) DEFAULT NULL,
  `stat` varchar(255) DEFAULT NULL,
  `id` bigint(64) NOT NULL,
  `grouped` varchar(255) DEFAULT NULL,
  `group_id` int(11) NOT NULL,
  `phone` bigint(64) NOT NULL,
  `major` varchar(255) NOT NULL,
  `sex` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('李冕','admin','n,n,n','123','0,0,0',50237,'n',0,13585904409,'ME','male'),('韩鹤鸣','stu','n,n,n','123','0,0,0',5143709133,'n',0,15800785519,'ECE','male'),('蔡童安','stu','n,n,n','123','0,0,0',515370910021,'n',0,123456789,'ECE','male'),('符晓浛','admin','n,n,n','123','0,0,0',515370910093,'n',0,1234567890,'ECE','male'),('朱景元','stu','n,4,5','123','0,1,1',515370910097,'n',0,18017101488,'ECE','male'),('陈俞翰','stu','3,n,n','123','2,0,0',515370910103,'n',0,15705791667,'ME','male'),('钱圣轶','stu','n,n,n','123','0,0,0',515370910143,'n',0,1234567890,'ECE','male'),('肖李然','stu','n,n,n','123','0,0,0',515370910155,'n',0,13333333333,'ECE','male'),('曾裕铭','stu','1,3,6','123','1,1,1',515370910214,'n',0,1,'ME','male'),('吴承刚','admin','n,n,n','123','0,0,0',515370910252,'n',0,123,'ECE','male'),('钟舒城','stu','n,n,n','123','0,0,0',515370910253,'n',0,15000408437,'ECE','male'),('陈亦轩','stu','3,n,n','123','2,0,0',515370910258,'n',0,123,'ME','male');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-09-07 11:31:03
