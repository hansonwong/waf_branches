<?php

include_once __DIR__ . '/../include.php';
include_once __DIR__ . '/lib_example.php';
// load production config
$config = include_once __DIR__ . '/../../_clickhouse_config_product.php';

die("Перенесено в отдельный проект https://github.com/smi2/phpMigrationsClickhouse");
/*
$cl = new ClickHouse\Cluster($config);

$cl->setScanTimeOut(2.5); // 2500 ms
if (!$cl->isReplicasIsOk())
{
    throw new Exception('Replica state is bad , error='.$cl->getError());
}
//
$cluster_name='sharovara';
//
echo "> $cluster_name , count shard   = ".$cl->getClusterCountShard($cluster_name)." ; count replica = ".$cl->getClusterCountReplica($cluster_name)."\n";


// ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
$mclq=new ClickHouse\Cluster\Migration($cluster_name);
$mclq->setAutoSplitQuery(';;');




$mclq->addSqlUpdate("

DROP DATABASE IF EXISTS shara

;;

CREATE DATABASE IF NOT EXISTS shara

;;

DROP TABLE IF EXISTS shara.adpreview_body_views_sharded

;;

DROP TABLE IF EXISTS shara.adpreview_body_views
;;

CREATE TABLE IF NOT EXISTS shara.adpreview_body_views_sharded (
    event_date Date DEFAULT toDate(event_time),
    event_time DateTime DEFAULT now(),
    body_id Int32,
    site_id Int32,
    views Int32
) ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/{sharovara_replica}/shara/adpreview_body_views_sharded', '{replica}', event_date, (event_date, event_time, body_id, site_id), 8192)
;;
CREATE TABLE IF NOT EXISTS
shara.adpreview_body_views AS shara.adpreview_body_views_sharded
ENGINE = Distributed(sharovara, shara, adpreview_body_views_sharded , rand())
");

// откат
$mclq->addSqlDowngrade('

DROP TABLE IF EXISTS shara.adpreview_body_views

;;

DROP TABLE IF EXISTS shara.adpreview_body_views_sharded
;;
DROP DATABASE IF EXISTS shara

');

echo "Start:sendMigration\n";
if (!$cl->sendMigration($mclq,true))
{
    throw new Exception('sendMigration is bad , error='.$cl->getError());
}


echo "\n----\nEND\n";
// ----------------------------------------------------------------------
*/
