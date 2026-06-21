import os
# Принудительно отключаем запросы к интернету для эфемерид
os.environ['KERYKEION_OFFLINE'] = '1'

from flask import Flask, request, jsonify
import kerykeion
import re

app = Flask(__name__)

def normalize_timezone(tz_input):
    if not tz_input:
        return "UTC"
    
    tz_str = str(tz_input).strip()
    
    # Если это стандартная временная зона IANA (например, Europe/Moscow)
    # или UTC/GMT
    if "/" in tz_str or tz_str.upper() in ["UTC", "GMT", "ZULU"]:
        return tz_str
    
    # Если передан сдвиг вида UTC+3 или GMT-5
    match = re.match(r'^(?:UTC|GMT)\s*([+-])\s*(\d+(?:\.\d+)?)$', tz_str, re.IGNORECASE)
    if match:
        sign = match.group(1)
        try:
            offset_val = int(float(match.group(2)))
            if offset_val == 0:
                return "UTC"
            # В базе IANA сдвиги GMT имеют противоположные знаки:
            # GMT+3 — это Etc/GMT-3, GMT-5 — это Etc/GMT+5
            return f"Etc/GMT-{offset_val}" if sign == '+' else f"Etc/GMT+{offset_val}"
        except ValueError:
            pass
            
    # Если передан числовой сдвиг (например, "3", 3.0, -5)
    try:
        offset_val = int(float(tz_str))
        if offset_val == 0:
            return "UTC"
        return f"Etc/GMT-{offset_val}" if offset_val >= 0 else f"Etc/GMT+{abs(offset_val)}"
    except ValueError:
        return tz_str

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json() or {}
        dp = list(map(int, data['birth_date'].split('-')))
        tp = list(map(int, data['birth_time'].split(':')[:2]))
        
        # Расчет
        chart = kerykeion.AstrologicalSubject('User', dp[0], dp[1], dp[2], tp[0], tp[1], 
                                              lat=float(data['lat']), lng=float(data['lon']), 
                                              tz_str=normalize_timezone(data.get('timezone', 'UTC')))
        
        planets = {p.name: {'sign': p.sign, 'degree': int(p.position)} 
                   for p in [chart.sun, chart.moon, chart.mercury, chart.venus, chart.mars, chart.jupiter, chart.saturn, chart.uranus, chart.neptune, chart.pluto]}
        
        return jsonify({'success': True, 'planets': planets})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3005)