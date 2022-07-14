from unicodedata import category
from .db import Cursor
from datetime import datetime
from dateutil import parser
TEST_ENV = 1


def latest_time():
    with Cursor() as cursor:
        sql = 'SELECT max(time) from vw_trips_afterhours'
        cursor.execute(sql)
        (max_tm,) = next(cursor)
        return max_tm


def to_sql_date(s: str):
    d = parser.isoparse(s)
    return d.strftime('%Y-%m-%d %H:%m')


def get_today():
    return f"STR_TO_DATE('{latest_time()}', '%Y-%m-%d')" if TEST_ENV else 'CURDATE()'


def generic_trips(days, after_hours):
    sql = f'SELECT sum(trips) as trips from vw_trips_afterhours where time <= ({get_today()}) and time > ({get_today()} - INTERVAL {days} DAY) and tr_afterhours={after_hours}'
    with Cursor() as cursor:
        cursor.execute(sql)
        (trips,) = next(cursor)
        trips = trips if trips else 0
        print(f'Generic Trips ({days}, {after_hours}): {trips}')
        return trips


def trip_trends(start_at, end_at):
    sql = f'''
    SELECT 
        time, 
        sum( if( tr_afterhours=1, trips, 0 ) ) AS AFTERHOURS,  
        sum( if( tr_afterhours=0, trips, 0 ) ) AS `LONG DISTANCE`
    FROM 
        vw_trips_afterhours WHERE time <= (CURDATE() + INTERVAL 1 DAY) and time >= %s and time <= %s 
    GROUP BY 
        time;
    '''

    if start_at and end_at:
        start_at = to_sql_date(start_at)
        end_at = to_sql_date(end_at)
        with Cursor() as cursor:
            cursor.execute(sql, (start_at, end_at))
            data = []

            for row in cursor:
                (time,  after_hours, long_distance) = row
                data.append({
                    'time': time,
                    'afterHours': after_hours,
                    'longDistance': long_distance
                })
            return data
    else:
        return []


def generic_inspections(days):
    with Cursor() as cursor:
        sql = 'SELECT max(time) from vw_trips_afterhours'
        cursor.execute(sql)
        (max_tm,) = next(cursor)
    sql = f'SELECT sum(inspections) as inspections from vw_inspections where time <= ({get_today()}) and time > ({get_today()} - INTERVAL {days} DAY)'

    with Cursor() as cursor:
        cursor.execute(sql)
        (value, ) = next(cursor)
        value = value if value else 0
        # print(f'Generic Inspections: ({days}): {value}')
        return value


def inspection_trends(start_at, end_at):
    sql = f"SELECT time, inspections as 'NUMBER OF INSPECTIONS' FROM vw_inspections WHERE time < (CURDATE() + INTERVAL 1 DAY) and time >= %s and time <= %s ORDER BY time"
    if start_at and end_at:
        start_at = to_sql_date(start_at)
        end_at = to_sql_date(end_at)
        print('Inspection Trends: ', start_at, end_at)
        with Cursor() as cursor:
            cursor.execute(sql, (start_at, end_at))
            data = []

            for row in cursor:
                (time,  inspections) = row
                data.append({
                    'time': time,
                    'inspections': inspections,
                })
                # print('Data: ', data)
            return data
    else:
        return []


def users():
    sql = '''
    select sum(user_count) as users, case when usr_contractor='VODACOM' then 'VODACOM' else 'SUPPLIER' end as category
    from vw_users_subcontractor
    group by 2;
    '''
    with Cursor() as cursor:
        cursor.execute(sql)
        data = []
        for row in cursor:
            (users, category) = row
            data.append({
                'category': category,
                'users': users
            })
        # print(f'Generic Inspections: (): {data}')
        return data


