"""Installment management controller"""
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class InstallmentController:
    """Handle installment operations"""
    
    def __init__(self, session):
        self.session = session
    
    def create_installment(self, installment_data):
        """Create a new installment"""
        from ..models import Installment
        
        try:
            installment = Installment(
                policy_id=installment_data['policy_id'],
                installment_number=installment_data['installment_number'],
                amount=installment_data['amount'],
                due_date=installment_data['due_date'],
                notes=installment_data.get('notes')
            )
            
            self.session.add(installment)
            self.session.commit()
            
            logger.info(f"Installment created for policy {installment.policy_id}")
            return True, "قسط با موفقیت ثبت شد", installment
            
        except Exception as e:
            logger.error(f"Installment creation error: {e}")
            self.session.rollback()
            return False, f"خطا در ثبت قسط: {str(e)}", None
    
    def create_installments_batch(self, policy_id, total_amount, num_installments, 
                                 start_date, interval_days=30):
        """
        Create multiple installments for a policy
        
        Args:
            policy_id: Policy ID
            total_amount: Total amount to be divided
            num_installments: Number of installments
            start_date: Start date for first installment
            interval_days: Days between installments (default: 30)
            
        Returns:
            tuple: (success: bool, message: str, installments: list)
        """
        from ..models import Installment
        
        try:
            installment_amount = total_amount / num_installments
            installments = []
            
            for i in range(num_installments):
                due_date = start_date + timedelta(days=interval_days * i)
                installment = Installment(
                    policy_id=policy_id,
                    installment_number=i + 1,
                    amount=installment_amount,
                    due_date=due_date
                )
                installments.append(installment)
                self.session.add(installment)
            
            self.session.commit()
            
            logger.info(f"Created {num_installments} installments for policy {policy_id}")
            return True, f"{num_installments} قسط با موفقیت ایجاد شد", installments
            
        except Exception as e:
            logger.error(f"Batch installment creation error: {e}")
            self.session.rollback()
            return False, f"خطا در ایجاد اقساط: {str(e)}", []
    
    def update_installment(self, installment_id, installment_data):
        """Update installment"""
        from ..models import Installment
        
        try:
            installment = self.session.query(Installment).filter(
                Installment.id == installment_id
            ).first()
            
            if not installment:
                return False, "قسط یافت نشد", None
            
            for key, value in installment_data.items():
                if hasattr(installment, key) and value is not None:
                    setattr(installment, key, value)
            
            installment.updated_at = datetime.now()
            self.session.commit()
            
            logger.info(f"Installment {installment_id} updated")
            return True, "قسط با موفقیت به‌روزرسانی شد", installment
            
        except Exception as e:
            logger.error(f"Installment update error: {e}")
            self.session.rollback()
            return False, f"خطا در به‌روزرسانی قسط: {str(e)}", None
    
    def mark_as_paid(self, installment_id, payment_method=None, transaction_ref=None):
        """Mark installment as paid"""
        from ..models import Installment
        
        try:
            installment = self.session.query(Installment).filter(
                Installment.id == installment_id
            ).first()
            
            if not installment:
                return False, "قسط یافت نشد"
            
            installment.status = 'paid'
            installment.payment_date = datetime.now()
            installment.payment_method = payment_method
            installment.transaction_reference = transaction_ref
            installment.updated_at = datetime.now()
            
            self.session.commit()
            
            logger.info(f"Installment {installment_id} marked as paid")
            
            # Send notification
            from ..utils import NotificationManager
            from ..models import InsurancePolicy
            
            policy = self.session.query(InsurancePolicy).filter(
                InsurancePolicy.id == installment.policy_id
            ).first()
            
            if policy:
                notif = NotificationManager()
                notif.send_payment_confirmation(policy.policy_number, installment.amount)
                
                # Check if all installments are paid, then auto-delete policy
                self._check_and_delete_policy_if_all_paid(policy.id)
            
            return True, "قسط به عنوان پرداخت شده ثبت شد"
            
        except Exception as e:
            logger.error(f"Payment marking error: {e}")
            self.session.rollback()
            return False, f"خطا در ثبت پرداخت: {str(e)}"
    
    def _check_and_delete_policy_if_all_paid(self, policy_id):
        """Check if all installments are paid and delete policy automatically"""
        from ..models import Installment, InsurancePolicy
        
        try:
            # Get all installments for this policy
            installments = self.session.query(Installment).filter(
                Installment.policy_id == policy_id
            ).all()
            
            # Check if there are any installments
            if not installments:
                return
            
            # Check if all installments are paid
            all_paid = all(inst.status == 'paid' for inst in installments)
            
            if all_paid:
                # Delete the policy (cascade will delete installments too)
                policy = self.session.query(InsurancePolicy).filter(
                    InsurancePolicy.id == policy_id
                ).first()
                
                if policy:
                    policy_number = policy.policy_number
                    self.session.delete(policy)
                    self.session.commit()
                    logger.info(f"Policy {policy_number} auto-deleted: all installments paid")
        
        except Exception as e:
            logger.error(f"Error checking/deleting policy: {e}")
            self.session.rollback()
    
    def get_installment(self, installment_id):
        """Get installment by ID"""
        from ..models import Installment
        
        try:
            return self.session.query(Installment).filter(
                Installment.id == installment_id
            ).first()
        except Exception as e:
            logger.error(f"Error fetching installment: {e}")
            return None
    
    def get_policy_installments(self, policy_id):
        """Get all installments for a policy"""
        from ..models import Installment
        
        try:
            return self.session.query(Installment).filter(
                Installment.policy_id == policy_id
            ).order_by(Installment.installment_number).all()
        except Exception as e:
            logger.error(f"Error fetching installments: {e}")
            return []
    
    def get_upcoming_installments(self, days_ahead=30, user_id=None):
        """Get installments due in next N days"""
        from ..models import Installment, InsurancePolicy
        
        try:
            today = datetime.now()
            future_date = today + timedelta(days=days_ahead)
            
            query = self.session.query(Installment).filter(
                Installment.due_date >= today,
                Installment.due_date <= future_date,
                Installment.status == 'pending'
            )
            
            if user_id:
                query = query.join(InsurancePolicy).filter(
                    InsurancePolicy.user_id == user_id
                )
            
            return query.order_by(Installment.due_date).all()
        except Exception as e:
            logger.error(f"Error fetching upcoming installments: {e}")
            return []
    
    def get_overdue_installments(self, user_id=None):
        """Get overdue installments"""
        from ..models import Installment, InsurancePolicy
        
        try:
            today = datetime.now()
            
            query = self.session.query(Installment).filter(
                Installment.due_date < today,
                Installment.status == 'pending'
            )
            
            if user_id:
                query = query.join(InsurancePolicy).filter(
                    InsurancePolicy.user_id == user_id
                )
            
            # Update status to overdue
            overdues = query.all()
            for inst in overdues:
                inst.status = 'overdue'
            self.session.commit()
            
            return overdues
        except Exception as e:
            logger.error(f"Error fetching overdue installments: {e}")
            return []
    
    def get_installments_by_date_range(self, start_date, end_date, user_id=None):
        """Get installments within date range"""
        from ..models import Installment, InsurancePolicy
        
        try:
            query = self.session.query(Installment).filter(
                Installment.due_date >= start_date,
                Installment.due_date <= end_date
            )
            
            if user_id:
                query = query.join(InsurancePolicy).filter(
                    InsurancePolicy.user_id == user_id
                )
            
            return query.order_by(Installment.due_date).all()
        except Exception as e:
            logger.error(f"Error fetching installments by date range: {e}")
            return []
    
    def get_installment_statistics(self, user_id=None):
        """Get installment statistics"""
        from ..models import Installment, InsurancePolicy
        from sqlalchemy import func
        
        try:
            query = self.session.query(
                func.count(Installment.id).label('total'),
                func.sum(Installment.amount).filter(
                    Installment.status == 'paid'
                ).label('total_paid'),
                func.sum(Installment.amount).filter(
                    Installment.status == 'pending'
                ).label('total_pending'),
                func.sum(Installment.amount).filter(
                    Installment.status == 'overdue'
                ).label('total_overdue')
            )
            
            if user_id:
                query = query.join(InsurancePolicy).filter(
                    InsurancePolicy.user_id == user_id
                )
            
            result = query.first()
            
            return {
                'total': result.total or 0,
                'total_paid': result.total_paid or 0,
                'total_pending': result.total_pending or 0,
                'total_overdue': result.total_overdue or 0
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {
                'total': 0,
                'total_paid': 0,
                'total_pending': 0,
                'total_overdue': 0
            }
