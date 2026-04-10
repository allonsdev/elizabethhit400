# ═══════════════════════════════════════════════════════
#  notifications.py  — Place in your app directory
#  Handles SweetAlert toast triggers AND email notifications
# ═══════════════════════════════════════════════════════
 
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import logging
 
logger = logging.getLogger(__name__)
 
 
# ── Email subjects & recipients config ──────────────────
NOTIFICATION_EMAILS = getattr(settings, 'SUPPLYINSIGHT_NOTIFY_EMAILS', [])
 
 
def send_notification_email(subject, template_name, context, recipient_list=None):
    """
    Generic HTML email sender.
    Falls back gracefully if email is not configured.
    """
    if recipient_list is None:
        recipient_list = NOTIFICATION_EMAILS
 
    if not recipient_list:
        logger.debug("No notification emails configured — skipping email.")
        return
 
    try:
        html_content = render_to_string(template_name, context)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=f"SupplyInsight Notification: {subject}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Notification email sent: {subject}")
    except Exception as e:
        logger.error(f"Failed to send notification email: {e}")
 
 
def notify_new_supplier(supplier):
    """
    Send email when a new supplier is registered.
    """
    send_notification_email(
        subject=f"New Supplier Registered: {supplier.name}",
        template_name="emails/new_supplier.html",
        context={
            "supplier": supplier,
            "timestamp": timezone.now(),
        }
    )
 
 
def notify_complaint_logged(complaint):
    """
    Send email when a complaint is logged.
    Urgency depends on severity.
    """
    send_notification_email(
        subject=f"[Complaint] {complaint.supplier.name} — Severity {complaint.severity_level}",
        template_name="emails/complaint_logged.html",
        context={
            "complaint": complaint,
            "timestamp": timezone.now(),
        }
    )
 
 
def notify_delivery_recorded(delivery):
    """
    Send email when a delivery is recorded.
    Flags LATE or DAMAGED deliveries.
    """
    is_issue = (
        delivery.delivery_status == 'LATE' or
        delivery.condition_status in ('DAMAGED', 'PARTIAL')
    )
    if is_issue:
        send_notification_email(
            subject=f"[Delivery Alert] {delivery.supplier.name} — {delivery.delivery_status} / {delivery.condition_status}",
            template_name="emails/delivery_alert.html",
            context={
                "delivery": delivery,
                "timestamp": timezone.now(),
            }
        )
 
 
def notify_low_stock(inventory_item):
    """
    Triggered when an inventory item falls below reorder level.
    """
    send_notification_email(
        subject=f"[Low Stock] {inventory_item.name} — {inventory_item.quantity_in_stock} units remaining",
        template_name="emails/low_stock.html",
        context={
            "item": inventory_item,
            "timestamp": timezone.now(),
        }
    )
 
 
# ── Base email HTML template (inline) ───────────────────
# Save as: templates/emails/base_email.html
 
BASE_EMAIL_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <style>
    body { font-family: 'Inter', Arial, sans-serif; background: #f1f5f9; margin: 0; padding: 0; }
    .wrapper { max-width: 600px; margin: 2rem auto; }
    .header {
      background: linear-gradient(135deg, #4f46e5, #0ea5e9);
      color: white; padding: 2rem; border-radius: 16px 16px 0 0;
      text-align: center;
    }
    .header h1 { font-size: 1.4rem; margin: 0 0 4px; font-weight: 800; }
    .header p  { opacity: 0.85; font-size: 13px; margin: 0; }
    .body  { background: white; padding: 2rem; }
    .footer {
      background: #f8fafc; padding: 1rem 2rem;
      border-radius: 0 0 16px 16px;
      font-size: 12px; color: #64748b; text-align: center;
    }
    .badge {
      display: inline-block; padding: 4px 12px; border-radius: 20px;
      font-size: 11px; font-weight: 700;
    }
    .badge-danger  { background: rgba(239,68,68,0.1);  color: #991b1b; }
    .badge-success { background: rgba(16,185,129,0.1); color: #065f46; }
    .badge-warning { background: rgba(245,158,11,0.1); color: #92400e; }
    .badge-info    { background: rgba(99,102,241,0.1); color: #3730a3; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    td, th { padding: 8px 0; border-bottom: 1px solid #f1f5f9; }
    th { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; font-weight: 700; }
    .btn {
      display: inline-block; padding: 10px 24px;
      background: #4f46e5; color: white; border-radius: 8px;
      text-decoration: none; font-weight: 700; font-size: 13px;
      margin-top: 1.5rem;
    }
  </style>
</head>
<body>
  <div class="wrapper">
    {% block content %}{% endblock %}
    <div class="footer">
      SupplyInsight &copy; {{ year }} — This is an automated notification. Do not reply.
    </div>
  </div>
</body>
</html>
"""
 
 