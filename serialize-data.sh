#!/bin/sh

year=$(date '+%Y')
database=data/lotto.db

echo "Serializing data ..."

# Data for home view
sqlite3 ${database} \
"SELECT json_object(
    'lastRow', json_object(
        'date', date,
        'round', round,
        'numbers', json_array(n1,n2,n3,n4,n5,n6,n7),
        'extra', json_array(e1)
    ),
    'totalRows', COUNT(*) OVER ()
)
FROM lotto_numbers
ORDER BY date DESC LIMIT 1" | jq > data/home.json

# Data for rows and search view
sqlite3 ${database} \
"SELECT json_object(
    'rounds', (
        SELECT json_group_array(
            json_object(
                'date', date,
                'round', round,
                'numbers', numbers,
                'extra', extra
            )
        )
        FROM (
            SELECT
                date,
                round,
                json_array(n1,n2,n3,n4,n5,n6,n7) AS numbers,
                json_array(e1) AS extra
            FROM lotto_numbers
            WHERE date>=(strftime('%Y',date('now')))
            ORDER BY date DESC
        )
    )
)" | jq '.rounds |= map(.numbers |= fromjson | .extra |= fromjson)' > "data/rows_${year}.json"

sqlite3 ${database} \
"SELECT json_object(
    'rounds', (
        SELECT json_group_array(
            json_object(
                'date', date,
                'round', round,
                'numbers', numbers,
                'extra', extra
            )
        )
        FROM (
            SELECT
                date,
                round,
                json_array(n1,n2,n3,n4,n5,n6,n7) AS numbers,
                json_array(e1,e2,e3,e4) AS extra
            FROM lotto_numbers
            ORDER BY date DESC
        )
    )
)" | jq '.rounds |= map(.numbers |= fromjson | .extra |= fromjson | .extra |= map(select(. != null)))' > data/rows.json


# Data for numbers and top10
sqlite3 ${database} \
"WITH distribution AS (
    SELECT number, frequency
        FROM (
            SELECT 1 AS number, i1 AS frequency FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 2, i2 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 3, i3 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 4, i4 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 5, i5 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 6, i6 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 7, i7 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 8, i8 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 9, i9 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 10, i10 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 11, i11 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 12, i12 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 13, i13 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 14, i14 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 15, i15 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 16, i16 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 17, i17 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 18, i18 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 19, i19 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 20, i20 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 21, i21 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 22, i22 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 23, i23 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 24, i24 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 25, i25 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 26, i26 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 27, i27 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 28, i28 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 29, i29 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 30, i30 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 31, i31 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 32, i32 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 33, i33 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 34, i34 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 35, i35 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 36, i36 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 37, i37 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 38, i38 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 39, i39 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
            UNION ALL
            SELECT 40, i40 FROM lotto_topten WHERE year=(strftime('%Y',date('now')))
        )
)
SELECT json_object(
    'average', (SELECT CAST(AVG(frequency) AS int) FROM distribution),
    'distribution', (
        SELECT json_group_array(
            json_object('number', number, 'frequency', frequency)
        )
        FROM (
            SELECT number, frequency
            FROM distribution
            ORDER BY frequency DESC
        )
    )
)" | jq > "data/numbers_${year}.json"

sqlite3 ${database} \
"WITH distribution AS (
    SELECT number, frequency
        FROM (
            SELECT 1 AS number, i1 AS frequency FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 2, i2 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 3, i3 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 4, i4 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 5, i5 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 6, i6 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 7, i7 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 8, i8 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 9, i9 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 10, i10 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 11, i11 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 12, i12 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 13, i13 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 14, i14 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 15, i15 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 16, i16 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 17, i17 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 18, i18 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 19, i19 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 20, i20 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 21, i21 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 22, i22 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 23, i23 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 24, i24 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 25, i25 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 26, i26 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 27, i27 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 28, i28 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 29, i29 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 30, i30 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 31, i31 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 32, i32 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 33, i33 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 34, i34 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 35, i35 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 36, i36 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 37, i37 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 38, i38 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 39, i39 FROM lotto_topten WHERE year=0
            UNION ALL
            SELECT 40, i40 FROM lotto_topten WHERE year=0
        )
)
SELECT json_object(
    'average', (SELECT CAST(AVG(frequency) AS int) FROM distribution),
    'distribution', (
        SELECT json_group_array(
            json_object('number', number, 'frequency', frequency)
        )
        FROM (
            SELECT number, frequency
            FROM distribution
            ORDER BY frequency DESC
        )
    )
)" | jq > "data/numbers.json"

