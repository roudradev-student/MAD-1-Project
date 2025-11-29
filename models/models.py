from datetime import datetime
from enum import Enum

from db import db


class UserRole(Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"


class AppointmentStatus(Enum):
    BOOKED = "booked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.PATIENT)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # One-to-one relationships (optional)
    doctor_profile = db.relationship("DoctorProfile", back_populates="user", uselist=False)
    patient_profile = db.relationship("PatientProfile", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

    # convenience relationship to doctors
    doctors = db.relationship("DoctorProfile", back_populates="department")

    def __repr__(self):
        return f"<Department {self.name}>"


class DoctorProfile(db.Model):
    __tablename__ = "doctor_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    license_number = db.Column(db.String(80), unique=True)
    specialization = db.Column(db.String(120), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    availability = db.Column(db.JSON, nullable=True)  # example format: {"mon": ["09:00-12:00", "14:00-17:00"], ...}
    phone = db.Column(db.String(30))
    bio = db.Column(db.Text)

    user = db.relationship("User", back_populates="doctor_profile")
    department = db.relationship("Department", back_populates="doctors")
    appointments = db.relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Doctor {self.user.username} ({self.specialization})>"


class PatientProfile(db.Model):
    __tablename__ = "patient_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    patient_identifier = db.Column(db.String(80), unique=True)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    phone = db.Column(db.String(30))
    address = db.Column(db.Text)
    medical_history = db.Column(db.Text)

    user = db.relationship("User", back_populates="patient_profile")
    appointments = db.relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient {self.user.username}>"


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient_profiles.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_profiles.id"), nullable=False, index=True)
    appointment_datetime = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.BOOKED)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    patient = db.relationship("PatientProfile", back_populates="appointments")
    doctor = db.relationship("DoctorProfile", back_populates="appointments")
    treatment = db.relationship("Treatment", back_populates="appointment", uselist=False, cascade="all, delete-orphan")

    def mark_completed(self, diagnosis=None, prescription=None, notes=None):
        self.status = AppointmentStatus.COMPLETED
        if not self.treatment:
            self.treatment = Treatment(appointment=self)
        if diagnosis:
            self.treatment.diagnosis = diagnosis
        if prescription:
            self.treatment.prescription = prescription
        if notes:
            self.treatment.notes = notes

    def __repr__(self):
        return f"<Appointment {self.id} {self.appointment_datetime} {self.status.value}>"


class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False, unique=True)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    appointment = db.relationship("Appointment", back_populates="treatment")

    def __repr__(self):
        return f"<Treatment for appointment {self.appointment_id}>"
