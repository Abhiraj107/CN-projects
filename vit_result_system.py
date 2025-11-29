"""
VIT Result Management System - Complete Application
Semester V (AIML) - MongoDB + Streamlit

Installation:
pip install streamlit pymongo pandas plotly

Run:
streamlit run vit_result_system.py
"""

import streamlit as st
from pymongo import MongoClient, ASCENDING
from datetime import datetime
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Optional

# ============================================
# MongoDB Configuration
# ============================================

class Database:
    def __init__(self):
        # Connect to MongoDB (localhost by default)
        try:
            # Read MongoDB connection URI from environment variable for flexibility
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client['vit_result_system']
            
            # Test connection
            self.client.server_info()
            
            # Initialize collections
            self.students = self.db['students']
            self.subjects = self.db['subjects']
            self.marks = self.db['marks']
            
            # Create indexes
            self._create_indexes()
            
            # Initialize default data if empty
            self._initialize_data()
            
        except Exception as e:
            st.error(f"❌ MongoDB Connection Error: {e}")
            st.info("💡 Make sure MongoDB is running on localhost:27017")
            st.stop()
    
    def _create_indexes(self):
        """Create unique indexes"""
        try:
            self.students.create_index([("rollNo", ASCENDING)], unique=True)
            self.students.create_index([("email", ASCENDING)], unique=True)
            self.subjects.create_index([("code", ASCENDING)], unique=True)
            self.marks.create_index([("studentId", ASCENDING), ("subjectId", ASCENDING)], unique=True)
        except:
            pass  # Indexes might already exist
    
    def _initialize_data(self):
        """Initialize subjects if database is empty"""
        if self.subjects.count_documents({}) == 0:
            default_subjects = [
                {"subjectName": "Computer Network Technology", "code": "ML3001"},
                {"subjectName": "Design and Analysis of Algorithms", "code": "ML3002"},
                {"subjectName": "Machine Learning", "code": "ML3003"},
                {"subjectName": "Cloud Computing", "code": "ML3004"}
            ]
            self.subjects.insert_many(default_subjects)

# ============================================
# Business Logic Functions
# ============================================

def calculate_grade(total: float) -> str:
    """Calculate grade based on total marks (total is already on 100 scale)"""
    if total >= 90:
        return "A+"
    elif total >= 80:
        return "A"
    elif total >= 70:
        return "B+"
    elif total >= 60:
        return "B"
    elif total >= 50:
        return "C"
    else:
        return "F"

def get_grade_color(grade: str) -> str:
    """Get color for grade display"""
    colors = {
        "A+": "#10b981",  # green
        "A": "#22c55e",
        "B+": "#3b82f6",  # blue
        "B": "#60a5fa",
        "C": "#f59e0b",   # yellow
        "F": "#ef4444"    # red
    }
    return colors.get(grade, "#6b7280")

# ============================================
# CRUD Operations
# ============================================

