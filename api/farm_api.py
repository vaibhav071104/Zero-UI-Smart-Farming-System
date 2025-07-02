from flask import Flask, request, jsonify
from datetime import datetime
import json

class FarmAPI:
    def __init__(self, multi_farm_controller):
        self.app = Flask(__name__)
        self.multi_farm = multi_farm_controller
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/farms', methods=['GET'])
        def get_all_farms():
            try:
                user_id = request.headers.get('User-ID', 'admin')
                farms_status = self.multi_farm.get_all_farms_status(user_id)
                return jsonify(farms_status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/farms/<farm_id>', methods=['GET'])
        def get_farm_details(farm_id):
            try:
                user_id = request.headers.get('User-ID', 'admin')
                details = self.multi_farm.get_farm_details(farm_id, user_id)
                return jsonify(details)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/farms', methods=['POST'])
        def create_farm():
            try:
                data = request.get_json()
                user_id = request.headers.get('User-ID', 'admin')
                
                result = self.multi_farm.add_farm(
                    farm_id=data['farm_id'],
                    name=data['name'],
                    location=data['location'],
                    owner_id=user_id,
                    area_hectares=data['area_hectares'],
                    crop_type=data['crop_type'],
                    planting_date=data.get('planting_date')
                )
                
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/farms/<farm_id>/irrigation', methods=['POST'])
        def control_irrigation(farm_id):
            try:
                data = request.get_json()
                user_id = request.headers.get('User-ID', 'admin')
                action = data.get('action')  # 'start' or 'stop'
                
                result = self.multi_farm.control_farm_irrigation(farm_id, action, user_id)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/analytics', methods=['GET'])
        def get_analytics():
            try:
                user_id = request.headers.get('User-ID', 'admin')
                analytics = self.multi_farm.get_multi_farm_analytics(user_id)
                return jsonify(analytics)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/dashboard', methods=['GET'])
        def get_dashboard():
            try:
                user_id = request.headers.get('User-ID', 'admin')
                from dashboard.farm_dashboard import FarmDashboard
                dashboard = FarmDashboard(self.multi_farm)
                data = dashboard.generate_dashboard_data(user_id)
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the API server"""
        print(f"Starting Farm API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
