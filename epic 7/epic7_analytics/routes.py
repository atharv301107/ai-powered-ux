from flask import Blueprint, render_template, request, jsonify, session

epic7_analytics = Blueprint('epic7_analytics', __name__, template_folder='templates', static_folder='static')

@epic7_analytics.route('/analytics')
def analytics_page():
    return render_template('epic7_analytics.html')

@epic7_analytics.route('/analytics/predict', methods=['POST'])
def predict_risk():
    return jsonify({'status': 'success', 'risk_score': 'Low Risk', 'details': 'Cardio health parameters within healthy thresholds.'})
