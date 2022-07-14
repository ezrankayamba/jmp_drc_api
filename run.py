# main.py

from fastapi import FastAPI

from lib.utils import drivers_kpi, generic_inspections, generic_trips, inspection_trends, trip_reason, trip_status, trip_trends, users

app = FastAPI()


@app.get("/")
async def api(start_at=None, end_at=None):
    data = {
        'result': 0,
        'message': "Successfully fetched data",
        'data': {
            'trips': {
                'today': {
                    'afterHours': generic_trips(days=1, after_hours=1),
                    'longDistance': generic_trips(days=1, after_hours=0),
                },
                '7days': {
                    'afterHours': generic_trips(days=7, after_hours=1),
                    'longDistance': generic_trips(days=7, after_hours=0),
                },
                '30days': {
                    'afterHours': generic_trips(days=30, after_hours=1),
                    'longDistance': generic_trips(days=30, after_hours=0),
                }
            },
            'inspections': {
                'today': generic_inspections(1),
                '7days': generic_inspections(7),
                '30days': generic_inspections(30),
            },
            'users': users(),
            'reasons': trip_reason(start_at, end_at),
            'statuses': trip_status(start_at, end_at),
            'tripTrends': trip_trends(start_at, end_at),
            'inspectionTrends': inspection_trends(start_at, end_at),
            'driversKpi': drivers_kpi()
        }
    }
    return data
