-- ============================================================
-- Тестовое задание: SQL / PostgreSQL
-- Источник данных: yandex_direct_test
-- Подключался и проводил вычисления через DBeaver,
-- здесь просто решение
-- ============================================================


-- ============================================================
-- 0. Получение данных
-- ============================================================
WITH source_data AS (
    SELECT
        "Date"::date      AS report_date,
        "CampaignId"      AS campaign_id,
        "Clicks"          AS clicks,
        "Cost"            AS cost,
        "Device"          AS device
    FROM public.yandex_direct_test
)
SELECT *
FROM source_data


-- ============================================================
-- 1. Количество кликов и сумма расходов
--    по каждой рекламной кампании и дате
-- ============================================================
WITH source_data AS (
    SELECT
        "Date"::date      AS report_date,
        "CampaignId"      AS campaign_id,
        "Clicks"          AS clicks,
        "Cost"            AS cost,
        "Device"          AS device
    FROM yandex_direct_test
)
SELECT
    report_date,
    campaign_id,
    SUM(clicks) AS total_clicks,
    SUM(cost)   AS total_cost
FROM source_data
GROUP BY
    report_date,
    campaign_id
ORDER BY
    report_date,
    campaign_id;


-- ============================================================
-- 2. Самая популярная рекламная кампания по месяцам
-- ============================================================
WITH source_data AS (
    SELECT
        "Date"::date AS report_date,
        "CampaignId" AS campaign_id,
        "Clicks" AS clicks
    FROM yandex_direct_test
),
monthly_clicks AS (
    SELECT
        (DATE_TRUNC('month', report_date) + INTERVAL '1 month - 1 day')::date AS month_end,
        campaign_id,
        SUM(clicks) AS total_clicks
    FROM source_data
    GROUP BY
        month_end,
        campaign_id
)
SELECT DISTINCT ON (month_end)
    month_end,
    campaign_id,
    total_clicks
FROM monthly_clicks
ORDER BY
    month_end,
    total_clicks DESC,
    campaign_id;


-- ============================================================
-- 3. Самая дорогая рекламная кампания по месяцам
-- ============================================================
WITH source_data AS (
    SELECT
        "Date"::date AS report_date,
        "CampaignId" AS campaign_id,
        "Cost" AS cost
    FROM yandex_direct_test
),
monthly_costs AS (
    SELECT
        (DATE_TRUNC('month', report_date) + INTERVAL '1 month - 1 day')::date AS month_end,
        campaign_id,
        ROUND(SUM(cost)::numeric, 2) AS total_cost
    FROM source_data
    GROUP BY
        (DATE_TRUNC('month', report_date) + INTERVAL '1 month - 1 day')::date,
        campaign_id
)
SELECT DISTINCT ON (month_end)
    month_end,
    campaign_id,
    total_cost
FROM monthly_costs
ORDER BY
    month_end,
    total_cost DESC,
    campaign_id;


-- ============================================================
-- 4. Количество переходов (кликов) по рекламным кампаниям
--    относительно типа устройства пользователя
--    в разрезе каждой кампании
-- ============================================================
WITH source_data AS (
    SELECT
        "Date"::date      AS report_date,
        "CampaignId"      AS campaign_id,
        "Clicks"          AS clicks,
        "Cost"            AS cost,
        "Device"          AS device
    FROM yandex_direct_test
)
SELECT
    campaign_id,
    device,
    SUM(clicks) AS total_clicks
FROM source_data
GROUP BY
    campaign_id,
    device
ORDER BY
    campaign_id,
    total_clicks DESC,
    device;