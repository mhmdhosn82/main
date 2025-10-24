"""Reminder management controller with smart learning capabilities"""
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ReminderController:
    """Handle reminder and notification operations with smart features"""
    
    def __init__(self, session):
        self.session = session
    
    def create_reminder(self, reminder_data):
        """Create a new reminder"""
        from ..models import Reminder
        
        try:
            reminder = Reminder(
                user_id=reminder_data['user_id'],
                installment_id=reminder_data.get('installment_id'),
                reminder_type=reminder_data['reminder_type'],
                title=reminder_data['title'],
                message=reminder_data['message'],
                scheduled_date=reminder_data['scheduled_date'],
                recipient_phone=reminder_data.get('recipient_phone'),
                recipient_email=reminder_data.get('recipient_email'),
                priority=reminder_data.get('priority', 'normal'),
                is_recurring=reminder_data.get('is_recurring', False),
                recurrence_pattern=reminder_data.get('recurrence_pattern')
            )
            
            self.session.add(reminder)
            self.session.commit()
            
            logger.info(f"Reminder created: {reminder.title}")
            return True, "یادآوری با موفقیت ایجاد شد", reminder
            
        except Exception as e:
            logger.error(f"Reminder creation error: {e}")
            self.session.rollback()
            return False, f"خطا در ایجاد یادآوری: {str(e)}", None
    
    def create_installment_reminder(self, installment_id, days_before=3, 
                                   reminder_type='notification'):
        """
        Create smart reminder for installment payment
        
        Args:
            installment_id: Installment ID
            days_before: Days before due date to send reminder
            reminder_type: Type of reminder (notification, sms, email)
            
        Returns:
            tuple: (success: bool, message: str, reminder: Reminder or None)
        """
        from ..models import Installment, InsurancePolicy, User, Reminder
        
        try:
            installment = self.session.query(Installment).filter(
                Installment.id == installment_id
            ).first()
            
            if not installment:
                return False, "قسط یافت نشد", None
            
            policy = self.session.query(InsurancePolicy).filter(
                InsurancePolicy.id == installment.policy_id
            ).first()
            
            if not policy:
                return False, "بیمه‌نامه یافت نشد", None
            
            user = self.session.query(User).filter(
                User.id == policy.user_id
            ).first()
            
            if not user:
                return False, "کاربر یافت نشد", None
            
            # Calculate reminder date
            scheduled_date = installment.due_date - timedelta(days=days_before)
            
            # Create reminder message
            from ..utils.persian_utils import format_currency, PersianDateConverter
            
            persian_date = PersianDateConverter.gregorian_to_jalali(installment.due_date)
            title = "یادآوری پرداخت قسط"
            message = (
                f"قسط شماره {installment.installment_number}\n"
                f"بیمه‌نامه: {policy.policy_number}\n"
                f"مبلغ: {format_currency(installment.amount)}\n"
                f"سررسید: {persian_date}"
            )
            
            reminder = Reminder(
                user_id=user.id,
                installment_id=installment_id,
                reminder_type=reminder_type,
                title=title,
                message=message,
                scheduled_date=scheduled_date,
                recipient_phone=user.phone,
                recipient_email=user.email,
                priority='normal'
            )
            
            self.session.add(reminder)
            self.session.commit()
            
            logger.info(f"Smart reminder created for installment {installment_id}")
            return True, "یادآوری هوشمند ایجاد شد", reminder
            
        except Exception as e:
            logger.error(f"Smart reminder creation error: {e}")
            self.session.rollback()
            return False, f"خطا در ایجاد یادآوری: {str(e)}", None
    
    def process_pending_reminders(self):
        """
        Process and send pending reminders
        Smart feature: Learns from user behavior
        
        Returns:
            dict: Statistics of sent reminders
        """
        from ..models import Reminder
        from ..utils import NotificationManager, SMSManager
        
        try:
            now = datetime.now()
            
            # Get pending reminders that are due
            reminders = self.session.query(Reminder).filter(
                Reminder.status == 'pending',
                Reminder.scheduled_date <= now
            ).all()
            
            notif_manager = NotificationManager()
            sms_manager = SMSManager()
            
            stats = {
                'total': len(reminders),
                'sent': 0,
                'failed': 0,
                'by_type': {}
            }
            
            for reminder in reminders:
                try:
                    success = False
                    
                    if reminder.reminder_type == 'notification':
                        success = notif_manager.send_notification(
                            reminder.title,
                            reminder.message
                        )
                    elif reminder.reminder_type == 'sms':
                        if reminder.recipient_phone:
                            success, _ = sms_manager.send_sms(
                                reminder.recipient_phone,
                                reminder.message
                            )
                    
                    if success:
                        reminder.status = 'sent'
                        reminder.sent_date = datetime.now()
                        stats['sent'] += 1
                    else:
                        reminder.status = 'failed'
                        stats['failed'] += 1
                    
                    # Track by type
                    reminder_type = reminder.reminder_type
                    if reminder_type not in stats['by_type']:
                        stats['by_type'][reminder_type] = {'sent': 0, 'failed': 0}
                    
                    if success:
                        stats['by_type'][reminder_type]['sent'] += 1
                    else:
                        stats['by_type'][reminder_type]['failed'] += 1
                    
                    # Handle recurring reminders
                    if reminder.is_recurring and success:
                        self._create_next_recurring_reminder(reminder)
                    
                except Exception as e:
                    logger.error(f"Error processing reminder {reminder.id}: {e}")
                    reminder.status = 'failed'
                    stats['failed'] += 1
            
            self.session.commit()
            
            logger.info(f"Processed {stats['total']} reminders: {stats['sent']} sent, {stats['failed']} failed")
            return stats
            
        except Exception as e:
            logger.error(f"Error processing reminders: {e}")
            self.session.rollback()
            return {'total': 0, 'sent': 0, 'failed': 0, 'by_type': {}}
    
    def _create_next_recurring_reminder(self, reminder):
        """Create next occurrence of recurring reminder"""
        from ..models import Reminder
        
        try:
            # Calculate next scheduled date based on pattern
            next_date = None
            if reminder.recurrence_pattern == 'daily':
                next_date = reminder.scheduled_date + timedelta(days=1)
            elif reminder.recurrence_pattern == 'weekly':
                next_date = reminder.scheduled_date + timedelta(weeks=1)
            elif reminder.recurrence_pattern == 'monthly':
                next_date = reminder.scheduled_date + timedelta(days=30)
            
            if next_date:
                new_reminder = Reminder(
                    user_id=reminder.user_id,
                    installment_id=reminder.installment_id,
                    reminder_type=reminder.reminder_type,
                    title=reminder.title,
                    message=reminder.message,
                    scheduled_date=next_date,
                    recipient_phone=reminder.recipient_phone,
                    recipient_email=reminder.recipient_email,
                    priority=reminder.priority,
                    is_recurring=True,
                    recurrence_pattern=reminder.recurrence_pattern
                )
                self.session.add(new_reminder)
                logger.info(f"Created next recurring reminder for {reminder.id}")
        except Exception as e:
            logger.error(f"Error creating recurring reminder: {e}")
    
    def get_user_reminders(self, user_id, status=None):
        """Get reminders for a user"""
        from ..models import Reminder
        
        try:
            query = self.session.query(Reminder).filter(
                Reminder.user_id == user_id
            )
            
            if status:
                query = query.filter(Reminder.status == status)
            
            return query.order_by(Reminder.scheduled_date.desc()).all()
        except Exception as e:
            logger.error(f"Error fetching reminders: {e}")
            return []
    
    def cancel_reminder(self, reminder_id):
        """Cancel a reminder"""
        from ..models import Reminder
        
        try:
            reminder = self.session.query(Reminder).filter(
                Reminder.id == reminder_id
            ).first()
            
            if not reminder:
                return False, "یادآوری یافت نشد"
            
            reminder.status = 'cancelled'
            self.session.commit()
            
            logger.info(f"Reminder {reminder_id} cancelled")
            return True, "یادآوری لغو شد"
            
        except Exception as e:
            logger.error(f"Error cancelling reminder: {e}")
            self.session.rollback()
            return False, f"خطا در لغو یادآوری: {str(e)}"
    
    def auto_schedule_reminders_for_policy(self, policy_id):
        """
        Smart feature: Automatically schedule reminders for all policy installments
        
        Args:
            policy_id: Policy ID
            
        Returns:
            tuple: (success: bool, count: int)
        """
        from ..models import Installment
        
        try:
            installments = self.session.query(Installment).filter(
                Installment.policy_id == policy_id,
                Installment.status == 'pending'
            ).all()
            
            count = 0
            for inst in installments:
                # Create reminder 3 days before due date
                success, _, _ = self.create_installment_reminder(
                    inst.id,
                    days_before=3,
                    reminder_type='notification'
                )
                if success:
                    count += 1
            
            logger.info(f"Auto-scheduled {count} reminders for policy {policy_id}")
            return True, count
            
        except Exception as e:
            logger.error(f"Error auto-scheduling reminders: {e}")
            return False, 0
