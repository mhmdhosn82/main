"""Dashboard widget with statistics and charts"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QFrame, QGridLayout, QPushButton, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import logging

logger = logging.getLogger(__name__)

class DashboardWidget(QWidget):
    """Dashboard with statistics and charts"""
    
    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the dashboard UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("داشبورد")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.total_policies_card = self.create_stat_card("بیمه‌نامه‌ها", "0", "#3498db")
        self.pending_installments_card = self.create_stat_card("اقساط معوق", "0", "#e74c3c")
        self.upcoming_payments_card = self.create_stat_card("پرداخت‌های آتی", "0", "#f39c12")
        self.total_paid_card = self.create_stat_card("کل پرداختی‌ها", "0 ریال", "#27ae60")
        
        stats_layout.addWidget(self.total_policies_card)
        stats_layout.addWidget(self.pending_installments_card)
        stats_layout.addWidget(self.upcoming_payments_card)
        stats_layout.addWidget(self.total_paid_card)
        
        layout.addLayout(stats_layout)
        
        # Charts section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # Payment status chart
        self.status_chart_widget = QWidget()
        self.status_chart_widget.setMinimumHeight(300)
        self.status_chart_layout = QVBoxLayout()
        self.status_chart_widget.setLayout(self.status_chart_layout)
        charts_layout.addWidget(self.status_chart_widget)
        
        # Monthly payments chart
        self.monthly_chart_widget = QWidget()
        self.monthly_chart_widget.setMinimumHeight(300)
        self.monthly_chart_layout = QVBoxLayout()
        self.monthly_chart_widget.setLayout(self.monthly_chart_layout)
        charts_layout.addWidget(self.monthly_chart_widget)
        
        layout.addLayout(charts_layout)
        
        # Recent activity section
        recent_label = QLabel("فعالیت‌های اخیر")
        recent_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(recent_label)
        
        self.recent_activity_widget = QWidget()
        self.recent_activity_layout = QVBoxLayout()
        self.recent_activity_widget.setLayout(self.recent_activity_layout)
        layout.addWidget(self.recent_activity_widget)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def create_stat_card(self, title, value, color):
        """Create a statistics card"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box | QFrame.Raised)
        card.setLineWidth(2)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {color};
        """)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setObjectName("value_label")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        card_layout.addWidget(value_label)
        card_layout.addWidget(title_label)
        
        card.setLayout(card_layout)
        return card
    
    def load_data(self):
        """Load dashboard data"""
        from ..controllers import PolicyController, InstallmentController
        from ..utils.persian_utils import format_currency
        
        try:
            policy_ctrl = PolicyController(self.session)
            installment_ctrl = InstallmentController(self.session)
            
            # Get statistics
            policy_stats = policy_ctrl.get_policy_statistics(self.user.id)
            installment_stats = installment_ctrl.get_installment_statistics(self.user.id)
            
            # Update stat cards
            self.update_stat_card(self.total_policies_card, str(policy_stats['total_policies']))
            
            overdue_count = len(installment_ctrl.get_overdue_installments(self.user.id))
            self.update_stat_card(self.pending_installments_card, str(overdue_count))
            
            upcoming_count = len(installment_ctrl.get_upcoming_installments(30, self.user.id))
            self.update_stat_card(self.upcoming_payments_card, str(upcoming_count))
            
            total_paid = format_currency(installment_stats['total_paid'])
            self.update_stat_card(self.total_paid_card, total_paid)
            
            # Create charts
            self.create_status_chart(installment_stats)
            self.create_monthly_chart()
            
            # Load recent activity
            self.load_recent_activity()
            
        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}")
    
    def update_stat_card(self, card, value):
        """Update stat card value"""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)
    
    def create_status_chart(self, stats):
        """Create payment status pie chart"""
        # Clear previous chart
        for i in reversed(range(self.status_chart_layout.count())):
            self.status_chart_layout.itemAt(i).widget().setParent(None)
        
        # Create figure
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)
        
        # Data
        labels = ['پرداخت شده', 'در انتظار', 'معوق']
        sizes = [
            stats.get('total_paid', 0),
            stats.get('total_pending', 0),
            stats.get('total_overdue', 0)
        ]
        colors = ['#27ae60', '#f39c12', '#e74c3c']
        
        # Only show if there's data
        if sum(sizes) > 0:
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'داده‌ای موجود نیست', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
        
        ax.set_title('وضعیت پرداخت‌ها', fontsize=14, fontweight='bold')
        fig.tight_layout()
        
        self.status_chart_layout.addWidget(canvas)
    
    def create_monthly_chart(self):
        """Create monthly payments bar chart"""
        # Clear previous chart
        for i in reversed(range(self.monthly_chart_layout.count())):
            self.monthly_chart_layout.itemAt(i).widget().setParent(None)
        
        # Create figure
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)
        
        # Get monthly data
        from ..utils import ReportGenerator
        from datetime import datetime, timedelta
        
        report_gen = ReportGenerator(self.session)
        start_date = datetime.now() - timedelta(days=180)  # Last 6 months
        df = report_gen.generate_payment_statistics(start_date)
        
        if not df.empty:
            months = df['month'].tolist()
            amounts = df['total_amount'].tolist()
            
            ax.bar(range(len(months)), amounts, color='#3498db')
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels(months, rotation=45, ha='right')
            ax.set_ylabel('مبلغ (ریال)')
            ax.set_title('پرداخت‌های ماهانه', fontsize=14, fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'داده‌ای موجود نیست', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
        
        fig.tight_layout()
        self.monthly_chart_layout.addWidget(canvas)
    
    def load_recent_activity(self):
        """Load recent activity"""
        # Clear previous items
        for i in reversed(range(self.recent_activity_layout.count())):
            self.recent_activity_layout.itemAt(i).widget().setParent(None)
        
        from ..controllers import InstallmentController
        from ..utils.persian_utils import PersianDateConverter, format_currency
        
        installment_ctrl = InstallmentController(self.session)
        
        # Get recent paid installments
        from ..models import Installment, InsurancePolicy
        
        recent = self.session.query(Installment, InsurancePolicy).join(
            InsurancePolicy
        ).filter(
            InsurancePolicy.user_id == self.user.id,
            Installment.status == 'paid'
        ).order_by(Installment.payment_date.desc()).limit(5).all()
        
        if recent:
            for inst, policy in recent:
                activity_text = (
                    f"✓ پرداخت قسط {inst.installment_number} "
                    f"بیمه‌نامه {policy.policy_number} - "
                    f"{format_currency(inst.amount)} - "
                    f"{PersianDateConverter.gregorian_to_jalali(inst.payment_date)}"
                )
                
                label = QLabel(activity_text)
                label.setStyleSheet("""
                    QLabel {
                        padding: 10px;
                        background-color: #f8f9fa;
                        border-left: 4px solid #27ae60;
                        margin: 5px;
                    }
                """)
                self.recent_activity_layout.addWidget(label)
        else:
            no_activity = QLabel("فعالیتی ثبت نشده است")
            no_activity.setStyleSheet("color: #7f8c8d; padding: 20px;")
            no_activity.setAlignment(Qt.AlignCenter)
            self.recent_activity_layout.addWidget(no_activity)
    
    def refresh(self):
        """Refresh dashboard data"""
        self.load_data()