# Data for top10
sqlite3 ${database} \
"SELECT json_array(
    json_object(
        'length', 7,
        'combinations', (
            SELECT json_group_array(
                json_object('numbers', numbers, 'frequency', frequency)
            )
            FROM (
                SELECT json_array(n1,n2,n3,n4,n5,n6,n7) AS numbers, frequency
                FROM lotto_combinations
                WHERE size=7 AND frequency > 1 ORDER BY frequency DESC LIMIT 10
            )
        )
    ),
    json_object(
        'length', 6,
        'combinations', (
            SELECT json_group_array(
                json_object('numbers', numbers, 'frequency', frequency)
            )
            FROM (
                SELECT json_array(n1,n2,n3,n4,n5,n6) AS numbers, frequency
                FROM lotto_combinations
                WHERE size=6 AND frequency > 1 ORDER BY frequency DESC LIMIT 10
            )
        )
    ),
    json_object(
        'length', 5,
        'combinations', (
            SELECT json_group_array(
                json_object('numbers', numbers, 'frequency', frequency)
            )
            FROM (
                SELECT json_array(n1,n2,n3,n4,n5) AS numbers, frequency
                FROM lotto_combinations
                WHERE size=5 AND frequency > 1 ORDER BY frequency DESC LIMIT 10
            )
        )
    ),
    json_object(
        'length', 4,
        'combinations', (
            SELECT json_group_array(
                json_object('numbers', numbers, 'frequency', frequency)
            )
            FROM (
                SELECT json_array(n1,n2,n3,n4) AS numbers, frequency
                FROM lotto_combinations
                WHERE size=4 AND frequency > 1 ORDER BY frequency DESC LIMIT 10
            )
        )
    ),
    json_object(
        'length', 3,
        'combinations', (
            SELECT json_group_array(
                json_object('numbers', numbers, 'frequency', frequency)
            )
            FROM (
                SELECT json_array(n1,n2,n3) AS numbers, frequency
                FROM lotto_combinations
                WHERE size=3 AND frequency > 1 ORDER BY frequency DESC LIMIT 10
            )
        )
    )
)" | jq 'map(.combinations |= map(.numbers |= fromjson))' > data/combinations_top10.json

# Data for stats view
sqlite3 ${database} \
"SELECT json_object(
    'lessThanEqual', (
        json_object(
            'total', (
                SELECT COUNT(*)
                FROM lotto_numbers
                WHERE n1<=31 AND n2<=31 AND n3<=31 AND n4<=31 AND n5<=31 AND n6<=31 AND n7<=31
            ),
            'percentage', (
                SELECT
                    ROUND((COUNT(CASE WHEN n1<=31 AND n2<=31 AND n3<=31 AND n4<=31 AND n5<=31 AND n6<=31 AND n7<=31 THEN 1 END) * 100.0) / COUNT(*), 2)
                FROM lotto_numbers
            )
        )
    ),
    'greaterThan', (
        json_object(
            'total', (
                SELECT COUNT(*)
                FROM lotto_numbers
                WHERE n1>31 OR n2>31 OR n3>31 OR n4>31 OR n5>31 OR n6>31 OR n7>31
            ),
            'percentage', (
                SELECT
                    ROUND((COUNT(CASE WHEN n1>31 OR n2>31 OR n3>31 OR n4>31 OR n5>31 OR n6>31 OR n7>31 THEN 1 END) * 100.0) / COUNT(*), 2)
                FROM lotto_numbers
            )
        )
    ),
    'evenNumbers', json_object(
        'total', (
            SELECT SUM(
                (n1 % 2 = 0) AND (n2 % 2 = 0) AND (n3 % 2 = 0) AND
                (n4 % 2 = 0) AND (n5 % 2 = 0) AND (n6 % 2 = 0) AND (n7 % 2 = 0)
            )
            FROM lotto_numbers
        ),
        'percentage', (
            SELECT ROUND(
                100.0 * SUM(
                    (n1 % 2 = 0) AND (n2 % 2 = 0) AND (n3 % 2 = 0) AND
                    (n4 % 2 = 0) AND (n5 % 2 = 0) AND (n6 % 2 = 0) AND (n7 % 2 = 0)
                ) / COUNT(*), 2
            )
            FROM lotto_numbers
        )
    ),
    'oddNumbers', json_object(
        'total', (
            SELECT SUM(
                (n1 % 2 = 1) AND (n2 % 2 = 1) AND (n3 % 2 = 1) AND
                (n4 % 2 = 1) AND (n5 % 2 = 1) AND (n6 % 2 = 1) AND (n7 % 2 = 1)
            )
            FROM lotto_numbers
        ),
        'percentage', (
            SELECT ROUND(
                100.0 * SUM(
                    (n1 % 2 = 1) AND (n2 % 2 = 1) AND (n3 % 2 = 1) AND
                    (n4 % 2 = 1) AND (n5 % 2 = 1) AND (n6 % 2 = 1) AND (n7 % 2 = 1)
                ) / COUNT(*), 2
            )
            FROM lotto_numbers
        )
    ),
    'mixedNumbers', json_object(
        'total', (
            SELECT
                COUNT(*) - SUM(
                    (n1 % 2 = 0) AND (n2 % 2 = 0) AND (n3 % 2 = 0) AND
                    (n4 % 2 = 0) AND (n5 % 2 = 0) AND (n6 % 2 = 0) AND (n7 % 2 = 0)
                ) - SUM(
                    (n1 % 2 = 1) AND (n2 % 2 = 1) AND (n3 % 2 = 1) AND
                    (n4 % 2 = 1) AND (n5 % 2 = 1) AND (n6 % 2 = 1) AND (n7 % 2 = 1)
                )
            FROM lotto_numbers
        ),
        'percentage', (
            SELECT ROUND(
                100.0 * (
                    COUNT(*) - SUM(
                        (n1 % 2 = 0) AND (n2 % 2 = 0) AND (n3 % 2 = 0) AND
                        (n4 % 2 = 0) AND (n5 % 2 = 0) AND (n6 % 2 = 0) AND (n7 % 2 = 0)
                    ) - SUM(
                        (n1 % 2 = 1) AND (n2 % 2 = 1) AND (n3 % 2 = 1) AND
                        (n4 % 2 = 1) AND (n5 % 2 = 1) AND (n6 % 2 = 1) AND (n7 % 2 = 1)
                    )
                ) / COUNT(*), 2
            )
            FROM lotto_numbers
        )
    )
)" | jq > data/rows_stats.json

