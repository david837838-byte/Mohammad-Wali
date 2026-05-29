"""
نماذج البيانات لنظام إدارة المستشفى
"""

from .user import User
from .patient import Patient
from .medical_record import MedicalRecord
from .visit import Visit

__all__ = ['User', 'Patient', 'MedicalRecord', 'Visit']