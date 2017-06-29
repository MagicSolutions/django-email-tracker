from __future__ import absolute_import


from django.core.mail import EmailMessage
from django.test import TestCase
from email_tracker.models import TrackedEmail, EmailCategory


class EmailTrackerAdminTestCase(TestCase):
    def setUp(self):
        super(EmailTrackerAdminTestCase, self).setUp()
        self.category = EmailCategory.objects.create(title='Test Mail')

    def test_create_mail_from_message(self):

        message = EmailMessage(
            subject='Test Subject',
            body='Text body',
            from_email='from@example.com',
            to=['to@example.com', 'to2@example.com'],
            cc=['cc@example.com'],
            bcc=['bcc@example.com'],
        )

        tracked_email = TrackedEmail.objects.create_from_message(message)
        self.assertEqual(tracked_email.subject, 'Test Subject')
        self.assertEqual(tracked_email.body, 'Text body')
        self.assertEqual(tracked_email.from_email, 'from@example.com')
        self.assertEqual(tracked_email.recipients, 'to@example.com, to2@example.com, cc@example.com, bcc@example.com')
        self.assertEqual(tracked_email.cc, 'cc@example.com')
        self.assertEqual(tracked_email.bcc, 'bcc@example.com')
        self.assertIsNone(tracked_email.category)

    def test_autocreate_category_from_message_headers(self):
        message = EmailMessage(
            subject='Test Subject',
            body='Text body',
            from_email='from@example.com',
            to=['to@example.com'],
        )
        message.extra_headers['X-Category'] = 'Some category'

        tracked_email = TrackedEmail.objects.create_from_message(message)
        self.assertIsNotNone(tracked_email.category)
        self.assertEqual(tracked_email.category.title, 'Some category')

    def test_reuse_category_from_message_headers(self):
        message = EmailMessage(
            subject='Test Subject',
            body='Text body',
            from_email='from@example.com',
            to=['to@example.com'],
        )
        message.extra_headers['X-Category'] = self.category.title

        tracked_email = TrackedEmail.objects.create_from_message(message)
        self.assertEqual(tracked_email.category, self.category)

    def test_reuse_category_from_subject(self):
        message = EmailMessage(
            subject=self.category.title,
            body='Text body',
            from_email='from@example.com',
            to=['to@example.com'],
        )

        tracked_email = TrackedEmail.objects.create_from_message(message)
        self.assertEqual(tracked_email.category, self.category)