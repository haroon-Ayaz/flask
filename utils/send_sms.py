from notifications_python_client.notifications import NotificationsAPIClient

API_KEY = "sms_notification-8413bf9f-5a51-4f58-a46c-fc4eb185fe50-c16005f8-c536-471d-9b4b-f1912dffffdd"
TEMPLATE_ID = "a6e1a749-f102-45ea-979e-5a21586275f5"

client = NotificationsAPIClient(API_KEY)

try:
    response = client.send_sms_notification(
        phone_number="+447786872193",
        template_id=TEMPLATE_ID,
        personalisation={
            "date": "2018-01-01 at 01:00PM"
        },
        reference="your reference"
    )
    print("SMS sent successfully!")
    print(response)
except Exception as e:
    print("Failed to send SMS:", e)

# {
#     'content': {
#         'body': 'REMINDER: you have an Endoscopy booked for 12 March 2025. Contact us on 0121 00000 or '
#                 'respond back with CANCEL if no longer needed.', 'from_number': '447860041655'
#     },
#     'id': 'f6c85acc-e9d1-444f-978c-6894cf6320e0',
#     'reference': None,
#     'scheduled_for': None,
#     'template': {
#         'id': 'a6e1a749-f102-45ea-979e-5a21586275f5',
#         'uri': 'https://api.notifications.service.gov.uk/services/8413bf9f-5a51-4f58-a46c-fc4eb185fe50/templates/a6e1a749-f102-45ea-979e-5a21586275f5',
#         'version': 2
#     },
#     'uri': 'https://api.notifications.service.gov.uk/v2/notifications/f6c85acc-e9d1-444f-978c-6894cf6320e0'
# }