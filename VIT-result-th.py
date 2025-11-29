"""
VIT Semester Result Portal - Python Flask + MongoDB Application
Single file containing Flask backend with HTML/CSS/JS frontend
Author: VIT Results Management System
Date: 2025
"""

from flask import Flask, render_template_string, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import json

app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "vit_results"
COLLECTION_NAME = "students_results"

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Create unique index on roll_number
    collection.create_index("roll_number", unique=True)
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/save_result', methods=['POST'])
def save_result():
    try:
        data = request.json
        
        result_data = {
            'student_name': data['student_name'],
            'roll_number': data['roll_number'],
            'subjects_json': data['subjects_json'],
            'cgpa': float(data['cgpa']),
            'status': data['status'],
            'created_at': datetime.now()
        }
        
        # Check if roll number exists
        existing = collection.find_one({'roll_number': data['roll_number']})
        
        if existing:
            # Update existing record
            collection.update_one(
                {'roll_number': data['roll_number']},
                {'$set': result_data}
            )
            return jsonify({'success': True, 'message': 'Result updated successfully!'})
        else:
            # Insert new record
            collection.insert_one(result_data)
            return jsonify({'success': True, 'message': 'Result saved successfully!'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/get_all_results', methods=['GET'])
def get_all_results():
    try:
        results = list(collection.find().sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            result['_id'] = str(result['_id'])
            result['id'] = str(result['_id'])
            result['created_at'] = result['created_at'].isoformat()
        
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/search_result', methods=['POST'])
def search_result():
    try:
        data = request.json
        search_term = data['search_term']
        
        # Search by roll number or name (case-insensitive)
        results = list(collection.find({
            '$or': [
                {'roll_number': {'$regex': search_term, '$options': 'i'}},
                {'student_name': {'$regex': search_term, '$options': 'i'}}
            ]
        }))
        
        # Convert ObjectId to string
        for result in results:
            result['_id'] = str(result['_id'])
            result['id'] = str(result['_id'])
            result['created_at'] = result['created_at'].isoformat()
        
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/delete_result', methods=['POST'])
def delete_result():
    try:
        data = request.json
        result_id = data['id']
        
        collection.delete_one({'_id': ObjectId(result_id)})
        
        return jsonify({'success': True, 'message': 'Result deleted successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIT Semester Result Portal</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .tab-btn {
            padding: 12px 30px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }
        
        .tab-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: border 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .subject-card {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 2px solid #e0e0e0;
            position: relative;
        }
        
        .subject-card h3 {
            margin-bottom: 15px;
            color: #667eea;
        }
        
        .subject-row {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
            gap: 15px;
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .subject-row {
                grid-template-columns: 1fr;
            }
        }
        
        .remove-subject {
            position: absolute;
            top: 15px;
            right: 15px;
            background: #ff4757;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }
        
        .remove-subject:hover {
            background: #ff3838;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-success {
            background: #2ecc71;
            color: white;
        }
        
        .btn-success:hover {
            background: #27ae60;
        }
        
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c0392b;
        }
        
        .btn-info {
            background: #3498db;
            color: white;
        }
        
        .btn-info:hover {
            background: #2980b9;
        }
        
        .results-table {
            width: 100%;
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
        }
        
        table td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        
        table tr:hover {
            background: #f5f5f5;
        }
        
        .status-pass {
            color: #2ecc71;
            font-weight: bold;
        }
        
        .status-fail {
            color: #e74c3c;
            font-weight: bold;
        }
        
        .result-card {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .result-header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #667eea;
        }
        
        .result-header h2 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .result-info {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        
        @media (max-width: 768px) {
            .result-info {
                grid-template-columns: 1fr;
            }
        }
        
        .info-item {
            padding: 10px;
            background: #f9f9f9;
            border-radius: 5px;
        }
        
        .info-item strong {
            color: #667eea;
        }
        
        .subjects-table {
            margin: 20px 0;
        }
        
        .cgpa-section {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .cgpa-section h3 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            animation: slideDown 0.5s;
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
            }
            
            .tabs, .btn, header, footer {
                display: none !important;
            }
            
            .result-card {
                box-shadow: none;
            }
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
            display: none;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .search-box {
            margin-bottom: 20px;
        }
        
        .search-box input {
            padding: 12px 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 VIT Semester Result Portal</h1>
            <p>VISHWAKARMA INSTITUE OF TECHNOLOGY- Student Result Management System (MongoDB)</p>
        </header>
        
        <div class="content">
            <div id="alertContainer"></div>
            
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('entry')">📝 Enter Results</button>
                <button class="tab-btn" onclick="switchTab('view')">📊 View All Results</button>
                <button class="tab-btn" onclick="switchTab('search')">🔍 Search Results</button>
            </div>
            
            <div id="entryTab" class="tab-content active">
                <h2>Enter Student Result</h2>
                <form id="resultForm">
                    <div class="form-group">
                        <label>Student Name *</label>
                        <input type="text" id="studentName" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Roll Number *</label>
                        <input type="text" id="rollNumber" required>
                    </div>
                    
                    <h3 style="margin: 30px 0 20px 0;">Subject Details</h3>
                    
                    <div id="subjectsContainer"></div>
                    
                    <button type="button" class="btn btn-success" onclick="addSubject()">➕ Add Subject</button>
                    
                    <div style="margin-top: 30px; padding: 20px; background: #f0f8ff; border-radius: 10px;">
                        <h3>Result Summary</h3>
                        <p><strong>CGPA:</strong> <span id="displayCGPA">0.00</span></p>
                        <p><strong>Status:</strong> <span id="displayStatus">-</span></p>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <button type="submit" class="btn btn-primary">💾 Save Result</button>
                        <button type="button" class="btn btn-info" onclick="resetForm()">🔄 Reset Form</button>
                    </div>
                </form>
            </div>
            
            <div id="viewTab" class="tab-content">
                <h2>All Student Results</h2>
                <div class="spinner" id="loadSpinner"></div>
                <div class="results-table">
                    <table id="resultsTable">
                        <thead>
                            <tr>
                                <th>Roll No</th>
                                <th>Student Name</th>
                                <th>CGPA</th>
                                <th>Status</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="resultsBody"></tbody>
                    </table>
                </div>
            </div>
            
            <div id="searchTab" class="tab-content">
                <h2>Search Student Result</h2>
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Enter Roll Number or Student Name...">
                    <button class="btn btn-primary" onclick="searchResults()">🔍 Search</button>
                </div>
                <div id="searchResults"></div>
            </div>
        </div>
        
        <footer>
            <p>&copy; 2025 Vellore Institute of Technology. All Rights Reserved.</p>
            <p>Developed for Academic Purpose | Result Management System v1.0 (Python Flask + MongoDB)</p>
        </footer>
    </div>

    <script>
        let subjectCount = 0;
        
        function calculateGrade(marks) {
            if (marks >= 90) return { grade: 'A+', gpa: 10 };
            if (marks >= 80) return { grade: 'A', gpa: 9 };
            if (marks >= 70) return { grade: 'B+', gpa: 8 };
            if (marks >= 60) return { grade: 'B', gpa: 7 };
            if (marks >= 50) return { grade: 'C', gpa: 6 };
            return { grade: 'F', gpa: 0 };
        }
        
        function calculateTotal(mse, ese) {
            return (parseFloat(mse) * 0.3) + (parseFloat(ese) * 0.7);
        }
        
        function addSubject() {
            subjectCount++;
            const container = document.getElementById('subjectsContainer');
            const subjectDiv = document.createElement('div');
            subjectDiv.className = 'subject-card';
            subjectDiv.id = `subject${subjectCount}`;
            
            subjectDiv.innerHTML = `
                <button type="button" class="remove-subject" onclick="removeSubject(${subjectCount})">✕ Remove</button>
                <h3>Subject ${subjectCount}</h3>
                <div class="subject-row">
                    <div class="form-group">
                        <label>Subject Name *</label>
                        <input type="text" class="subject-name" required>
                    </div>
                    <div class="form-group">
                        <label>MSE Marks (30%) *</label>
                        <input type="number" class="mse-marks" min="0" max="100" step="0.01" required 
                               onchange="updateCalculations()">
                    </div>
                    <div class="form-group">
                        <label>ESE Marks (70%) *</label>
                        <input type="number" class="ese-marks" min="0" max="100" step="0.01" required 
                               onchange="updateCalculations()">
                    </div>
                    <div class="form-group">
                        <label>Total Marks</label>
                        <input type="number" class="total-marks" readonly>
                    </div>
                    <div class="form-group">
                        <label>Grade</label>
                        <input type="text" class="grade" readonly>
                    </div>
                    <div class="form-group">
                        <label>GPA</label>
                        <input type="number" class="gpa" readonly>
                    </div>
                </div>
            `;
            
            container.appendChild(subjectDiv);
        }
        
        function removeSubject(id) {
            const subject = document.getElementById(`subject${id}`);
            if (subject) {
                subject.remove();
                updateCalculations();
            }
        }
        
        function updateCalculations() {
            const subjects = document.querySelectorAll('.subject-card');
            let totalGPA = 0;
            let subjectCount = 0;
            let hasFailed = false;
            
            subjects.forEach(subject => {
                const mse = parseFloat(subject.querySelector('.mse-marks').value) || 0;
                const ese = parseFloat(subject.querySelector('.ese-marks').value) || 0;
                
                if (mse < 0 || ese < 0 || mse > 100 || ese > 100) {
                    showAlert('Marks must be between 0 and 100', 'error');
                    return;
                }
                
                const total = calculateTotal(mse, ese);
                const gradeInfo = calculateGrade(total);
                
                subject.querySelector('.total-marks').value = total.toFixed(2);
                subject.querySelector('.grade').value = gradeInfo.grade;
                subject.querySelector('.gpa').value = gradeInfo.gpa;
                
                totalGPA += gradeInfo.gpa;
                subjectCount++;
                
                if (gradeInfo.grade === 'F') {
                    hasFailed = true;
                }
            });
            
            const cgpa = subjectCount > 0 ? (totalGPA / subjectCount).toFixed(2) : '0.00';
            const status = hasFailed ? 'Fail' : 'Pass';
            
            document.getElementById('displayCGPA').textContent = cgpa;
            document.getElementById('displayStatus').textContent = status;
            document.getElementById('displayStatus').className = hasFailed ? 'status-fail' : 'status-pass';
        }
        
        document.getElementById('resultForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const studentName = document.getElementById('studentName').value.trim();
            const rollNumber = document.getElementById('rollNumber').value.trim();
            
            if (!studentName || !rollNumber) {
                showAlert('Please enter student name and roll number', 'error');
                return;
            }
            
            const subjects = [];
            const subjectCards = document.querySelectorAll('.subject-card');
            
            if (subjectCards.length === 0) {
                showAlert('Please add at least one subject', 'error');
                return;
            }
            
            let isValid = true;
            subjectCards.forEach(card => {
                const subjectName = card.querySelector('.subject-name').value.trim();
                const mse = parseFloat(card.querySelector('.mse-marks').value);
                const ese = parseFloat(card.querySelector('.ese-marks').value);
                const total = parseFloat(card.querySelector('.total-marks').value);
                const grade = card.querySelector('.grade').value;
                const gpa = parseFloat(card.querySelector('.gpa').value);
                
                if (!subjectName || isNaN(mse) || isNaN(ese)) {
                    isValid = false;
                    return;
                }
                
                subjects.push({
                    name: subjectName,
                    mse: mse,
                    ese: ese,
                    total: total,
                    grade: grade,
                    gpa: gpa
                });
            });
            
            if (!isValid) {
                showAlert('Please fill all subject details correctly', 'error');
                return;
            }
            
            const cgpa = document.getElementById('displayCGPA').textContent;
            const status = document.getElementById('displayStatus').textContent;
            
            const data = {
                student_name: studentName,
                roll_number: rollNumber,
                subjects_json: JSON.stringify(subjects),
                cgpa: cgpa,
                status: status
            };
            
            try {
                const response = await fetch('/save_result', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAlert(result.message, 'success');
                    resetForm();
                    loadAllResults();
                } else {
                    showAlert(result.message, 'error');
                }
            } catch (error) {
                showAlert('Error saving result: ' + error.message, 'error');
            }
        });
        
        function resetForm() {
            document.getElementById('resultForm').reset();
            document.getElementById('subjectsContainer').innerHTML = '';
            subjectCount = 0;
            document.getElementById('displayCGPA').textContent = '0.00';
            document.getElementById('displayStatus').textContent = '-';
            document.getElementById('rollNumber').readOnly = false;
            
            for (let i = 0; i < 4; i++) {
                addSubject();
            }
        }
        
        async function loadAllResults() {
            const spinner = document.getElementById('loadSpinner');
            spinner.style.display = 'block';
            
            try {
                const response = await fetch('/get_all_results');
                const result = await response.json();
                
                if (result.success) {
                    displayResults(result.data);
                }
            } catch (error) {
                showAlert('Error loading results: ' + error.message, 'error');
            } finally {
                spinner.style.display = 'none';
            }
        }
        
        function displayResults(results) {
            const tbody = document.getElementById('resultsBody');
            tbody.innerHTML = '';
            
            if (results.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No results found</td></tr>';
                return;
            }
            
            results.forEach(result => {
                const row = document.createElement('tr');
                const statusClass = result.status === 'Pass' ? 'status-pass' : 'status-fail';
                const date = new Date(result.created_at).toLocaleDateString();
                
                row.innerHTML = `
                    <td>${result.roll_number}</td>
                    <td>${result.student_name}</td>
                    <td>${result.cgpa}</td>
                    <td class="${statusClass}">${result.status}</td>
                    <td>${date}</td>
                    <td>
                        <button class="btn btn-info" onclick='viewResult(${JSON.stringify(result).replace(/'/g, "&#39;")})'>👁 View</button>
                        <button class="btn btn-primary" onclick='editResult(${JSON.stringify(result).replace(/'/g, "&#39;")})'>✏ Edit</button>
                        <button class="btn btn-danger" onclick="deleteResult('${result.id}')">🗑 Delete</button>
                    </td>
                `;
                
                tbody.appendChild(row);
            });
        }
        
        function viewResult(result) {
            const subjects = JSON.parse(result.subjects_json);
            
            let subjectsHTML = '<table><thead><tr><th>Subject Name</th><th>MSE (30%)</th><th>ESE (70%)</th><th>Total</th><th>Grade</th><th>GPA</th></tr></thead><tbody>';
            
            subjects.forEach(subject => {
                subjectsHTML += `<tr><td>${subject.name}</td><td>${subject.mse}</td><td>${subject.ese}</td><td>${subject.total}</td><td>${subject.grade}</td><td>${subject.gpa}</td></tr>`;
            });
            
            subjectsHTML += '</tbody></table>';
            
            const statusClass = result.status === 'Pass' ? 'status-pass' : 'status-fail';
            const date = new Date(result.created_at).toLocaleDateString();
            
            const resultHTML = `
                <div class="result-card">
                    <div class="result-header">
                        <h2>VIT Semester Result</h2>
                        <p>Academic Year 2024-2025</p>
                    </div>
                    <div class="result-info">
                        <div class="info-item"><strong>Student Name:</strong> ${result.student_name}</div>
                        <div class="info-item"><strong>Roll Number:</strong> ${result.roll_number}</div>
                        <div class="info-item"><strong>Date:</strong> ${date}</div>
                        <div class="info-item"><strong>Status:</strong> <span class="${statusClass}">${result.status}</span></div>
                    </div>
                    <div class="subjects-table">
                        <h3>Subject-wise Details</h3>
                        ${subjectsHTML}
                    </div>
                    <div class="cgpa-section">
                        <h3>CGPA: ${result.cgpa}</h3>
                        <p>Final Result: ${result.status}</p>
                    </div>
                    <div style="margin-top: 20px; text-align: center;">
                        <button class="btn btn-primary" onclick="window.print()">🖨 Print / Download PDF</button>
                        <button class="btn btn-info" onclick="switchTab('view')">← Back to Results</button>
                    </div>
                </div>
            `;
            
            document.getElementById('searchResults').innerHTML = resultHTML;
            switchTab('search');
        }
        
        function editResult(result) {
            document.getElementById('studentName').value = result.student_name;
            document.getElementById('rollNumber').value = result.roll_number;
            document.getElementById('rollNumber').readOnly = true;
            
            const subjects = JSON.parse(result.subjects_json);
            document.getElementById('subjectsContainer').innerHTML = '';
            subjectCount = 0;
            
            subjects.forEach((subject, index) => {
                addSubject();
                const card = document.getElementById(`subject${index + 1}`);
                card.querySelector('.subject-name').value = subject.name;
                card.querySelector('.mse-marks').value = subject.mse;
                card.querySelector('.ese-marks').value = subject.ese;
                card.querySelector('.total-marks').value = subject.total.toFixed(2);
                card.querySelector('.grade').value = subject.grade;
                card.querySelector('.gpa').value = subject.gpa;
            });
            
            document.getElementById('displayCGPA').textContent = result.cgpa;
            document.getElementById('displayStatus').textContent = result.status;
            document.getElementById('displayStatus').className = result.status === 'Pass' ? 'status-pass' : 'status-fail';
            
            switchTab('entry');
            showAlert('Editing result for ' + result.student_name, 'success');
        }
        
        async function deleteResult(id) {
            if (!confirm('Are you sure you want to delete this result?')) {
                return;
            }
            
            try {
                const response = await fetch('/delete_result', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: id })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAlert(result.message, 'success');
                    loadAllResults();
                } else {
                    showAlert(result.message, 'error');
                }
            } catch (error) {
                showAlert('Error deleting result: ' + error.message, 'error');
            }
        }
        
        async function searchResults() {
            const searchTerm = document.getElementById('searchInput').value.trim();
            
            if (!searchTerm) {
                showAlert('Please enter search term', 'error');
                return;
            }
            
            try {
                const response = await fetch('/search_result', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ search_term: searchTerm })
                });
                
                const result = await response.json();
                
                if (result.success && result.data.length > 0) {
                    viewResult(result.data[0]);
                } else {
                    document.getElementById('searchResults').innerHTML = 
                        '<div class="alert alert-error">No results found for "' + searchTerm + '"</div>';
                }
            } catch (error) {
                showAlert('Error searching: ' + error.message, 'error');
            }
        }
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            if (tabName === 'entry') {
                document.getElementById('entryTab').classList.add('active');
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
            } else if (tabName === 'view') {
                document.getElementById('viewTab').classList.add('active');
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                loadAllResults();
            } else if (tabName === 'search') {
                document.getElementById('searchTab').classList.add('active');
                document.querySelectorAll('.tab-btn')[2].classList.add('active');
            }
        }
        
        function showAlert(message, type) {
            const container = document.getElementById('alertContainer');
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type}`;
            alertDiv.textContent = message;
            
            container.innerHTML = '';
            container.appendChild(alertDiv);
            
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
        
        window.onload = function() {
            for (let i = 0; i < 4; i++) {
                addSubject();
            }
            loadAllResults();
            
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchResults();
                }
            });
        };
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("=" * 60)
    print("🎓 VIT Semester Result Portal - Python Flask + MongoDB")
    print("=" * 60)
    print("\n📋 Setup Instructions:")
    print("1. Install required packages:")
    print("   pip install flask pymongo")
    print("\n2. Install MongoDB:")
    print("   - Download from: https://www.mongodb.com/try/download/community")
    print("   - Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas")
    print("\n3. Start MongoDB service:")
    print("   - Windows: Run MongoDB service from Services")
    print("   - Mac/Linux: mongod")
    print("\n4. Run this application:")
    print("   python app.py")
    print("\n5. Open browser and visit:")
    print("   http://localhost:5001")
    print("\n" + "=" * 60)
    print("✅ Starting Flask server...")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)