class StudentService:
    def __init__(self, db: Database):
        self.db = db
    
    def add_student(self, roll_no: str, name: str, email: str) -> bool:
        """Add new student"""
        try:
            student = {
                "rollNo": roll_no,
                "name": name,
                "email": email,
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
            self.db.students.insert_one(student)
            return True
        except Exception as e:
            st.error(f"Error adding student: {e}")
            return False
    
    def get_all_students(self) -> List[Dict]:
        """Get all students"""
        return list(self.db.students.find({}, {"_id": 0}).sort("rollNo", ASCENDING))
    
    def get_student_by_roll_no(self, roll_no: str) -> Optional[Dict]:
        """Get student by roll number"""
        return self.db.students.find_one({"rollNo": roll_no}, {"_id": 0})
    
    def update_student(self, roll_no: str, name: str, email: str) -> bool:
        """Update student details"""
        try:
            result = self.db.students.update_one(
                {"rollNo": roll_no},
                {"$set": {"name": name, "email": email, "updatedAt": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception as e:
            st.error(f"Error updating student: {e}")
            return False
    
    def delete_student(self, roll_no: str) -> bool:
        """Delete student and all their marks"""
        try:
            # Delete student's marks first
            self.db.marks.delete_many({"studentId": roll_no})
            # Delete student
            result = self.db.students.delete_one({"rollNo": roll_no})
            return result.deleted_count > 0
        except Exception as e:
            st.error(f"Error deleting student: {e}")
            return False

class SubjectService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_subjects(self) -> List[Dict]:
        """Get all subjects"""
        return list(self.db.subjects.find({}, {"_id": 0}))

class MarkService:
    def __init__(self, db: Database):
        self.db = db
    
    def add_or_update_marks(self, student_id: str, subject_id: str, mse: float, ese: float) -> bool:
        """Add or update marks for a student"""
        try:
            # Convert to percentage first (MSE out of 30, ESE out of 70)
            mse_percent = (mse / 30) * 30  # Convert to percentage of total contribution
            ese_percent = (ese / 70) * 70  # Convert to percentage of total contribution
            total = mse_percent + ese_percent
            grade = calculate_grade(total)
            
            mark = {
                "studentId": student_id,
                "subjectId": subject_id,
                "mseMarks": mse,
                "eseMarks": ese,
                "total": round(total, 2),
                "grade": grade,
                "updatedAt": datetime.now()
            }
            
            self.db.marks.update_one(
                {"studentId": student_id, "subjectId": subject_id},
                {"$set": mark, "$setOnInsert": {"createdAt": datetime.now()}},
                upsert=True
            )
            return True
        except Exception as e:
            st.error(f"Error saving marks: {e}")
            return False
    
    def get_student_marks(self, student_id: str) -> List[Dict]:
        """Get all marks for a student with subject details"""
        pipeline = [
            {"$match": {"studentId": student_id}},
            {
                "$lookup": {
                    "from": "subjects",
                    "localField": "subjectId",
                    "foreignField": "code",
                    "as": "subject"
                }
            },
            {"$unwind": "$subject"},
            {
                "$project": {
                    "_id": 0,
                    "subjectCode": "$subjectId",
                    "subjectName": "$subject.subjectName",
                    "mseMarks": 1,
                    "eseMarks": 1,
                    "total": 1,
                    "grade": 1
                }
            },
            {"$sort": {"subjectCode": 1}}
        ]
        return list(self.db.marks.aggregate(pipeline))
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        total_students = self.db.students.count_documents({})
        
        # Get class average
        avg_pipeline = [
            {"$group": {"_id": None, "average": {"$avg": "$total"}}}
        ]
        avg_result = list(self.db.marks.aggregate(avg_pipeline))
        class_average = round(avg_result[0]["average"], 2) if avg_result else 0
        
        # Get top scorer
        top_pipeline = [
            {
                "$group": {
                    "_id": "$studentId",
                    "avgMarks": {"$avg": "$total"}
                }
            },
            {"$sort": {"avgMarks": -1}},
            {"$limit": 1}
        ]
        top_result = list(self.db.marks.aggregate(top_pipeline))
        
        top_scorer = None
        if top_result:
            top_student_id = top_result[0]["_id"]
            top_scorer = self.db.students.find_one({"rollNo": top_student_id}, {"_id": 0})
        
        return {
            "total_students": total_students,
            "class_average": class_average,
            "top_scorer": top_scorer
        }

# ============================================
# Streamlit UI
# ============================================

def init_session_state():
    """Initialize session state variables"""
    if 'db' not in st.session_state:
        st.session_state.db = Database()
    if 'student_service' not in st.session_state:
        st.session_state.student_service = StudentService(st.session_state.db)
    if 'subject_service' not in st.session_state:
        st.session_state.subject_service = SubjectService(st.session_state.db)
    if 'mark_service' not in st.session_state:
        st.session_state.mark_service = MarkService(st.session_state.db)

def show_dashboard():
    """Dashboard page"""
    st.title("🎓 VIT Result Management System")
    st.subheader("Semester V - AIML Department")
    
    # Get statistics
    stats = st.session_state.mark_service.get_dashboard_stats()
    
    # Display stats in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="👥 Total Students",
            value=stats['total_students']
        )
    
    with col2:
        if stats['top_scorer']:
            st.metric(
                label="🏆 Top Scorer",
                value=stats['top_scorer']['name']
            )
            st.caption(f"Roll No: {stats['top_scorer']['rollNo']}")
        else:
            st.metric(label="🏆 Top Scorer", value="N/A")
    
    with col3:
        st.metric(
            label="📊 Class Average",
            value=f"{stats['class_average']}%"
        )
    
    st.divider()
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Student", type="primary", use_container_width=True):
            # Set page in session state and trigger rerun
            st.session_state["navigation"] = "👥 Students"
            st.rerun()
    
    with col2:
        if st.button("📝 Enter Marks", type="primary", use_container_width=True):
            # Set page in session state and trigger rerun
            st.session_state["navigation"] = "📝 Marks Entry"
            st.rerun()
    
    with col3:
        if st.button("🔍 View Results", type="primary", use_container_width=True):
            # Set page in session state and trigger rerun
            st.session_state["navigation"] = "🔍 Results"
            st.rerun()
    
    # Show recent students
    st.divider()
    st.subheader("📋 All Students")
    students = st.session_state.student_service.get_all_students()
    
    if students:
        df = pd.DataFrame(students)
        df = df[['rollNo', 'name', 'email']]
        df.columns = ['Roll Number', 'Name', 'Email']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No students found. Add your first student!")

def show_students():
    """Students management page"""
    st.title("👥 Students Management")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Student", "📝 Edit Student", "🗑️ Delete Student"])
    
    # Add Student Tab
    with tab1:
        st.subheader("Add New Student")
        with st.form("add_student_form"):
            roll_no = st.text_input("Roll Number *", placeholder="e.g., 21AIML001")
            name = st.text_input("Name *", placeholder="e.g., John Doe")
            email = st.text_input("Email *", placeholder="e.g., john.doe@vit.edu")
            
            submitted = st.form_submit_button("Add Student", use_container_width=True, type="primary")
            
            if submitted:
                if roll_no and name and email:
                    if st.session_state.student_service.add_student(roll_no, name, email):
                        st.success(f"✅ Student {name} added successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Failed to add student. Roll number or email might already exist.")
                else:
                    st.warning("⚠️ Please fill all required fields.")
    
    # Edit Student Tab
    with tab2:
        st.subheader("Edit Student Details")
        students = st.session_state.student_service.get_all_students()
        
        if students:
            student_options = {f"{s['rollNo']} - {s['name']}": s['rollNo'] for s in students}
            selected_student = st.selectbox("Select Student", options=list(student_options.keys()))
            
            if selected_student:
                roll_no = student_options[selected_student]
                student = st.session_state.student_service.get_student_by_roll_no(roll_no)
                
                with st.form("edit_student_form"):
                    st.text_input("Roll Number", value=student['rollNo'], disabled=True)
                    new_name = st.text_input("Name *", value=student['name'])
                    new_email = st.text_input("Email *", value=student['email'])
                    
                    submitted = st.form_submit_button("Update Student", use_container_width=True, type="primary")
                    
                    if submitted:
                        if new_name and new_email:
                            if st.session_state.student_service.update_student(roll_no, new_name, new_email):
                                st.success("✅ Student updated successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to update student.")
                        else:
                            st.warning("⚠️ Please fill all required fields.")
        else:
            st.info("No students available to edit.")
    
    # Delete Student Tab
    with tab3:
        st.subheader("Delete Student")
        st.warning("⚠️ This will delete the student and all their marks permanently!")
        
        students = st.session_state.student_service.get_all_students()
        
        if students:
            student_options = {f"{s['rollNo']} - {s['name']}": s['rollNo'] for s in students}
            selected_student = st.selectbox("Select Student to Delete", options=list(student_options.keys()))
            
            if selected_student:
                roll_no = student_options[selected_student]
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("🗑️ Delete", type="primary", use_container_width=True):
                        if st.session_state.student_service.delete_student(roll_no):
                            st.success("✅ Student deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete student.")
        else:
            st.info("No students available to delete.")

def show_marks():
    """Marks entry page"""
    st.title("📝 Enter Marks")
    
    students = st.session_state.student_service.get_all_students()
    subjects = st.session_state.subject_service.get_all_subjects()
    
    if not students:
        st.warning("⚠️ No students found. Please add students first.")
        return
    
    # Student selection outside form to trigger reloads
    student_options = {f"{s['rollNo']} - {s['name']}": s['rollNo'] for s in students}
    selected_student = st.selectbox("Select Student *", options=list(student_options.keys()))
    student_id = student_options[selected_student]
    
    # Subject selection outside form to trigger reloads
    subject_options = {f"{s['code']} - {s['subjectName']}": s['code'] for s in subjects}
    selected_subject = st.selectbox("Select Subject *", options=list(subject_options.keys()))
    subject_id = subject_options[selected_subject]
    
    # Get existing marks if any
    existing_marks = st.session_state.mark_service.get_student_marks(student_id)
    current_marks = next((m for m in existing_marks if m['subjectCode'] == subject_id), None)

    def _normalize_mark(value, max_mark):
        """Normalize stored mark to a display value within 0..max_mark.

        Handles cases where values were saved as fractions (0..1) or
        accidentally scaled. Will clamp to [0, max_mark].
        """
        try:
            v = float(value)
        except Exception:
            return 0.0

        # If value looks like a fraction (0 < v <= 1), scale to full mark
        if 0 < v <= 1:
            v = v * max_mark

        # If value is very small but likely intended as a larger integer (e.g. 0.0055 -> 55),
        # try repeatedly scaling by 100 until it is within a plausible range or exceeds max_mark.
        # This recovers cases where values were accidentally divided by 100 or 10000 when saved.
        attempts = 0
        while v < 1 and attempts < 4:
            v *= 100
            attempts += 1

        # Finally clamp to valid range
        if v < 0:
            v = 0.0
        if v > max_mark:
            # don't silently overflow: clamp but note it
            v = float(max_mark)

        return round(v, 2)

    if current_marks:
        st.info(f"📝 Existing marks found for {selected_subject.split(' - ')[1]}")
    
    with st.form("marks_form"):
        # Use text inputs so empty placeholder shows up and disappears on focus
        col1, col2 = st.columns(2)
        with col1:
            mse_default_val = _normalize_mark(current_marks['mseMarks'], 30) if current_marks else None
            mse_text = st.text_input(
                "MSE Marks (out of 30) *",
                value=f"{mse_default_val:.2f}" if mse_default_val is not None else "",
                placeholder="0.00",
                key=f"mse_text_{student_id}_{subject_id}"
            )
        with col2:
            ese_default_val = _normalize_mark(current_marks['eseMarks'], 70) if current_marks else None
            ese_text = st.text_input(
                "ESE Marks (out of 70) *",
                value=f"{ese_default_val:.2f}" if ese_default_val is not None else "",
                placeholder="0.00",
                key=f"ese_text_{student_id}_{subject_id}"
            )

        # Parse inputs
        parse_ok = True
        mse_num = 0.0
        ese_num = 0.0
        if mse_text and mse_text.strip() != "":
            try:
                mse_num = float(mse_text)
            except Exception:
                st.error("Invalid MSE value — please enter a number between 0 and 30.")
                parse_ok = False
        if ese_text and ese_text.strip() != "":
            try:
                ese_num = float(ese_text)
            except Exception:
                st.error("Invalid ESE value — please enter a number between 0 and 70.")
                parse_ok = False

        # Validate ranges
        if parse_ok:
            if mse_num < 0 or mse_num > 30:
                st.error("MSE must be between 0 and 30.")
                parse_ok = False
            if ese_num < 0 or ese_num > 70:
                st.error("ESE must be between 0 and 70.")
                parse_ok = False

        # Preview calculation
        if parse_ok and (mse_num > 0 or ese_num > 0):
            # Values already in mark-scale, total is simple sum
            total = round(mse_num + ese_num, 2)
            grade = calculate_grade(total)

            st.divider()
            st.subheader("📊 Preview")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Total Marks", f"{total:.2f}/100")
            with c2:
                st.markdown(f"**Grade:** <span style='color: {get_grade_color(grade)}; font-size: 24px; font-weight: bold;'>{grade}</span>", unsafe_allow_html=True)

            # Show change if editing existing marks
            if current_marks:
                old_total = float(current_marks['total'])
                change = total - old_total
                if abs(change) > 0.01:
                    st.caption(f"{'📈' if change > 0 else '📉'} Change from previous: {change:+.2f}")

        submitted = st.form_submit_button(
            "📝 Update Marks" if current_marks else "💾 Save Marks",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            if not parse_ok:
                st.error("Fix input errors before submitting.")
            else:
                # Save numeric values (mse_num and ese_num)
                if st.session_state.mark_service.add_or_update_marks(student_id, subject_id, mse_num, ese_num):
                    st.success("✅ Marks saved successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to save marks.")

def show_results():
    """Results view page"""
    st.title("🔍 View Results")
    
    students = st.session_state.student_service.get_all_students()
    
    if not students:
        st.warning("⚠️ No students found.")
        return
    
    # Search student
    student_options = {f"{s['rollNo']} - {s['name']}": s['rollNo'] for s in students}
    selected_student = st.selectbox("Search Student by Roll Number", options=list(student_options.keys()))
    
    if selected_student:
        roll_no = student_options[selected_student]
        student = st.session_state.student_service.get_student_by_roll_no(roll_no)
        marks = st.session_state.mark_service.get_student_marks(roll_no)
        
        # Student Header
        st.divider()
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📋 {student['name']}")
            st.text(f"Roll No: {student['rollNo']}")
            st.text(f"Email: {student['email']}")
        
        if marks:
            # Calculate overall stats
            total_avg = sum(m['total'] for m in marks) / len(marks)
            overall_grade = calculate_grade(total_avg)
            
            with col2:
                st.metric("Overall Percentage", f"{total_avg:.2f}%")
                st.markdown(f"**Overall Grade:** <span style='color: {get_grade_color(overall_grade)}; font-size: 28px; font-weight: bold;'>{overall_grade}</span>", unsafe_allow_html=True)
            
            st.divider()
            
            # Marks Table
            st.subheader("📊 Subject-wise Performance")
            df = pd.DataFrame(marks)

            # Rename columns explicitly (use mapping instead of positional rename)
            df_display = df.rename(columns={
                'subjectCode': 'Subject Code',
                'subjectName': 'Subject Name',
                'mseMarks': 'MSE (30)',
                'eseMarks': 'ESE (70)',
                'total': 'Total (100)',
                'grade': 'Grade'
            })

            # Ensure columns appear in the desired order
            desired_cols = ['Subject Code', 'Subject Name', 'MSE (30)', 'ESE (70)', 'Total (100)', 'Grade']
            df_display = df_display[[c for c in desired_cols if c in df_display.columns]]

            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Visualization
            st.divider()
            st.subheader("📈 Performance Chart")
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[m['subjectCode'] for m in marks],
                y=[m['total'] for m in marks],
                text=[m['grade'] for m in marks],
                textposition='outside',
                marker_color=[get_grade_color(m['grade']) for m in marks],
                name='Total Marks'
            ))
            
            fig.update_layout(
                title="Subject-wise Total Marks",
                xaxis_title="Subject",
                yaxis_title="Total Marks (out of 100)",
                yaxis=dict(range=[0, 110]),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("📝 No marks entered for this student yet.")

def show_subjects():
    """Subjects view page"""
    st.title("📚 Semester V Subjects (AIML)")
    
    subjects = st.session_state.subject_service.get_all_subjects()
    
    for i, subject in enumerate(subjects):
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"### {subject['code']}")
        with col2:
            st.markdown(f"### {subject['subjectName']}")
        
        if i < len(subjects) - 1:
            st.divider()

# ============================================
# Main App
# ============================================

def main():
    # Page config
    st.set_page_config(
        page_title="VIT Result Management System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Dark theme with modern gradient styling
    st.markdown("""
        <style>
        /* Main background */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1a202c 50%, #16213e 100%);
            color: #e2e8f0;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a202c 0%, #0f172a 100%) !important;
            border-right: 2px solid #4f46e5;
        }
        
        /* Metric cards - vibrant gradient */
        .stMetric {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #4f46e5;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        
        .stMetric > div:first-child {
            color: #94a3b8 !important;
        }
        
        .stMetric .stMetricValue {
            color: #e0f2fe !important;
            font-size: 2.8rem !important;
            font-weight: 700 !important;
        }
        
        .stMetric .stMetricLabel {
            color: #cbd5e1 !important;
            font-size: 1rem !important;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] button {
            background-color: #1e293b !important;
            border-bottom: 2px solid #334155 !important;
            color: #94a3b8 !important;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: #4f46e5 !important;
            color: #ffffff !important;
            border-bottom: 2px solid #4f46e5 !important;
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 20px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton>button:hover {
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
            box-shadow: 0 6px 20px rgba(122, 60, 237, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Form elements */
        .stTextInput>div>div>input,
        .stSelectbox>div>div>select,
        .stNumberInput>div>div>input {
            background-color: #1e293b !important;
            color: #e2e8f0 !important;
            border: 1px solid #4f46e5 !important;
            border-radius: 6px !important;
            padding: 10px 12px !important;
        }
        
        .stTextInput>div>div>input::placeholder,
        .stSelectbox>div>div>select::placeholder {
            color: #64748b !important;
        }
        
        /* Success/Error/Info/Warning messages */
        .stSuccess {
            background-color: #064e3b !important;
            color: #10b981 !important;
            border-left: 4px solid #10b981 !important;
        }
        
        .stError {
            background-color: #7f1d1d !important;
            color: #fca5a5 !important;
            border-left: 4px solid #ef4444 !important;
        }
        
        .stWarning {
            background-color: #78350f !important;
            color: #fcd34d !important;
            border-left: 4px solid #f59e0b !important;
        }
        
        .stInfo {
            background-color: #0c4a6e !important;
            color: #38bdf8 !important;
            border-left: 4px solid #0ea5e9 !important;
        }
        
        /* Titles and headers */
        h1, h2, h3 {
            color: #f1f5f9 !important;
            font-weight: 700 !important;
        }
        
        /* Divider */
        hr {
            border-color: #334155 !important;
        }
        
        /* Caption text */
        .caption {
            color: #94a3b8 !important;
        }
        
        /* Dataframe styling */
        .stDataFrame {
            background-color: #1e293b !important;
        }
        
        /* Form container */
        .element-container {
            color: #e2e8f0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Initialize navigation in session state if not present
    if "navigation" not in st.session_state:
        st.session_state["navigation"] = "🏠 Dashboard"
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎓 VIT Result System")
        st.divider()
        
        # Update navigation state when radio changes
        st.session_state["navigation"] = st.radio(
            "Navigation",
            ["🏠 Dashboard", "👥 Students", "📝 Marks Entry", "🔍 Results", "📚 Subjects"],
            label_visibility="collapsed",
            key="nav_radio",
            index=["🏠 Dashboard", "👥 Students", "📝 Marks Entry", "🔍 Results", "📚 Subjects"].index(st.session_state["navigation"])
        )
        
        st.divider()
        st.caption("Semester V - AIML Department")
        st.caption("Powered by MongoDB + Streamlit")
    
    # Route to pages based on navigation state
    current_page = st.session_state["navigation"]
    if current_page == "🏠 Dashboard":
        show_dashboard()
    elif current_page == "👥 Students":
        show_students()
    elif current_page == "📝 Marks Entry":
        show_marks()
    elif current_page == "🔍 Results":
        show_results()
    elif current_page == "📚 Subjects":
        show_subjects()

if __name__ == "__main__":
    main()