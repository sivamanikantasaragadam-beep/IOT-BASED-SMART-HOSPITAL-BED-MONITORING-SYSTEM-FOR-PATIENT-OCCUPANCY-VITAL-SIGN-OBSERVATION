#!/usr/bin/env python3
"""
Smart Hospital Bed Monitoring System - Simulation Engine
Monitors patient occupancy, vital signs, and emergency conditions
"""

import json
import csv
from datetime import datetime, timedelta
import random
import math

class BedSensor:
    """Simulates pressure sensors in hospital beds"""
    def __init__(self, bed_id):
        self.bed_id = bed_id
        self.occupied = False
        self.pressure_reading = 0.0
        self.occupancy_threshold = 20.0  # kPa
        
    def read_pressure(self):
        """Generate pressure reading"""
        if self.occupied:
            # Realistic pressure for human body on bed
            base_pressure = random.gauss(60, 5)
            base_pressure = max(20, min(100, base_pressure))
        else:
            # Minimal pressure when unoccupied
            base_pressure = random.gauss(2, 1)
            base_pressure = max(0, base_pressure)
        
        self.pressure_reading = base_pressure
        return self.pressure_reading
    
    def detect_occupancy(self):
        """Detect if bed is occupied"""
        self.occupied = self.pressure_reading > self.occupancy_threshold
        return self.occupied

class VitalSignSensor:
    """Simulates vital sign sensors (heart rate, temperature, SpO2)"""
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.heart_rate = 72  # bpm
        self.body_temperature = 37.0  # Celsius
        self.spo2 = 98  # Oxygen saturation percentage
        self.respiratory_rate = 16  # breaths per minute
        
    def read_heart_rate(self):
        """Generate realistic heart rate reading"""
        # Normal resting heart rate: 60-100 bpm
        variation = random.gauss(0, 2)
        self.heart_rate = max(40, min(150, self.heart_rate + variation))
        return round(self.heart_rate, 1)
    
    def read_body_temperature(self):
        """Generate realistic body temperature reading"""
        # Normal body temperature: 36.5-37.5°C
        variation = random.gauss(0, 0.1)
        self.body_temperature = max(35.0, min(40.0, self.body_temperature + variation))
        return round(self.body_temperature, 2)
    
    def read_spo2(self):
        """Generate realistic SpO2 reading"""
        # Normal SpO2: 95-100%
        variation = random.gauss(0, 0.5)
        self.spo2 = max(85, min(100, self.spo2 + variation))
        return round(self.spo2, 1)
    
    def read_respiratory_rate(self):
        """Generate realistic respiratory rate"""
        # Normal respiratory rate: 12-20 breaths/min
        variation = random.gauss(0, 0.5)
        self.respiratory_rate = max(8, min(30, self.respiratory_rate + variation))
        return round(self.respiratory_rate, 1)

class Patient:
    """Represents a patient in a hospital bed"""
    def __init__(self, patient_id, name, age, condition):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.condition = condition  # Normal, Critical, Recovering
        self.vital_signs = VitalSignSensor(patient_id)
        self.admitted_time = datetime.now()
        self.discharge_time = None
        
    def get_patient_info(self):
        """Return patient information"""
        return {
            'patient_id': self.patient_id,
            'name': self.name,
            'age': self.age,
            'condition': self.condition,
            'admitted_time': self.admitted_time.isoformat()
        }

class HospitalBed:
    """Represents a hospital bed with monitoring capabilities"""
    def __init__(self, bed_id, bed_number, ward):
        self.bed_id = bed_id
        self.bed_number = bed_number
        self.ward = ward
        self.bed_sensor = BedSensor(bed_id)
        self.current_patient = None
        self.last_occupancy_change = datetime.now()
        
    def admit_patient(self, patient):
        """Admit a patient to the bed"""
        self.current_patient = patient
        self.bed_sensor.occupied = True
        self.last_occupancy_change = datetime.now()
        
    def discharge_patient(self):
        """Discharge patient from bed"""
        self.current_patient = None
        self.bed_sensor.occupied = False
        self.last_occupancy_change = datetime.now()
    
    def get_bed_status(self):
        """Get current bed status"""
        return {
            'bed_id': self.bed_id,
            'bed_number': self.bed_number,
            'ward': self.ward,
            'occupied': self.bed_sensor.occupied,
            'patient_id': self.current_patient.patient_id if self.current_patient else None,
            'pressure_reading': self.bed_sensor.pressure_reading
        }

