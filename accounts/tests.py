from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from .models import Account, Transaction
import uuid
import csv
import io

class AccountModelTest(TestCase):
    def test_account_creation(self):
        """Test account creation with valid data"""
        account = Account.objects.create(
            name="Test Account",
            balance=Decimal('1000.00')
        )
        
        self.assertIsInstance(account.id, uuid.UUID)
        self.assertEqual(account.name, "Test Account")
        self.assertEqual(account.balance, Decimal('1000.00'))
        self.assertTrue(account.slug)
        self.assertEqual(str(account), "Test Account")

    def test_account_slug_generation(self):
        """Test unique slug generation"""
        account1 = Account.objects.create(
            name="Test Account",
            balance=Decimal('1000.00')
        )
        account2 = Account.objects.create(
            name="Test Account",
            balance=Decimal('2000.00')
        )

        self.assertNotEqual(account1.slug, account2.slug)
        self.assertTrue(account1.slug.startswith('test-account'))
        self.assertTrue(account2.slug.startswith('test-account'))

class TransactionModelTest(TestCase):
    def setUp(self):
        """Create accounts for transaction testing"""
        self.sender = Account.objects.create(
            name="Sender Account",
            balance=Decimal('5000.00')
        )
        self.receiver = Account.objects.create(
            name="Receiver Account", 
            balance=Decimal('1000.00')
        )

    def test_transaction_creation(self):
        """Test transaction creation and default date"""
        transaction = Transaction.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('500.00')
        )

        self.assertEqual(transaction.sender, self.sender)
        self.assertEqual(transaction.receiver, self.receiver)
        self.assertEqual(transaction.amount, Decimal('500.00'))
        self.assertIsNotNone(transaction.date)
        self.assertTrue(str(transaction).startswith(f'{self.sender} sent 500.00 to {self.receiver}'))

class ViewsTest(TestCase):
    def setUp(self):
        """Set up test client and create test accounts"""
        self.client = Client()
        self.sender = Account.objects.create(
            name="Sender Account",
            balance=Decimal('5000.00')
        )
        self.receiver = Account.objects.create(
            name="Receiver Account", 
            balance=Decimal('1000.00')
        )

    def test_list_accounts_view(self):
        """Test accounts listing view"""
        response = self.client.get(reverse('accounts:list_accounts'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('accounts', response.context)
        self.assertIn('total_accounts', response.context)
        self.assertIn('total_balance', response.context)

    def test_account_detail_view(self):
        """Test account detail view"""
        response = self.client.get(reverse('accounts:account_detail', kwargs={'slug': self.sender.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['account'], self.sender)

    def test_transaction_view(self):
        """Test transaction processing"""
        transaction_data = {
            'sender': str(self.sender.id),
            'receiver': str(self.receiver.id),
            'amount': '500.00'
        }
        
        response = self.client.post(reverse('accounts:transaction'), transaction_data)
        
        # Refresh accounts from database
        self.sender.refresh_from_db()
        self.receiver.refresh_from_db()

        self.assertEqual(self.sender.balance, Decimal('4500.00'))
        self.assertEqual(self.receiver.balance, Decimal('1500.00'))
        self.assertTrue(Transaction.objects.filter(
            sender=self.sender, 
            receiver=self.receiver, 
            amount=Decimal('500.00')
        ).exists())

    def test_invalid_transaction(self):
        """Test invalid transaction scenarios"""
        # Insufficient funds
        transaction_data = {
            'sender': str(self.sender.id),
            'receiver': str(self.receiver.id),
            'amount': '6000.00'
        }
        
        response = self.client.post(reverse('accounts:transaction'), transaction_data)
        
        # Accounts should remain unchanged
        self.sender.refresh_from_db()
        self.receiver.refresh_from_db()

        self.assertEqual(self.sender.balance, Decimal('5000.00'))
        self.assertEqual(self.receiver.balance, Decimal('1000.00'))

    def test_import_accounts(self):
        """Test account import functionality"""
        # Create a CSV file in memory
        csv_content = io.StringIO()
        csv_writer = csv.writer(csv_content)
        csv_writer.writerow(['ID', 'Name', 'Balance'])
        csv_writer.writerow([str(uuid.uuid4()), 'New Account', '1000.00'])
        
        csv_content.seek(0)
        
        csv_file = SimpleUploadedFile(
            "accounts.csv", 
            csv_content.getvalue().encode('utf-8'), 
            content_type='text/csv'
        )

        response = self.client.post(reverse('accounts:import_accounts'), {'csv_file': csv_file})
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Account.objects.filter(name='New Account').exists())

    def test_account_search(self):
        """Test account search functionality"""
        response = self.client.get(reverse('accounts:account_search'), {'search': 'Sender'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('accounts', response.context)
        self.assertTrue(len(response.context['accounts']) > 0)