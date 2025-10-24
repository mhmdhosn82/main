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
        
        # Convert to DataFrame
        data = []
        for inst, policy_num, holder_name, policy_type in results:
            data.append({
                'policy_number': policy_num,
                'policy_holder': holder_name,
                'insurance_type': policy_type,
                'installment_number': inst.installment_number,
                'amount': inst.amount,
                'due_date': inst.due_date,
                'payment_date': inst.payment_date,
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
        """Generate payment statistics report"""
        from ..models import Installment
        from sqlalchemy import func
        
        query = self.session.query(
            func.strftime('%Y-%m', Installment.payment_date).label('month'),
            func.count(Installment.id).label('count'),
            func.sum(Installment.amount).label('total')
        ).filter(
            Installment.status == 'paid'
        )
        
        if start_date:
            query = query.filter(Installment.payment_date >= start_date)
        if end_date:
            query = query.filter(Installment.payment_date <= end_date)
        
        query = query.group_by('month').order_by('month')
        
        results = query.all()
        
        data = []
        for month, count, total in results:
            data.append({
                'month': month,
                'payment_count': count,
                'total_amount': total or 0
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