class AlertGenerator:
    """Generates alerts for abnormal conditions"""
    def __init__(self):
        self.alerts = []
        
    def check_vital_signs(self, patient, timestamp):
        """Check vital signs and generate alerts"""
        alerts = []
        
        # Heart rate alerts
        if patient.vital_signs.heart_rate < 50:
            alerts.append({
                'timestamp': timestamp,
                'alert_type': 'CRITICAL_LOW_HEART_RATE',
                'severity': 'CRITICAL',
                'value': patient.vital_signs.heart_rate,
                'threshold': 50,
                'message': f'Critical low heart rate: {patient.vital_signs.heart_rate} bpm'
            })
        elif patient.vital_signs.heart_rate > 120:
            alerts.append({
                'timestamp': timestamp,
                'alert_type': 'HIGH_HEART_RATE',
                'severity': 'WARNING',
                'value': patient.vital_signs.heart_rate,
                'threshold': 120,
                'message': f'High heart rate: {patient.vital_signs.heart_rate} bpm'
            })
        
        # Temperature alerts
        if patient.vital_signs.body_temperature < 36.0:
            alerts.append({
                'timestamp': timestamp,
                'alert_type': 'LOW_BODY_TEMPERATURE',
                'severity': 'WARNING',
                'value': patient.vital_signs.body_temperature,
                'threshold': 36.0,
                'message': f'Low body temperature: {patient.vital_signs.body_temperature}°C'
            })
        elif patient.vital_signs.body_temperature > 38.5:
            alerts.append({
                'timestamp': timestamp,
                'alert_type': 'HIGH_FEVER',
                'severity': 'WARNING',
                'value': patient.vital_signs.body_temperature,
                'threshold': 38.5,
                'message': f'High fever: {patient.vital_signs.body_temperature}°C'
            })
        
        # SpO2 alerts
        if patient.vital_signs.spo2 < 90:
            alerts.append({
                'timestamp': timestamp,
                'alert_type': 'CRITICAL_LOW_SPO2',
                'severity': 'CRITICAL',
                'value': patient.vital_signs.spo2,
                'threshold': 90,
                'message': f'Critical low oxygen saturation: {patient.vital_signs.spo2}%'
            })
        elif patient.vital_signs.spo2 < 95:
            alerts.append({
                'timestamp': timestamp,
                'alert_type': 'LOW_SPO2',
                'severity': 'WARNING',
                'value': patient.vital_signs.spo2,
                'threshold': 95,
                'message': f'Low oxygen saturation: {patient.vital_signs.spo2}%'
            })
        
        # Respiratory rate alerts
        if patient.vital_signs.respiratory_rate < 10:
            alerts.append({
                'timestamp': timestamp,
                'alert_type': 'LOW_RESPIRATORY_RATE',
                'severity': 'WARNING',
                'value': patient.vital_signs.respiratory_rate,
                'threshold': 10,
                'message': f'Low respiratory rate: {patient.vital_signs.respiratory_rate} breaths/min'
            })
        elif patient.vital_signs.respiratory_rate > 25:
            alerts.append({
                'timestamp': timestamp,
                'alert_type': 'HIGH_RESPIRATORY_RATE',
                'severity': 'WARNING',
                'value': patient.vital_signs.respiratory_rate,
                'threshold': 25,
                'message': f'High respiratory rate: {patient.vital_signs.respiratory_rate} breaths/min'
            })
        
        return alerts

