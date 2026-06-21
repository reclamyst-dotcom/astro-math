import os
# Принудительно отключаем запросы к интернету для эфемерид
os.environ['KERYKEION_OFFLINE'] = '1'

from flask import Flask, request, jsonify
import kerykeion

app = Flask(__name__)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json() or {}
        dp = list(map(int, data['birth_date'].split('-')))
        tp = list(map(int, data['birth_time'].split(':')[:2]))
        
        # Расчет
        chart = kerykeion.AstrologicalSubject('User', dp[0], dp[1], dp[2], tp[0], tp[1], 
                                              lat=float(data['lat']), lng=float(data['lon']), 
                                              tz_str=str(int(float(data['timezone']))))
        
        planets = {p.name: {'sign': p.sign, 'degree': int(p.position)} 
                   for p in [chart.sun, chart.moon, chart.mercury, chart.venus, chart.mars, chart.jupiter, chart.saturn, chart.uranus, chart.neptune, chart.pluto]}
        
        return jsonify({'success': True, 'planets': planets})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3005)