"""Report generator for custom reports"""
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate custom reports with filters"""
    
    def __init__(self, session):
        """
        Initialize report generator
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def generate_installment_report(self, start_date=None, end_date=None, 
                                   status=None, policy_id=None, insurance_type=None):
        """
        Generate installment report with filters
        
        Args:
            start_date: Filter by due date >= start_date
            end_date: Filter by due date <= end_date
            status: Filter by status (pending, paid, overdue, etc.)
            policy_id: Filter by specific policy
            insurance_type: Filter by insurance type (Third Party, Body, etc.)
            
        Returns:
            pandas DataFrame with report data
        """
        from ..models import Installment, InsurancePolicy
        from ..utils.persian_utils import PersianDateConverter
        
        query = self.session.query(
            Installment,
            InsurancePolicy.policy_number,
            InsurancePolicy.policy_holder_name,
            InsurancePolicy.policy_type
        ).join(InsurancePolicy)
        
        # Apply filters
        if start_date:
            query = query.filter(Installment.due_date >= start_date)
        if end_date:
            query = query.filter(Installment.due_date <= end_date)
        if status:
            query = query.filter(Installment.status == status)
        if policy_id:
            query = query.filter(Installment.policy_id == policy_id)
        if insurance_type:
            query = query.filter(InsurancePolicy.policy_type == insurance_type)
        
        # Execute query
        results = query.all()
        
        # Convert to DataFrame with Persian dates
        data = []
        for inst, policy_num, holder_name, policy_type in results:
            data.append({
                'policy_number': policy_num,
                'policy_holder': holder_name,
                'insurance_type': policy_type,
                'installment_number': inst.installment_number,
                'amount': inst.amount,
                'due_date': PersianDateConverter.gregorian_to_jalali(inst.due_date) if inst.due_date else '',
                'payment_date': PersianDateConverter.gregorian_to_jalali(inst.payment_date) if inst.payment_date else '',
                'status': inst.status,
                'payment_method': inst.payment_method
            })
        
        return pd.DataFrame(data)
    
    def generate_policy_summary(self, user_id=None):
        """Generate policy summary report"""
        from ..models import InsurancePolicy, Installment
        from sqlalchemy import func
        
        query = self.session.query(
            InsurancePolicy,
            func.count(Installment.id).label('total_installments'),
            func.sum(Installment.amount).filter(Installment.status == 'paid').label('total_paid'),
            func.sum(Installment.amount).filter(Installment.status == 'pending').label('total_pending')
        ).outerjoin(Installment).group_by(InsurancePolicy.id)
        
        if user_id:
            query = query.filter(InsurancePolicy.user_id == user_id)
        
        results = query.all()
        
        data = []
        for policy, total_inst, paid, pending in results:
            data.append({
                'policy_number': policy.policy_number,
                'policy_holder': policy.policy_holder_name,
                'policy_type': policy.policy_type,
                'total_amount': policy.total_amount,
                'total_installments': total_inst or 0,
                'total_paid': paid or 0,
                'total_pending': pending or 0,
                'status': policy.status
            })
        
        return pd.DataFrame(data)
    
    def generate_payment_statistics(self, start_date=None, end_date=None):
        """Generate payment statistics report with Persian dates"""
        from ..models import Installment
        from sqlalchemy import func
        from ..utils.persian_utils import PersianDateConverter
        from persiantools.jdatetime import JalaliDateTime
        
        query = self.session.query(
            Installment
        ).filter(
            Installment.status == 'paid'
        )
        
        if start_date:
            query = query.filter(Installment.payment_date >= start_date)
        if end_date:
            query = query.filter(Installment.payment_date <= end_date)
        
        results = query.all()
        
        # Group by Persian month
        monthly_data = {}
        for inst in results:
            if inst.payment_date:
                jalali = JalaliDateTime.to_jalali(inst.payment_date)
                month_key = f"{jalali.year}/{jalali.month:02d}"
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'count': 0, 'total': 0}
                
                monthly_data[month_key]['count'] += 1
                monthly_data[month_key]['total'] += inst.amount
        
        # Convert to DataFrame
        data = []
        for month, stats in sorted(monthly_data.items()):
            data.append({
                'month': month,
                'payment_count': stats['count'],
                'total_amount': stats['total']
            })
        
        return pd.DataFrame(data)
    
    def export_to_excel(self, dataframe, filename):
        """Export DataFrame to Excel file"""
        try:
            dataframe.to_excel(filename, index=False, engine='openpyxl')
            logger.info(f"Report exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            return False
    
    def export_to_csv(self, dataframe, filename):
        """Export DataFrame to CSV file"""
        try:
            dataframe.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"Report exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            return False