def trip_reason(start_at, end_at):
    if start_at and end_at:

        start_at = to_sql_date(start_at)
        end_at = to_sql_date(end_at)
        print('Trip Reason: ', start_at, end_at)
        sql = f'''
        SELECT CASE WHEN tr_reason IN ('EMERGENCY') THEN 'PRIVATE' ELSE 'WORK' END AS tr_reason, 100*sum(trips)/(SELECT SUM(trips) FROM vw_trips_reason 
        where time >= %s and time <= %s ) as trips from vw_trips_reason where time >= %s and time <= %s group by 1 order by 1
        '''
        with Cursor() as cursor:
            cursor.execute(sql, (start_at, end_at, start_at, end_at))
            data = []
            for row in cursor:
                (reason, trips) = row
                data.append({
                    'reason': reason,
                    'trips': trips
                })
            print(f'Trip Reason: (): {data}')
            return data
    else:
        return []


def trip_status(start_at, end_at):
    if start_at and end_at:
        def sql_date(s):
            d = parser.isoparse(s)
            return d.strftime('%Y-%m-%d %H:%m')
        start_at = sql_date(start_at)
        end_at = sql_date(end_at)
        print('Trip Status: ', start_at, end_at)
        sql = f'''
        SELECT tr_status, 100*sum(trips)/(SELECT SUM(trips) FROM vw_trips_status 
        where time >= %s and time <= %s ) as trips from vw_trips_status where time >= %s and time <= %s group by 1 order by 1
        '''
        with Cursor() as cursor:
            cursor.execute(sql, (start_at, end_at, start_at, end_at))
            data = []
            for row in cursor:
                (status, trips) = row
                data.append({
                    'status': status,
                    'trips': trips
                })
            print(f'Trip Status: (): {data}')
            return data
    else:
        return []


def drivers_kpi():
    sql = f'''
        SELECT 100*(SELECT COUNT(*)
        FROM jmp_drivers WHERE dr_contractor='VODACOM')/(SELECT COUNT(*)
        FROM jmp_drivers WHERE dr_contractor='VODACOM') AS VODACOM,
        100*(SELECT COUNT(*)
        FROM jmp_drivers WHERE dr_contractor<>'VODACOM')/(SELECT COUNT(*)
        FROM jmp_drivers WHERE dr_contractor<>'VODACOM') AS SUPPLIER,
        kpi
        FROM (

        SELECT sum(users_vodacom) as VODACOM, sum(users_supplier) as SUPPLIER, kpi
        FROM (

        SELECT 'MEDICAL' as kpi, sum(
        case when dr_contractor = 'VODACOM' AND dr_medical_expiry > NOW() then 1 else 0 end
        ) AS users_vodacom, sum(
        case when dr_contractor != 'VODACOM' AND dr_medical_expiry > NOW() then 1 else 0 end
        ) AS users_supplier
        FROM jmp_drivers

        UNION 

        SELECT 'LICENCE' as kpi, sum(
        case when dr_contractor = 'VODACOM' AND dr_lic_expirydate > NOW() then 1 else 0 end
        ) AS users_vodacom, sum(
        case when dr_contractor != 'VODACOM' AND dr_lic_expirydate > NOW() then 1 else 0 end
        ) AS users_supplier
        FROM jmp_drivers

        UNION 

        SELECT 'DEFENSIVE' as kpi, sum(
        case when dr_contractor = 'VODACOM' AND dr_deffensive_expiry > NOW() then 1 else 0 end
        ) AS users_vodacom, sum(
        case when dr_contractor != 'VODACOM' AND dr_deffensive_expiry > NOW() then 1 else 0 end
        ) AS users_supplier
        FROM jmp_drivers

        ) as t

        GROUP BY  kpi
        ) AS t2
        '''
    with Cursor() as cursor:
        cursor.execute(sql)
        data = []
        for row in cursor:
            (vodacom, supplier, kpi) = row
            data.append({
                'vodacom': vodacom if vodacom else 0,
                'supplier': supplier if supplier else 0,
                'kpi': kpi,
            })
        print(f'drivers_kpi: (): {data}')
        return data
