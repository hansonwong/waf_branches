<?php

namespace ClickHouseDB;
/**
 * Class CSV
 * @package ClickHouse
 * @deprecated Оставлен для совместимости
 */
class CSV
{
    public static function quoteRow($row)
    {
        return FormatLine::CSV($row);
    }
}