sqlite3 ${database} \
"SELECT json_array(
    json_object(
        'length', 7,
        'unique', 18643560,
        'drawn', (
            SELECT COUNT(*)
            FROM lotto_combinations
            WHERE size=7
        ),
        'percentage', (
            SELECT
                ROUND((COUNT(CASE WHEN size=7 THEN 1 END) * 100.0) / 18643560, 2)
            FROM lotto_combinations
        )
    ),
    json_object(
        'length', 6,
        'unique', 3838380,
        'drawn', (
            SELECT COUNT(*)
            FROM lotto_combinations
            WHERE size=6
        ),
        'percentage', (
            SELECT
                ROUND((COUNT(CASE WHEN size=6 THEN 1 END) * 100.0) / 3838380, 2)
            FROM lotto_combinations
        )
    ),
    json_object(
        'length', 5,
        'unique', 658008,
        'drawn', (
            SELECT COUNT(*)
            FROM lotto_combinations
            WHERE size=5
        ),
        'percentage', (
            SELECT
                ROUND((COUNT(CASE WHEN size=5 THEN 1 END) * 100.0) / 658008, 2)
            FROM lotto_combinations
        )
    ),
    json_object(
        'length', 4,
        'unique', 91390,
        'drawn', (
            SELECT COUNT(*)
            FROM lotto_combinations
            WHERE size=4
        ),
        'percentage', (
            SELECT
                ROUND((COUNT(CASE WHEN size=4 THEN 1 END) * 100.0) / 91390, 2)
            FROM lotto_combinations
        )
    ),
    json_object(
        'length', 3,
        'unique', 9880,
        'drawn', (
            SELECT COUNT(*)
            FROM lotto_combinations
            WHERE size=3
        ),
        'percentage', (
            SELECT
                ROUND((COUNT(CASE WHEN size=3 THEN 1 END) * 100.0) / 9880, 2)
            FROM lotto_combinations
        )
    )
)" | jq > data/combinations_stats.json


# Data for generate view
sqlite3 ${database} \
"SELECT json_group_array(
  json_array(n1, n2, n3, n4, n5, n6, n7)
)
FROM lotto_generated
" | jq > data/generated_rows.json

sqlite3 ${database} \
"SELECT json_object(
    'rounds', (
        SELECT json_group_array(
            json_object('round', round, 'winnings', winnings)
        )
        FROM (
            SELECT
                round,
                json_object(
                    '7', c7,
                    '6p1', c6p1,
                    '6', c6,
                    '5', c5,
                    '4', c4,
                    '3p1', c3p1
                ) as winnings
            FROM lotto_genstat
            JOIN lotto_numbers ON lotto_genstat.lotto_numbers_id=lotto_numbers.id
            WHERE lotto_numbers.date>=(strftime('%Y',date('now')))
            ORDER BY lotto_numbers.date DESC
        )
    )
)" | jq '.rounds |= map(.winnings |= fromjson)' > "data/generated_stats_${year}.json"

echo "Serialization completed"

