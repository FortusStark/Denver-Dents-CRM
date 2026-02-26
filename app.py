#!/usr/bin/env python3
"""
Denver Dents - CRM v5 with Customer Profiles
Complete customer view with documents and correspondence tracking

Run: python3 web_dashboard_v5_profiles.py
"""

from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for
from functools import wraps
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'ace-auto-crm-secret-key-change-in-production'

# Password protection
CRM_PASSWORD = "denverdents2026"

def check_auth():
    return session.get('authenticated')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_auth():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == CRM_PASSWORD:
            session['authenticated'] = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head><title>Login - Denver Dents CRM</title></head>
            <body style="font-family: Arial; max-width: 400px; margin: 100px auto; padding: 20px;">
                <h2 style="color: #dc3545;">‚ùå Incorrect Password</h2>
                <p><a href="/login" style="color: #007bff;">Try again</a></p>
            </body>
            </html>
        ''')
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head><title>Login - Denver Dents CRM</title></head>
        <body style="font-family: Arial; max-width: 400px; margin: 100px auto; padding: 20px; background: #f5f5f5;">
            <div style="background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="margin-bottom: 20px; color: #333;">üîí Denver Dents CRM</h2>
                <form method="post">
                    <input type="password" name="password" placeholder="Enter password" 
                           style="width: 100%; padding: 12px; margin: 10px 0; font-size: 16px; border: 1px solid #ddd; border-radius: 5px;" autofocus>
                    <button type="submit" style="width: 100%; padding: 12px; background: #007bff; 
                            color: white; border: none; font-size: 16px; cursor: pointer; border-radius: 5px;">
                        Login
                    </button>
                </form>
            </div>
        </body>
        </html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
CRM_FILE = 'jobs.json'

def load_crm():
    if not os.path.exists(CRM_FILE):
        return {"jobs": [], "stages": [], "lastUpdated": datetime.now().isoformat()}
    with open(CRM_FILE, 'r') as f:
        return json.load(f)

def save_crm(data):
    data['lastUpdated'] = datetime.now().isoformat()
    with open(CRM_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Enhanced Dashboard HTML with Customer Profiles
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Denver Dents CRM v5</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #ffffff;
            overflow-x: auto;
        }
        
        /* Header */
        .header {
            background: white;
            padding: 15px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        /* Filters */
        .filters {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }
        .filter-btn {
            padding: 6px 12px;
            border: 2px solid #dc0000;
            background: white;
            color: #dc0000;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: 600;
            transition: all 0.2s;
        }
        .filter-btn.active {
            background: #dc0000;
            color: white;
        }
        .filter-btn:hover {
            background: #ff0000;
            color: white;
            border-color: #ff0000;
        }
        .search-box {
            flex: 1;
            min-width: 200px;
            padding: 6px 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 0.9em;
        }
        
        /* Stats */
        .stats {
            display: flex;
            gap: 15px;
            margin-top: 10px;
            font-size: 0.9em;
            flex-wrap: wrap;
        }
        .stat {
            background: #f8f9fa;
            padding: 8px 15px;
            border-radius: 6px;
            font-weight: 600;
        }
        
        /* Kanban Board */
        .kanban-board {
            display: flex;
            padding: 20px;
            gap: 15px;
            min-height: calc(100vh - 200px);
            overflow-x: auto;
        }
        .stage-column {
            min-width: 300px;
            max-width: 300px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            transition: all 0.3s;
        }
        .stage-column.collapsed {
            min-width: 60px;
            max-width: 60px;
        }
        .stage-header {
            background: linear-gradient(135deg, #dc0000 0%, #000000 100%);
            color: white;
            padding: 15px;
            border-radius: 10px 10px 0 0;
            cursor: pointer;
            user-select: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
        }
        .stage-column.collapsed .stage-header {
            writing-mode: vertical-rl;
            padding: 15px 10px;
            border-radius: 10px;
        }
        .stage-count {
            background: rgba(255,255,255,0.3);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.85em;
        }
        .stage-column.collapsed .stage-count {
            display: none;
        }
        .jobs-container {
            flex: 1;
            padding: 12px;
            overflow-y: auto;
            max-height: calc(100vh - 280px);
        }
        .stage-column.collapsed .jobs-container {
            display: none;
        }
        
        /* RO Number Badges for Collapsed Columns */
        .ro-badges {
            display: none;
            flex-direction: column;
            gap: 4px;
            padding: 8px;
            align-items: center;
        }
        .stage-column.collapsed .ro-badges {
            display: flex;
        }
        .ro-badge-collapsed {
            background: white;
            color: #dc0000;
            font-weight: 700;
            font-size: 0.75em;
            padding: 4px 6px;
            border-radius: 4px;
            border: 2px solid #dc0000;
            cursor: pointer;
            transition: all 0.2s;
            min-width: 45px;
            text-align: center;
        }
        .ro-badge-collapsed:hover {
            background: #dc0000;
            color: white;
            transform: scale(1.1);
        }
        
        /* Job Cards */
        .job-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            border-left: 4px solid #dc0000;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }
        .job-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }
        
        /* Badges */
        .badges {
            display: flex;
            gap: 4px;
            margin-bottom: 6px;
            flex-wrap: wrap;
        }
        .badge {
            font-size: 0.7em;
            padding: 2px 6px;
            border-radius: 10px;
            font-weight: 600;
        }
        .badge-urgent { background: #dc3545; color: white; }
        .badge-overdue { background: #fd7e14; color: white; }
        .badge-arrived { background: #28a745; color: white; }
        .badge-not-arrived { background: #ffc107; color: #000; }
        .badge-parts { background: #17a2b8; color: white; }
        
        .days-badge {
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0,0,0,0.6);
            color: white;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.7em;
            font-weight: 600;
        }
        
        .job-customer {
            font-weight: bold;
            font-size: 1em;
            color: #333;
            margin-bottom: 4px;
        }
        .job-assigned {
            font-size: 0.75em;
            color: #666;
            margin-bottom: 4px;
        }
        .job-vehicle {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 4px;
        }
        .job-money {
            font-size: 0.9em;
            font-weight: 600;
            color: #28a745;
            margin-top: 6px;
        }
        
        /* Enhanced Modal for Customer Profiles */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            overflow-y: auto;
        }
        .modal.show {
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding: 20px;
        }
        .modal-content {
            background: white;
            border-radius: 12px;
            max-width: 1400px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            margin-top: 20px;
        }
        .modal-header {
            padding: 20px;
            border-bottom: 2px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            background: white;
            z-index: 10;
        }
        .modal-header h2 {
            color: #dc0000;
            font-size: 1.5em;
            font-weight: 700;
        }
        .close-btn {
            background: none;
            border: none;
            font-size: 2em;
            cursor: pointer;
            color: #999;
            line-height: 1;
        }
        .close-btn:hover {
            color: #dc0000;
        }
        
        /* Two Column Layout */
        .modal-body {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }
        
        /* Left Column */
        .left-column {
            border-right: 2px solid #f0f0f0;
            padding-right: 20px;
        }
        
        .profile-section {
            margin-bottom: 25px;
        }
        .section-title {
            font-size: 1.1em;
            font-weight: 700;
            color: #dc0000;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #dc0000;
        }
        
        /* Documents Section */
        .document-category {
            margin-bottom: 20px;
        }
        .category-header {
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            font-size: 0.95em;
        }
        .document-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .document-item {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-left: 3px solid #dc0000;
        }
        .doc-icon {
            font-size: 1.5em;
        }
        .doc-info {
            flex: 1;
        }
        .doc-name {
            font-weight: 600;
            color: #333;
            font-size: 0.9em;
        }
        .doc-meta {
            font-size: 0.75em;
            color: #666;
        }
        .doc-actions {
            display: flex;
            gap: 5px;
        }
        .doc-btn {
            padding: 4px 8px;
            background: #dc0000;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 0.75em;
            cursor: pointer;
        }
        .doc-btn:hover {
            background: #ff0000;
        }
        
        .upload-btn {
            width: 100%;
            padding: 12px;
            background: #dc0000;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
        }
        .upload-btn:hover {
            background: #ff0000;
        }
        
        /* Right Column - Tabbed Correspondence */
        .right-column {
            display: flex;
            flex-direction: column;
        }
        
        .correspondence-tabs {
            display: flex;
            gap: 10px;
            border-bottom: 3px solid #f0f0f0;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .correspondence-tab {
            flex: 1;
            padding: 12px 15px;
            background: #f8f9fa;
            border: 2px solid #ddd;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9em;
            text-align: center;
            transition: all 0.2s;
            color: #666;
        }
        .correspondence-tab:hover {
            background: #e9ecef;
            transform: translateY(-2px);
        }
        .correspondence-tab.active {
            background: white;
            border-bottom: 3px solid #dc0000;
            color: #333;
            font-weight: 700;
        }
        .correspondence-tab.insurance.active {
            border-bottom-color: #ffc107;
        }
        .correspondence-tab.team.active {
            border-bottom-color: #28a745;
        }
        .correspondence-tab.customer.active {
            border-bottom-color: #dc0000;
        }
        
        .correspondence-section {
            border: 2px solid #f0f0f0;
            border-radius: 8px;
            padding: 15px;
            display: none;
        }
        .correspondence-section.active {
            display: block;
        }
        .correspondence-header {
            font-weight: 700;
            color: #333;
            margin-bottom: 12px;
            font-size: 1em;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .add-correspondence-btn {
            padding: 4px 10px;
            background: #dc0000;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 0.8em;
            cursor: pointer;
        }
        .add-correspondence-btn:hover {
            background: #ff0000;
        }
        
        .correspondence-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-height: 300px;
            overflow-y: auto;
        }
        .correspondence-item {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 12px;
            border-left: 3px solid #17a2b8;
        }
        .correspondence-item.insurance {
            border-left-color: #ffc107;
        }
        .correspondence-item.team {
            border-left-color: #28a745;
        }
        .correspondence-item.customer {
            border-left-color: #dc0000;
        }
        .corr-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
        }
        .corr-who {
            font-weight: 600;
            font-size: 0.85em;
            color: #333;
        }
        .corr-when {
            font-size: 0.75em;
            color: #999;
        }
        .corr-content {
            font-size: 0.85em;
            color: #666;
            line-height: 1.4;
        }
        
        /* Form fields */
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
            font-size: 0.9em;
        }
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 0.9em;
        }
        .form-group textarea {
            min-height: 80px;
            resize: vertical;
        }
        
        /* Buttons */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9em;
        }
        .btn-primary {
            background: #dc0000;
            color: white;
        }
        .btn-primary:hover {
            background: #ff0000;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-success:hover {
            background: #218838;
        }
        
        /* Timeline */
        .timeline {
            margin-top: 20px;
        }
        .timeline-item {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            padding-left: 20px;
            border-left: 3px solid #dc0000;
        }
        .timeline-time {
            font-size: 0.75em;
            color: #999;
            min-width: 120px;
        }
        .timeline-content {
            flex: 1;
        }
        .timeline-stage {
            font-weight: 600;
            color: #333;
            margin-bottom: 4px;
        }
        .timeline-duration {
            font-size: 0.8em;
            color: #666;
        }
        
        /* Toast */
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: none;
            z-index: 2000;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { transform: translateX(100%); }
            to { transform: translateX(0); }
        }
        .toast.error {
            background: #dc3545;
        }
        
        .empty-state {
            text-align: center;
            padding: 30px 20px;
            color: #999;
            font-size: 0.9em;
        }
        
        /* Mobile responsive */
        @media (max-width: 1200px) {
            .modal-body {
                grid-template-columns: 1fr;
            }
            .left-column {
                border-right: none;
                border-bottom: 2px solid #f0f0f0;
                padding-right: 0;
                padding-bottom: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
            <div style="font-family: 'Arial Black', sans-serif;">
                <div style="font-size: 2em; font-weight: 900; color: #000; line-height: 0.9; letter-spacing: -1px;">ACE</div>
                <div style="font-size: 0.7em; font-weight: 700; color: #dc0000; letter-spacing: 2px;">AUTO HAIL REPAIR</div>
            </div>
            <div style="border-left: 2px solid #ddd; height: 40px;"></div>
            <h1 style="margin: 0; font-size: 1.3em; color: #dc0000;">CRM Dashboard</h1>
        </div>
        
        <div class="filters">
            <input type="text" class="search-box" id="searchBox" placeholder="üîç Search customer, vehicle..." oninput="applyFilters()">
            <button class="filter-btn active" id="filterAll" onclick="setFilter('all')">All</button>
            <button class="filter-btn" id="filterUrgent" onclick="setFilter('urgent')">üî¥ Urgent</button>
            <button class="filter-btn" id="filterMine" onclick="setFilter('mine')">My Jobs</button>
            <select class="filter-btn" style="padding: 4px 8px;" id="assignFilter" onchange="applyFilters()">
                <option value="">All People</option>
                <option value="Sales">Sales</option>
                <option value="R&I">R&I Tech</option>
                <option value="Manager">Manager</option>
                <option value="Owner">Owner</option>
            </select>
        </div>
        
        <div class="stats">
            <div class="stat">üìã <span id="totalJobs">0</span> Jobs</div>
            <div class="stat">üí∞ <span id="totalRevenue">$0</span> Revenue</div>
            <div class="stat">‚è≥ <span id="inProgress">0</span> Active</div>
            <div class="stat">üî¥ <span id="urgentCount">0</span> Urgent</div>
        </div>
    </div>

    <div class="kanban-board" id="kanban-board"></div>
    
    <!-- Enhanced Customer Profile Modal -->
    <div class="modal" id="jobModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Customer Profile</h2>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Content populated by JavaScript -->
            </div>
        </div>
    </div>
    
    <div class="toast" id="toast"></div>

    <script>
        let crmData = null;
        let collapsedStages = new Set();
        let currentFilter = 'all';
        let searchQuery = '';
        let assigneeFilter = '';
        let currentJobId = null;
        let corrScrollPositions = {}; // Store scroll positions for each tab
        
        function showToast(message, isError = false) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast' + (isError ? ' error' : '');
            toast.style.display = 'block';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }

        function formatMoney(amount) {
            return '$' + (amount || 0).toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ',');
        }

        function formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', {month: 'short', day: 'numeric', year: 'numeric'});
        }
        
        function formatDateTime(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', {month: 'short', day: 'numeric'}) + ' ' + 
                   date.toLocaleTimeString('en-US', {hour: 'numeric', minute: '2-digit'});
        }
        
        function getDaysInStage(job) {
            const timeline = job.timeline || [];
            if (timeline.length === 0) return 0;
            
            const lastChange = new Date(timeline[timeline.length - 1].timestamp);
            const now = new Date();
            const days = Math.floor((now - lastChange) / (1000 * 60 * 60 * 24));
            return days;
        }
        
        function getJobBadges(job) {
            const badges = [];
            const flags = job.flags || [];
            
            if (flags.includes('urgent')) {
                badges.push('<span class="badge badge-urgent">URGENT</span>');
            }
            
            const days = getDaysInStage(job);
            if (days > 7) {
                badges.push('<span class="badge badge-overdue">OVERDUE</span>');
            }
            
            if (job.stageData && job.stageData.arrived === true) {
                badges.push('<span class="badge badge-arrived">‚úì Arrived</span>');
            } else if (job.stageData && job.stageData.arrived === false) {
                badges.push('<span class="badge badge-not-arrived">‚è≥ Not Arrived</span>');
            }
            
            if (job.stageData && job.stageData.partsOrdered) {
                badges.push('<span class="badge badge-parts">Parts Ordered</span>');
            }
            
            return badges.join('');
        }
        
        function setFilter(filter) {
            currentFilter = filter;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('filter' + filter.charAt(0).toUpperCase() + filter.slice(1)).classList.add('active');
            applyFilters();
        }
        
        function applyFilters() {
            searchQuery = document.getElementById('searchBox').value.toLowerCase();
            assigneeFilter = document.getElementById('assignFilter').value;
            renderBoard();
        }
        
        function filterJobs(jobs) {
            return jobs.filter(job => {
                if (searchQuery) {
                    const searchable = (job.customerName + ' ' + job.vehicle + ' ' + job.phone).toLowerCase();
                    if (!searchable.includes(searchQuery)) return false;
                }
                
                if (assigneeFilter && job.assignedTo !== assigneeFilter) {
                    return false;
                }
                
                if (currentFilter === 'urgent') {
                    return (job.flags || []).includes('urgent');
                }
                if (currentFilter === 'mine') {
                    return job.assignedTo === 'Manager';
                }
                
                return true;
            });
        }

        function toggleStage(stageName) {
            const allStages = crmData.stages || [];
            collapsedStages.clear();
            allStages.forEach(stage => {
                if (stage !== stageName) {
                    collapsedStages.add(stage);
                }
            });
            renderBoard();
        }

        async function moveJobToStage(jobId, targetStage, event) {
            event.stopPropagation();
            try {
                const response = await fetch('/api/job/' + jobId + '/move', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({targetStage: targetStage})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast('‚úÖ Moved to ' + targetStage);
                    loadData();
                } else {
                    showToast('‚ùå ' + result.message, true);
                }
            } catch (err) {
                showToast('‚ùå Error: ' + err.message, true);
            }
        }
        
        function openJobModal(jobId) {
            currentJobId = jobId;
            const job = crmData.jobs.find(j => j.id === jobId);
            if (!job) return;
            
            const revenue = job.checkAmount || job.estimateAmount || job.invoiceAmount || 0;
            const timeline = job.timeline || [];
            const documents = job.documents || {photos: [], estimates: [], invoices: [], approvals: [], supplements: [], other: []};
            const correspondence = job.correspondence || {insurance: [], team: [], customer: []};
            
            let html = `
                <div class="left-column">
                    <!-- Main Info -->
                    <div class="profile-section">
                        <div class="section-title">üìã Customer Information</div>
                        <div class="form-group">
                            <label>RO Number</label>
                            <input type="text" value="${job.ro_number || '????'}" id="edit-ro" readonly style="background: #f0f0f0; font-weight: 700; color: #dc0000;">
                        </div>
                        <div class="form-group">
                            <label>Customer Name</label>
                            <input type="text" value="${job.customerName}" id="edit-customer">
                        </div>
                        <div class="form-group">
                            <label>Phone</label>
                            <input type="text" value="${job.phone}" id="edit-phone">
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="text" value="${job.email || ''}" id="edit-email">
                        </div>
                        <div class="form-group">
                            <label>Vehicle</label>
                            <input type="text" value="${job.vehicle}" id="edit-vehicle">
                        </div>
                        <div class="form-group">
                            <label>Current Stage</label>
                            <select id="edit-stage">
                                ${crmData.stages.map(s => `<option value="${s}" ${job.stage === s ? 'selected' : ''}>${s}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Assigned To</label>
                            <select id="edit-assigned">
                                <option value="">Unassigned</option>
                                <option value="Sales" ${job.assignedTo === 'Sales' ? 'selected' : ''}>Sales</option>
                                <option value="R&I" ${job.assignedTo === 'R&I' ? 'selected' : ''}>R&I Tech</option>
                                <option value="Manager" ${job.assignedTo === 'Manager' ? 'selected' : ''}>Manager</option>
                                <option value="Owner" ${job.assignedTo === 'Owner' ? 'selected' : ''}>Owner</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Revenue</label>
                            <input type="number" value="${revenue}" id="edit-revenue">
                        </div>
                        
                        <button class="btn btn-primary" onclick="saveJobDetails('${jobId}')" style="margin-right: 10px;">üíæ Save Changes</button>
                        <button class="btn btn-success" onclick="moveJobToNextStage('${jobId}')">‚û°Ô∏è Next Stage</button>
                    </div>
                    
                    <!-- Documents Section -->
                    <div class="profile-section">
                        <div class="section-title">üìé Attached Documents</div>
                        
                        <div class="document-category">
                            <div class="category-header">üì∏ Photos (${documents.photos.length})</div>
                            <div class="document-list">
                                ${documents.photos.length === 0 ? '<div class="empty-state">No photos yet</div>' : 
                                  documents.photos.map(doc => `
                                    <div class="document-item">
                                        <div class="doc-icon">üì∏</div>
                                        <div class="doc-info">
                                            <div class="doc-name">${doc.name}</div>
                                            <div class="doc-meta">Uploaded by ${doc.uploadedBy} ‚Ä¢ ${doc.stage} ‚Ä¢ ${formatDate(doc.date)}</div>
                                        </div>
                                        <div class="doc-actions">
                                            <button class="doc-btn">View</button>
                                        </div>
                                    </div>
                                  `).join('')}
                            </div>
                        </div>
                        
                        <div class="document-category">
                            <div class="category-header">üìÑ Estimates (${documents.estimates.length})</div>
                            <div class="document-list">
                                ${documents.estimates.length === 0 ? '<div class="empty-state">No estimates yet</div>' : 
                                  documents.estimates.map(doc => `
                                    <div class="document-item">
                                        <div class="doc-icon">üìÑ</div>
                                        <div class="doc-info">
                                            <div class="doc-name">${doc.name}</div>
                                            <div class="doc-meta">Uploaded by ${doc.uploadedBy} ‚Ä¢ ${doc.stage} ‚Ä¢ ${formatDate(doc.date)}</div>
                                        </div>
                                        <div class="doc-actions">
                                            <button class="doc-btn">View</button>
                                        </div>
                                    </div>
                                  `).join('')}
                            </div>
                        </div>
                        
                        <div class="document-category">
                            <div class="category-header">üìã Invoices (${documents.invoices.length})</div>
                            <div class="document-list">
                                ${documents.invoices.length === 0 ? '<div class="empty-state">No invoices yet</div>' : 
                                  documents.invoices.map(doc => `
                                    <div class="document-item">
                                        <div class="doc-icon">üìã</div>
                                        <div class="doc-info">
                                            <div class="doc-name">${doc.name}</div>
                                            <div class="doc-meta">Uploaded by ${doc.uploadedBy} ‚Ä¢ ${doc.stage} ‚Ä¢ ${formatDate(doc.date)}</div>
                                        </div>
                                        <div class="doc-actions">
                                            <button class="doc-btn">View</button>
                                        </div>
                                    </div>
                                  `).join('')}
                            </div>
                        </div>
                        
                        <div class="document-category">
                            <div class="category-header">‚úÖ Approvals (${documents.approvals.length})</div>
                            <div class="document-list">
                                ${documents.approvals.length === 0 ? '<div class="empty-state">No approvals yet</div>' : 
                                  documents.approvals.map(doc => `
                                    <div class="document-item">
                                        <div class="doc-icon">‚úÖ</div>
                                        <div class="doc-info">
                                            <div class="doc-name">${doc.name}</div>
                                            <div class="doc-meta">Uploaded by ${doc.uploadedBy} ‚Ä¢ ${doc.stage} ‚Ä¢ ${formatDate(doc.date)}</div>
                                        </div>
                                        <div class="doc-actions">
                                            <button class="doc-btn">View</button>
                                        </div>
                                    </div>
                                  `).join('')}
                            </div>
                        </div>
                        
                        <div class="document-category">
                            <div class="category-header">üìë Supplements (${documents.supplements.length})</div>
                            <div class="document-list">
                                ${documents.supplements.length === 0 ? '<div class="empty-state">No supplements yet</div>' : 
                                  documents.supplements.map(doc => `
                                    <div class="document-item">
                                        <div class="doc-icon">üìë</div>
                                        <div class="doc-info">
                                            <div class="doc-name">${doc.name}</div>
                                            <div class="doc-meta">Uploaded by ${doc.uploadedBy} ‚Ä¢ ${doc.stage} ‚Ä¢ ${formatDate(doc.date)}</div>
                                        </div>
                                        <div class="doc-actions">
                                            <button class="doc-btn">View</button>
                                        </div>
                                    </div>
                                  `).join('')}
                            </div>
                        </div>
                        
                        <button class="upload-btn" onclick="uploadDocument('${jobId}')">üì§ Upload Document</button>
                    </div>
                    
                    <!-- Timeline -->
                    <div class="profile-section">
                        <div class="section-title">üìä Timeline</div>
                        <div class="timeline">
            `;
            
            timeline.slice().reverse().forEach((entry, idx) => {
                const duration = idx < timeline.length - 1 ? 
                    Math.floor((new Date(entry.timestamp) - new Date(timeline[timeline.length - idx - 2].timestamp)) / (1000 * 60 * 60 * 24)) : 
                    getDaysInStage(job);
                
                html += `
                    <div class="timeline-item">
                        <div class="timeline-time">${formatDateTime(entry.timestamp)}</div>
                        <div class="timeline-content">
                            <div class="timeline-stage">${entry.stage}</div>
                            <div class="timeline-duration">${duration} day${duration !== 1 ? 's' : ''} ${idx === 0 ? '(current)' : ''}</div>
                        </div>
                    </div>
                `;
            });
            
            html += `
                        </div>
                    </div>
                </div>
                
                <div class="right-column">
                    <!-- Correspondence Tabs -->
                    <div class="correspondence-tabs">
                        <div class="correspondence-tab insurance active" onclick="switchCorrTab('${jobId}', 'insurance')">
                            üì® Insurance (${correspondence.insurance.length})
                        </div>
                        <div class="correspondence-tab team" onclick="switchCorrTab('${jobId}', 'team')">
                            üë• Team (${correspondence.team.length})
                        </div>
                        <div class="correspondence-tab customer" onclick="switchCorrTab('${jobId}', 'customer')">
                            üí¨ Customer (${correspondence.customer.length})
                        </div>
                    </div>
                    
                    <!-- Insurance Correspondence -->
                    <div class="correspondence-section insurance active" id="corr-insurance-${jobId}">
                        <div class="correspondence-header">
                            <span>üì® Insurance Correspondence</span>
                            <button class="add-correspondence-btn" onclick="addCorrespondence('${jobId}', 'insurance')">+ Add</button>
                        </div>
                        <div class="correspondence-list" id="corr-list-insurance-${jobId}">
                            ${correspondence.insurance.length === 0 ? 
                                '<div class="empty-state">No insurance correspondence yet</div>' :
                                correspondence.insurance.map(c => `
                                    <div class="correspondence-item insurance">
                                        <div class="corr-header">
                                            <div class="corr-who">${c.who}</div>
                                            <div class="corr-when">${formatDateTime(c.timestamp)}</div>
                                        </div>
                                        <div class="corr-content">${c.content}</div>
                                    </div>
                                `).join('')}
                        </div>
                    </div>
                    
                    <!-- Team Correspondence -->
                    <div class="correspondence-section team" id="corr-team-${jobId}">
                        <div class="correspondence-header">
                            <span>üë• Team Correspondence</span>
                            <button class="add-correspondence-btn" onclick="addCorrespondence('${jobId}', 'team')">+ Add</button>
                        </div>
                        <div class="correspondence-list" id="corr-list-team-${jobId}">
                            ${correspondence.team.length === 0 ? 
                                '<div class="empty-state">No team messages yet</div>' :
                                correspondence.team.map(c => `
                                    <div class="correspondence-item team">
                                        <div class="corr-header">
                                            <div class="corr-who">${c.who}</div>
                                            <div class="corr-when">${formatDateTime(c.timestamp)}</div>
                                        </div>
                                        <div class="corr-content">${c.content}</div>
                                    </div>
                                `).join('')}
                        </div>
                    </div>
                    
                    <!-- Customer Correspondence -->
                    <div class="correspondence-section customer" id="corr-customer-${jobId}">
                        <div class="correspondence-header">
                            <span>üí¨ Customer Correspondence</span>
                            <button class="add-correspondence-btn" onclick="addCorrespondence('${jobId}', 'customer')">+ Add</button>
                        </div>
                        <div class="correspondence-list" id="corr-list-customer-${jobId}">
                            ${correspondence.customer.length === 0 ? 
                                '<div class="empty-state">No customer correspondence yet</div>' :
                                correspondence.customer.map(c => `
                                    <div class="correspondence-item customer">
                                        <div class="corr-header">
                                            <div class="corr-who">${c.who}</div>
                                            <div class="corr-when">${formatDateTime(c.timestamp)}</div>
                                        </div>
                                        <div class="corr-content">${c.content}</div>
                                    </div>
                                `).join('')}
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('modalTitle').textContent = 'RO #' + (job.ro_number || '????') + ' - ' + job.customerName;
            document.getElementById('modalBody').innerHTML = html;
            document.getElementById('jobModal').classList.add('show');
            
            // Scroll insurance tab (default) to bottom (newest) on first open
            setTimeout(() => {
                const insuranceList = document.getElementById('corr-list-insurance-' + jobId);
                if (insuranceList) {
                    insuranceList.scrollTop = insuranceList.scrollHeight;
                }
            }, 100);
        }
        
        function closeModal() {
            document.getElementById('jobModal').classList.remove('show');
            currentJobId = null;
            corrScrollPositions = {}; // Clear scroll positions
        }
        
        function switchCorrTab(jobId, tabType) {
            // Save current scroll position
            const currentActive = document.querySelector('.correspondence-section.active');
            if (currentActive) {
                const listId = currentActive.querySelector('.correspondence-list').id;
                const list = document.getElementById(listId);
                if (list) {
                    corrScrollPositions[listId] = list.scrollTop;
                }
            }
            
            // Switch tabs
            document.querySelectorAll('.correspondence-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.correspondence-section').forEach(section => {
                section.classList.remove('active');
            });
            
            document.querySelector('.correspondence-tab.' + tabType).classList.add('active');
            document.getElementById('corr-' + tabType + '-' + jobId).classList.add('active');
            
            // Restore or set scroll position
            const newList = document.getElementById('corr-list-' + tabType + '-' + jobId);
            if (newList) {
                setTimeout(() => {
                    if (corrScrollPositions['corr-list-' + tabType + '-' + jobId] !== undefined) {
                        // Restore saved position
                        newList.scrollTop = corrScrollPositions['corr-list-' + tabType + '-' + jobId];
                    } else {
                        // First time opening - scroll to bottom (newest)
                        newList.scrollTop = newList.scrollHeight;
                    }
                }, 50);
            }
        }
        
        async function saveJobDetails(jobId) {
            const data = {
                customerName: document.getElementById('edit-customer').value,
                phone: document.getElementById('edit-phone').value,
                email: document.getElementById('edit-email').value,
                vehicle: document.getElementById('edit-vehicle').value,
                assignedTo: document.getElementById('edit-assigned').value,
                revenue: parseFloat(document.getElementById('edit-revenue').value),
                stage: document.getElementById('edit-stage').value
            };
            
            try {
                const response = await fetch('/api/job/' + jobId + '/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast('‚úÖ Saved!');
                    loadData();
                    // Re-open modal to show updates
                    setTimeout(() => openJobModal(jobId), 500);
                } else {
                    showToast('‚ùå ' + result.message, true);
                }
            } catch (err) {
                showToast('‚ùå Error: ' + err.message, true);
            }
        }
        
        async function moveJobToNextStage(jobId) {
            const job = crmData.jobs.find(j => j.id === jobId);
            if (!job) return;
            
            const currentIndex = crmData.stages.indexOf(job.stage);
            if (currentIndex < crmData.stages.length - 1) {
                await moveJobToStage(jobId, crmData.stages[currentIndex + 1], {stopPropagation: () => {}});
                closeModal();
            } else {
                showToast('Already at final stage', true);
            }
        }
        
        function uploadDocument(jobId) {
            const category = prompt('Document type?\\nOptions: photos, estimates, invoices, approvals, supplements, other');
            if (!category) return;
            
            const name = prompt('Document name/description:');
            if (!name) return;
            
            // In real implementation, this would handle file upload
            showToast('üì§ Document upload feature coming soon!');
        }
        
        function addCorrespondence(jobId, type) {
            const who = prompt('Who? (Name or company):');
            if (!who) return;
            
            const content = prompt('Summary of conversation:');
            if (!content) return;
            
            fetch('/api/job/' + jobId + '/correspondence', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    type: type,
                    who: who,
                    content: content
                })
            })
            .then(r => r.json())
            .then(result => {
                if (result.success) {
                    showToast('‚úÖ Added correspondence');
                    loadData();
                    setTimeout(() => openJobModal(jobId), 500);
                } else {
                    showToast('‚ùå Error', true);
                }
            });
        }

        function renderBoard() {
            if (!crmData) return;

            const board = document.getElementById('kanban-board');
            const stages = crmData.stages || [];
            let jobs = crmData.jobs || [];
            
            jobs = filterJobs(jobs);
            
            board.innerHTML = '';
            
            stages.forEach((stage, stageIndex) => {
                const stageJobs = jobs.filter(j => j.stage === stage)
                                      .sort((a, b) => {
                                          const dateA = new Date(a.updatedAt || a.createdAt);
                                          const dateB = new Date(b.updatedAt || b.createdAt);
                                          return dateB - dateA;
                                      });
                
                const isCollapsed = collapsedStages.has(stage);
                
                const column = document.createElement('div');
                column.className = 'stage-column' + (isCollapsed ? ' collapsed' : '');
                column.setAttribute('data-stage', stage);
                
                column.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    column.style.background = '#f0f0f0';
                });
                column.addEventListener('dragleave', () => {
                    column.style.background = 'white';
                });
                column.addEventListener('drop', (e) => {
                    e.preventDefault();
                    column.style.background = 'white';
                    const jobId = e.dataTransfer.getData('text/plain');
                    moveJobToStage(jobId, stage, e);
                });
                
                const header = document.createElement('div');
                header.className = 'stage-header';
                header.onclick = () => toggleStage(stage);
                header.innerHTML = `
                    <div class="stage-title">${stageIndex + 1}. ${stage}</div>
                    <div class="stage-count">${stageJobs.length}</div>
                `;
                column.appendChild(header);
                
                const container = document.createElement('div');
                container.className = 'jobs-container';
                
                // Add RO badges for collapsed view
                const roBadges = document.createElement('div');
                roBadges.className = 'ro-badges';
                stageJobs.forEach(job => {
                    const badge = document.createElement('div');
                    badge.className = 'ro-badge-collapsed';
                    badge.textContent = job.ro_number || '????';
                    badge.title = job.customerName;
                    badge.onclick = (e) => {
                        e.stopPropagation();
                        openJobModal(job.id);
                    };
                    roBadges.appendChild(badge);
                });
                column.appendChild(roBadges);
                
                if (stageJobs.length === 0) {
                    container.innerHTML = '<div class="empty-state">No jobs</div>';
                } else {
                    stageJobs.forEach(job => {
                        const card = document.createElement('div');
                        card.className = 'job-card';
                        card.draggable = true;
                        card.onclick = () => openJobModal(job.id);
                        
                        card.addEventListener('dragstart', (e) => {
                            e.dataTransfer.setData('text/plain', job.id);
                            card.classList.add('dragging');
                        });
                        card.addEventListener('dragend', () => {
                            card.classList.remove('dragging');
                        });
                        
                        const revenue = job.checkAmount || job.estimateAmount || job.invoiceAmount || 0;
                        const days = getDaysInStage(job);
                        
                        card.innerHTML = `
                            ${getJobBadges(job)}
                            ${days > 0 ? `<div class="days-badge">${days}d</div>` : ''}
                            <div class="job-customer">RO #${job.ro_number || '????'} - ${job.customerName}</div>
                            ${job.assignedTo ? `<div class="job-assigned">üë§ ${job.assignedTo}</div>` : ''}
                            <div class="job-vehicle">üöó ${job.vehicle}</div>
                            ${revenue > 0 ? `<div class="job-money">üí∞ ${formatMoney(revenue)}</div>` : ''}
                        `;
                        
                        container.appendChild(card);
                    });
                }
                
                column.appendChild(container);
                board.appendChild(column);
            });
        }

        function updateStats(data) {
            const jobs = data.jobs || [];
            const totalRevenue = jobs.reduce((sum, j) => sum + (j.checkAmount || j.estimateAmount || 0), 0);
            const inProgress = jobs.filter(j => !['Completed', 'Paid/Closed'].includes(j.stage)).length;
            const urgent = jobs.filter(j => (j.flags || []).includes('urgent')).length;
            
            document.getElementById('totalJobs').textContent = jobs.length;
            document.getElementById('totalRevenue').textContent = formatMoney(totalRevenue);
            document.getElementById('inProgress').textContent = inProgress;
            document.getElementById('urgentCount').textContent = urgent;
        }

        async function loadData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                crmData = data;
                updateStats(data);
                renderBoard();
            } catch (err) {
                console.error('Error loading data:', err);
            }
        }

        // Initialize
        loadData();
        setInterval(loadData, 30000);
        
        // Close modal on outside click
        document.getElementById('jobModal').addEventListener('click', (e) => {
            if (e.target.id === 'jobModal') closeModal();
        });
    </script>
</body>
</html>
"""

@app.route('/')
@login_required
def index():
    return render_template_string(DASHBOARD_HTML)

@login_required
@app.route('/api/data')
def api_data():
    return jsonify(load_crm())

@login_required
@app.route('/api/job/<job_id>/move', methods=['POST'])
def move_job(job_id):
    """Move job to target stage"""
    try:
        data = load_crm()
        target_stage = request.json.get('targetStage')
        
        job = next((j for j in data['jobs'] if j['id'] == job_id), None)
        if not job:
            return jsonify({'success': False, 'message': 'Job not found'})
        
        if 'timeline' not in job:
            job['timeline'] = []
        
        job['timeline'].append({
            'stage': target_stage,
            'timestamp': datetime.now().isoformat(),
            'changedBy': 'User'
        })
        
        job['stage'] = target_stage
        job['updatedAt'] = datetime.now().isoformat()
        
        save_crm(data)
        return jsonify({'success': True, 'newStage': target_stage})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@login_required
@app.route('/api/job/<job_id>/update', methods=['POST'])
def update_job(job_id):
    """Update job details"""
    try:
        data = load_crm()
        updates = request.json
        
        job = next((j for j in data['jobs'] if j['id'] == job_id), None)
        if not job:
            return jsonify({'success': False, 'message': 'Job not found'})
        
        # Update fields
        if 'customerName' in updates:
            job['customerName'] = updates['customerName']
        if 'phone' in updates:
            job['phone'] = updates['phone']
        if 'email' in updates:
            job['email'] = updates['email']
        if 'vehicle' in updates:
            job['vehicle'] = updates['vehicle']
        if 'assignedTo' in updates:
            job['assignedTo'] = updates['assignedTo']
        if 'revenue' in updates:
            job['checkAmount'] = updates['revenue']
        if 'stage' in updates and updates['stage'] != job['stage']:
            # Stage change - add to timeline
            if 'timeline' not in job:
                job['timeline'] = []
            job['timeline'].append({
                'stage': updates['stage'],
                'timestamp': datetime.now().isoformat(),
                'changedBy': 'User'
            })
            job['stage'] = updates['stage']
        
        job['updatedAt'] = datetime.now().isoformat()
        
        save_crm(data)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@login_required
@app.route('/api/job/<job_id>/correspondence', methods=['POST'])
def add_correspondence(job_id):
    """Add correspondence to a job"""
    try:
        data = load_crm()
        corr_data = request.json
        
        job = next((j for j in data['jobs'] if j['id'] == job_id), None)
        if not job:
            return jsonify({'success': False, 'message': 'Job not found'})
        
        if 'correspondence' not in job:
            job['correspondence'] = {'insurance': [], 'team': [], 'customer': []}
        
        corr_type = corr_data.get('type')
        if corr_type not in ['insurance', 'team', 'customer']:
            return jsonify({'success': False, 'message': 'Invalid correspondence type'})
        
        job['correspondence'][corr_type].append({
            'who': corr_data.get('who'),
            'content': corr_data.get('content'),
            'timestamp': datetime.now().isoformat()
        })
        
        job['updatedAt'] = datetime.now().isoformat()
        
        save_crm(data)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("üöó ACE AUTO HAIL REPAIR - CRM v5 with Customer Profiles")
    print("="*70)
    print("\n‚ú® NEW FEATURE: Complete Customer Profiles!")
    print("\nüìã Left Column:")
    print("  ‚Ä¢ Customer information (editable)")
    print("  ‚Ä¢ Attached documents by category")
    print("    - Photos, Estimates, Invoices")
    print("    - Approvals, Supplements, Other")
    print("  ‚Ä¢ Timeline view")
    print("\nüí¨ Right Column:")
    print("  ‚Ä¢ Insurance correspondence")
    print("  ‚Ä¢ Team correspondence")
    print("  ‚Ä¢ Customer correspondence")
    print("\nüì± Access:")
    print("  http://localhost:5000")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