class SmartHospitalBedSystem:
    """Main system controller for hospital bed monitoring"""
    def __init__(self, num_beds=10):
        self.beds = []
        self.patients = []
        self.alert_generator = AlertGenerator()
        self.readings = []
        self.alerts = []
        self.statistics = {}
        
        # Initialize beds
        for i in range(num_beds):
            bed = HospitalBed(f'BED_{i+1:03d}', i+1, f'Ward_{(i//5)+1}')
            self.beds.append(bed)
        
        # Create sample patients
        patient_names = ['John Smith', 'Mary Johnson', 'Robert Brown', 'Patricia Davis', 
                        'Michael Wilson', 'Jennifer Martinez', 'William Anderson', 'Linda Taylor']
        conditions = ['Normal', 'Critical', 'Recovering']
        
        for i in range(min(6, num_beds)):
            patient = Patient(f'PAT_{i+1:03d}', patient_names[i], random.randint(30, 85), 
                            random.choice(conditions))
            self.patients.append(patient)
            self.beds[i].admit_patient(patient)
    
    def run_simulation(self, num_cycles=1000):
        """Run the monitoring simulation"""
        print(f"Starting Smart Hospital Bed Monitoring Simulation...")
        print(f"Number of beds: {len(self.beds)}")
        print(f"Number of patients: {len(self.patients)}")
        print(f"Simulation cycles: {num_cycles}")
        print()
        
        start_time = datetime.now()
        
        for cycle in range(num_cycles):
            timestamp = start_time + timedelta(minutes=cycle)
            
            # Process each bed
            for bed in self.beds:
                # Read bed sensor
                bed.bed_sensor.read_pressure()
                bed.bed_sensor.detect_occupancy()
                
                # Record bed reading
                bed_reading = {
                    'timestamp': timestamp.isoformat(),
                    'cycle': cycle,
                    'bed_id': bed.bed_id,
                    'bed_number': bed.bed_number,
                    'ward': bed.ward,
                    'occupied': bed.bed_sensor.occupied,
                    'pressure_reading': round(bed.bed_sensor.pressure_reading, 2),
                    'patient_id': bed.current_patient.patient_id if bed.current_patient else None
                }
                self.readings.append(bed_reading)
                
                # If patient is in bed, read vital signs and generate alerts
                if bed.current_patient:
                    patient = bed.current_patient
                    
                    # Read vital signs
                    hr = patient.vital_signs.read_heart_rate()
                    temp = patient.vital_signs.read_body_temperature()
                    spo2 = patient.vital_signs.read_spo2()
                    rr = patient.vital_signs.read_respiratory_rate()
                    
                    # Record vital signs
                    vital_reading = {
                        'timestamp': timestamp.isoformat(),
                        'cycle': cycle,
                        'patient_id': patient.patient_id,
                        'patient_name': patient.name,
                        'bed_id': bed.bed_id,
                        'heart_rate': hr,
                        'body_temperature': temp,
                        'spo2': spo2,
                        'respiratory_rate': rr,
                        'condition': patient.condition
                    }
                    
                    # Generate alerts
                    alerts = self.alert_generator.check_vital_signs(patient, timestamp)
                    for alert in alerts:
                        alert['patient_id'] = patient.patient_id
                        alert['bed_id'] = bed.bed_id
                        self.alerts.append(alert)
                    
                    # Simulate patient discharge (5% chance per cycle)
                    if random.random() < 0.05 and patient.condition != 'Critical':
                        bed.discharge_patient()
                        # Admit new patient
                        if len(self.patients) > 0:
                            new_patient = Patient(f'PAT_{random.randint(100, 999):03d}', 
                                                random.choice(['Alice Green', 'Bob White', 'Carol Black']),
                                                random.randint(25, 80),
                                                random.choice(['Normal', 'Recovering']))
                            self.patients.append(new_patient)
                            bed.admit_patient(new_patient)
            
            # Progress indicator
            if (cycle + 1) % 100 == 0:
                print(f"Completed {cycle + 1}/{num_cycles} cycles...")
        
        print(f"Simulation completed in {(datetime.now() - start_time).total_seconds():.2f} seconds")
        self.calculate_statistics()
    
    def calculate_statistics(self):
        """Calculate comprehensive statistics"""
        print("\nCalculating statistics...")
        
        # Bed statistics
        occupied_count = sum(1 for bed in self.beds if bed.bed_sensor.occupied)
        
        # Alert statistics
        critical_alerts = sum(1 for alert in self.alerts if alert['severity'] == 'CRITICAL')
        warning_alerts = sum(1 for alert in self.alerts if alert['severity'] == 'WARNING')
        
        # Vital signs statistics
        heart_rates = []
        temperatures = []
        spo2_values = []
        
        for reading in self.readings:
            if 'heart_rate' in reading:
                heart_rates.append(reading['heart_rate'])
                temperatures.append(reading['body_temperature'])
                spo2_values.append(reading['spo2'])
        
        self.statistics = {
            'total_beds': len(self.beds),
            'occupied_beds': occupied_count,
            'occupancy_rate': round((occupied_count / len(self.beds)) * 100, 2),
            'total_patients': len(self.patients),
            'total_readings': len(self.readings),
            'total_alerts': len(self.alerts),
            'critical_alerts': critical_alerts,
            'warning_alerts': warning_alerts,
            'alert_rate': round((len(self.alerts) / len(self.readings)) * 100, 2) if self.readings else 0,
            'avg_heart_rate': round(sum(heart_rates) / len(heart_rates), 2) if heart_rates else 0,
            'avg_temperature': round(sum(temperatures) / len(temperatures), 2) if temperatures else 0,
            'avg_spo2': round(sum(spo2_values) / len(spo2_values), 2) if spo2_values else 0,
            'min_heart_rate': min(heart_rates) if heart_rates else 0,
            'max_heart_rate': max(heart_rates) if heart_rates else 0,
            'min_temperature': min(temperatures) if temperatures else 0,
            'max_temperature': max(temperatures) if temperatures else 0,
            'min_spo2': min(spo2_values) if spo2_values else 0,
            'max_spo2': max(spo2_values) if spo2_values else 0
        }
        
        print(f"Total readings: {self.statistics['total_readings']}")
        print(f"Total alerts: {self.statistics['total_alerts']}")
        print(f"Occupancy rate: {self.statistics['occupancy_rate']}%")
        print(f"Average heart rate: {self.statistics['avg_heart_rate']} bpm")
        print(f"Average temperature: {self.statistics['avg_temperature']}°C")
        print(f"Average SpO2: {self.statistics['avg_spo2']}%")
    
    def export_to_csv(self):
        """Export readings to CSV files"""
        print("\nExporting data to CSV files...")
        
        # Export bed readings
        with open('bed_readings.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'cycle', 'bed_id', 'bed_number', 
                                                   'ward', 'occupied', 'pressure_reading', 'patient_id'])
            writer.writeheader()
            writer.writerows(self.readings)
        print("✓ bed_readings.csv")
        
        # Export alerts
        if self.alerts:
            with open('system_alerts.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'alert_type', 'severity', 
                                                       'patient_id', 'bed_id', 'value', 'threshold', 'message'])
                writer.writeheader()
                writer.writerows(self.alerts)
            print("✓ system_alerts.csv")
    
    def export_to_json(self):
        """Export analytics to JSON"""
        print("Exporting analytics to JSON...")
        
        analytics = {
            'simulation_info': {
                'total_beds': len(self.beds),
                'total_patients': len(self.patients),
                'total_cycles': len(set(r['cycle'] for r in self.readings))
            },
            'statistics': self.statistics,
            'beds': [bed.get_bed_status() for bed in self.beds],
            'patients': [p.get_patient_info() for p in self.patients]
        }
        
        with open('hospital_bed_analytics.json', 'w') as f:
            json.dump(analytics, f, indent=2)
        print("✓ hospital_bed_analytics.json")
    
    def print_summary(self):
        """Print summary statistics"""
        print("\n" + "="*60)
        print("SMART HOSPITAL BED MONITORING SYSTEM - SIMULATION SUMMARY")
        print("="*60)
        print(f"Total Beds: {self.statistics['total_beds']}")
        print(f"Occupied Beds: {self.statistics['occupied_beds']}")
        print(f"Occupancy Rate: {self.statistics['occupancy_rate']}%")
        print(f"Total Patients: {self.statistics['total_patients']}")
        print(f"Total Readings: {self.statistics['total_readings']}")
        print(f"Total Alerts: {self.statistics['total_alerts']}")
        print(f"  - Critical: {self.statistics['critical_alerts']}")
        print(f"  - Warning: {self.statistics['warning_alerts']}")
        print(f"Alert Rate: {self.statistics['alert_rate']}%")
        print(f"\nVital Signs Statistics:")
        print(f"  Heart Rate: {self.statistics['avg_heart_rate']} bpm (range: {self.statistics['min_heart_rate']}-{self.statistics['max_heart_rate']})")
        print(f"  Temperature: {self.statistics['avg_temperature']}°C (range: {self.statistics['min_temperature']}-{self.statistics['max_temperature']})")
        print(f"  SpO2: {self.statistics['avg_spo2']}% (range: {self.statistics['min_spo2']}-{self.statistics['max_spo2']})")
        print("="*60)

def main():
    """Main execution function"""
    # Create and run system
    system = SmartHospitalBedSystem(num_beds=10)
    system.run_simulation(num_cycles=1000)
    
    # Export data
    system.export_to_csv()
    system.export_to_json()
    
    # Print summary
    system.print_summary()

if __name__ == '__main__':
    main()
