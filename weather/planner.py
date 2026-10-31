"""Conservative weather screening, not a pesticide recommendation or water prescription."""
from datetime import datetime, timedelta, timezone
import math
from .spray import calculate_wet_bulb, evaluate_spray_condition


def number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)


def build_plan(days, crops, growing_place='', soil='unknown', now=None):
    now = now or datetime.now(timezone.utc)
    slots=[]
    for day in days:
        for slot in day.get('slots',[]):
            when=datetime.fromisoformat(slot['time'])
            if when.tzinfo and when >= now:
                slots.append({**slot,'when':when})
    slots.sort(key=lambda s:s['when'])
    planned=[]
    for index,slot in enumerate(slots):
        # Forecasts are three-hour snapshots. Never invent hourly predictions.
        horizon=[s for s in slots[index:] if s['when'] <= slot['when']+timedelta(hours=6)]
        complete=(len(horizon)>=3 and all(horizon[n+1]['when']-horizon[n]['when']==timedelta(hours=3) for n in range(len(horizon)-1)))
        valid=complete and all(number(s.get(k)) for s in horizon for k in ('temp','humidity','wind','pop','rain','code'))
        spray='Insufficient forecast'
        delta_t_val='—'
        delta_t_ok=False
        spray_reason=''
        if valid:
            wind_kmh = slot['wind'] * 3.6
            rain_3h = (slot.get('rain', 0) > 0) or (slot.get('pop', 0) >= 0.3) or (slot.get('code', 800) < 600) or any(s['rain'] > 0 or s['pop'] >= 0.3 or s.get('code', 800) < 600 for s in horizon)
            eval_res = evaluate_spray_condition(slot['temp'], slot['humidity'], wind_kmh, rain_3h)
            delta_t_val = f"{eval_res['delta_t']} °C"
            delta_t_ok = (2 <= eval_res['delta_t'] <= 8)
            spray_reason = eval_res['reason']

            daylight_ok = slot.get('daylight', False) and 8 <= slot['when'].hour < 17
            gust_ok = not (number(slot.get('gust')) and slot['gust'] > 4.5)
            fog_ok = slot.get('code') not in (701, 741)
            unsafe = (not daylight_ok or not gust_ok or not fog_ok or eval_res['status'] in ('DO_NOT_SPRAY', 'POOR_CONDITIONS'))
            spray = 'Avoid' if unsafe else 'Check conditions'
        irrigation='Insufficient forecast'
        if valid:
            if soil=='wet' or any(s['rain']>=1 or s['pop']>=.5 for s in horizon) or slot['temp']<=4:
                irrigation='Avoid'
            elif not (6<=slot['when'].hour<11 or 16<=slot['when'].hour<19) or slot['temp']>=35:
                irrigation='Avoid'
            else:
                irrigation='Check conditions' if soil=='dry' else 'Check soil first'
        if crops == ['Rice'] and growing_place != 'pots':
            irrigation = 'Check paddy water level.'
        checks = [
            {'label':'Forecast coverage','value':'6 h' if complete else '—','ok':valid},
            {'label':'Daylight','value':slot['when'].strftime('%H:%M'),
             'ok':slot.get('daylight',False) and 8<=slot['when'].hour<17},
            {'label':'Temperature (°C)','value':f"{slot.get('temp')} °C" if number(slot.get('temp')) else '—',
             'ok':number(slot.get('temp')) and 10<=slot['temp']<=28},
            {'label':'Relative humidity (%)','value':f"{slot.get('humidity')}%" if number(slot.get('humidity')) else '—',
             'ok':number(slot.get('humidity')) and 40<=slot['humidity']<=85},
            {'label':'Delta T (°C)','value':delta_t_val,
             'ok':delta_t_ok},
            {'label':'Wind speed','value':f"{slot.get('wind')} m/s" if number(slot.get('wind')) else '—',
             'ok':number(slot.get('wind')) and 1.5<=slot['wind']<=3.3},
            {'label':'Rainfall (mm)','value':f"{sum(s['rain'] for s in horizon):.1f} mm" if valid else '—',
             'ok':valid and all(s['rain']==0 for s in horizon)},
            {'label':'Rain chance','value':f"{max(s['pop'] for s in horizon)*100:.0f}%" if valid else '—',
             'ok':valid and not any(s['rain']>0 or s['pop']>=.3 or s['code']<600 for s in horizon)},
            {'label':'Weather','value':slot.get('description',''),
             'ok':number(slot.get('code')) and slot['code'] not in (701,741)},
        ]
        if number(slot.get('gust')):
            checks.append({'label':'Wind gust','value':f"{slot['gust']} m/s",'ok':slot['gust']<=4.5})
        planned.append({**slot,'checks':checks,'spray':spray,'irrigation':irrigation,
                        'delta_t':delta_t_val,'spray_reason':spray_reason,
                        'spray_class':'candidate' if spray=='Check conditions' else ('avoid' if spray=='Avoid' else 'unknown'),
                        'irrigation_class':'candidate' if irrigation=='Check conditions' else ('avoid' if irrigation=='Avoid' else 'unknown')})
    daily=[]
    for day in days:
        matching=[s for s in planned if s['when'].date().isoformat()==day['date']]
        if not matching:continue
        daily.append({**day,'when':matching[0]['when'],
                      'spray_window':next((s for s in matching if s['spray']=='Check conditions'),None),
                      'water_window':next((s for s in matching if s['irrigation'] in ('Check conditions','Check soil first')),None)})
    crop_cards=[]
    for crop in crops:
        note='Check root-zone moisture.'
        water=next((s for s in planned if s['irrigation'] in ('Check conditions','Check soil first')),None)
        if crop=='Rice' and growing_place!='pots':
            note='Check paddy water level.'
            water=None  # Forecast cannot prescribe paddy water-level management.
        elif growing_place=='pots':
            note='Check pot drainage.'
        crop_cards.append({'crop':crop,'note':note,'water':water,
                           'spray':next((s for s in planned if s['spray']=='Check conditions'),None)})
    return {'slots':planned[:16],'daily':daily,'crops':crop_cards,'next':planned[0] if planned else None}
