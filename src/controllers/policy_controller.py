"""Policy management controller"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PolicyController:
    """Handle insurance policy operations"""
    
    def __init__(self, session):
        self.session = session
    
    def create_policy(self, user_id, policy_data):
        """
        Create a new insurance policy
        
        Args:
            user_id: User ID
            policy_data: Dictionary with policy information
            
        Returns:
            tuple: (success: bool, message: str, policy: Policy or None)
        """
        from ..models import InsurancePolicy
        
        try:
            policy = InsurancePolicy(
                user_id=user_id,
                policy_number=policy_data['policy_number'],
                policy_holder_name=policy_data['policy_holder_name'],
                policy_holder_national_id=policy_data.get('policy_holder_national_id'),
                mobile_number=policy_data.get('mobile_number'),
                policy_type=policy_data.get('policy_type'),
                insurance_company=policy_data.get('insurance_company'),
                total_amount=policy_data['total_amount'],
                down_payment=policy_data.get('down_payment', 0),
                num_installments=policy_data.get('num_installments', 0),
                start_date=policy_data['start_date'],
                end_date=policy_data['end_date'],
                description=policy_data.get('description'),
                status='active'
            )
            
            self.session.add(policy)
            self.session.commit()
            
            logger.info(f"Policy created: {policy.policy_number}")
            return True, "بیمه‌نامه با موفقیت ثبت شد", policy
            
        except Exception as e:
            logger.error(f"Policy creation error: {e}")
            self.session.rollback()
            return False, f"خطا در ثبت بیمه‌نامه: {str(e)}", None
    
    def update_policy(self, policy_id, policy_data):
        """Update existing policy"""
        from ..models import InsurancePolicy
        
        try:
            policy = self.session.query(InsurancePolicy).filter(
                InsurancePolicy.id == policy_id
            ).first()
            
            if not policy:
                return False, "بیمه‌نامه یافت نشد", None
            
            # Update fields
            for key, value in policy_data.items():
                if hasattr(policy, key) and value is not None:
                    setattr(policy, key, value)
            
            policy.updated_at = datetime.now()
            self.session.commit()
            
            logger.info(f"Policy updated: {policy.policy_number}")
            return True, "بیمه‌نامه با موفقیت به‌روزرسانی شد", policy
            
        except Exception as e:
            logger.error(f"Policy update error: {e}")
            self.session.rollback()
            return False, f"خطا در به‌روزرسانی بیمه‌نامه: {str(e)}", None
    
    def delete_policy(self, policy_id):
        """Delete policy"""
        from ..models import InsurancePolicy
        
        try:
            policy = self.session.query(InsurancePolicy).filter(
                InsurancePolicy.id == policy_id
            ).first()
            
            if not policy:
                return False, "بیمه‌نامه یافت نشد"
            
            policy_number = policy.policy_number
            self.session.delete(policy)
            self.session.commit()
            
            logger.info(f"Policy deleted: {policy_number}")
            return True, "بیمه‌نامه با موفقیت حذف شد"
            
        except Exception as e:
            logger.error(f"Policy deletion error: {e}")
            self.session.rollback()
            return False, f"خطا در حذف بیمه‌نامه: {str(e)}"
    
    def get_policy(self, policy_id):
        """Get policy by ID"""
        from ..models import InsurancePolicy
        
        try:
            policy = self.session.query(InsurancePolicy).filter(
                InsurancePolicy.id == policy_id
            ).first()
            return policy
        except Exception as e:
            logger.error(f"Error fetching policy: {e}")
            return None
    
    def get_all_policies(self, user_id=None, status=None):
        """Get all policies with optional filters"""
        from ..models import InsurancePolicy
        
        try:
            query = self.session.query(InsurancePolicy)
            
            if user_id:
                query = query.filter(InsurancePolicy.user_id == user_id)
            if status:
                query = query.filter(InsurancePolicy.status == status)
            
            return query.order_by(InsurancePolicy.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error fetching policies: {e}")
            return []
    
    def search_policies(self, search_term, user_id=None):
        """Search policies by number or holder name"""
        from ..models import InsurancePolicy
        
        try:
            query = self.session.query(InsurancePolicy).filter(
                (InsurancePolicy.policy_number.like(f'%{search_term}%')) |
                (InsurancePolicy.policy_holder_name.like(f'%{search_term}%'))
            )
            
            if user_id:
                query = query.filter(InsurancePolicy.user_id == user_id)
            
            return query.all()
        except Exception as e:
            logger.error(f"Error searching policies: {e}")
            return []
    
    def get_policy_statistics(self, user_id=None):
        """Get policy statistics"""
        from ..models import InsurancePolicy, Installment
        from sqlalchemy import func
        
        try:
            query = self.session.query(
                func.count(InsurancePolicy.id).label('total_policies'),
                func.sum(InsurancePolicy.total_amount).label('total_amount'),
                func.count(InsurancePolicy.id).filter(
                    InsurancePolicy.status == 'active'
                ).label('active_policies')
            )
            
            if user_id:
                query = query.filter(InsurancePolicy.user_id == user_id)
            
            result = query.first()
            
            return {
                'total_policies': result.total_policies or 0,
                'total_amount': result.total_amount or 0,
                'active_policies': result.active_policies or 0
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {
                'total_policies': 0,
                'total_amount': 0,
                'active_policies': 0
            }
