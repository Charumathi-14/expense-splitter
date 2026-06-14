import csv
import io
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime

from django.db import models, transaction
from django.conf import settings

from accounts.models import User
from groups.models import Group, GroupMember
from expenses.models import Expense, ExpenseParticipant
from settlements.models import Settlement
from imports.models import ImportIssue


class CSVImporter:

    DEFAULT_CURRENCY = getattr(settings, 'DEFAULT_CURRENCY', 'INR')
    CURRENCY_RATES = getattr(settings, 'CURRENCY_RATES', {
        'INR': Decimal('1'),
        'USD': Decimal('82.00')
    })

    FIELD_ALIASES = {
        'amount': ['amount', 'total', 'value', 'sum', 'amt'],
        'currency': ['currency', 'curr', 'ccy'],
        'date': ['date', 'expense_date', 'payment_date', 'transaction_date'],
        'paid_by': ['paid_by', 'payer', 'paidby'],
        'receiver': ['receiver', 'received_by', 'payee', 'paid_to'],
        'participants': ['participants', 'paid_for', 'shared_with', 'split_with'],
        'description': ['description', 'details', 'title', 'notes', 'remarks'],
        'group': ['group', 'group_name', 'flat'],
        'split_type': ['split_type', 'share_type', 'type_of_split'],
        'split_values': ['split_values', 'shares', 'share_values']
    }

    DATE_FORMATS = [
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%d %b %Y',
        '%d %B %Y'
    ]

    REFUND_KEYWORDS = ['refund', 'return', 'reversed', 'credit']

    def process(self, file_obj, batch=None):
        issues = []
        created = {'expenses': 0, 'settlements': 0, 'skipped': 0}

        text_file = self._open_text_file(file_obj)
        reader = csv.DictReader(text_file)
        rows = list(reader)

        duplicate_map = self._find_duplicates(rows)

        for index, raw_row in enumerate(rows):
            row_number = index + 2
            row = self._normalize_row(raw_row)
            duplicate_key = duplicate_map.get(self._row_signature(row))
            if duplicate_key is not None and duplicate_key < index:
                issues.append(self._record_issue(
                    batch,
                    row_number,
                    'Duplicate row',
                    'warning',
                    'Duplicate expense row detected; keeping first occurrence.',
                    'skipped duplicate row'
                ))
                created['skipped'] += 1
                continue

            kind = self._determine_row_kind(row)
            amount, currency, amount_issue = self._parse_amount(row, row_number, batch)
            if amount is None:
                issues.append(amount_issue)
                created['skipped'] += 1
                continue

            date, date_issue = self._parse_date(row, row_number, batch)
            if date is None:
                issues.append(date_issue)
                created['skipped'] += 1
                continue

            group, group_issue = self._resolve_group(row, row_number, batch)
            if group is None:
                issues.append(group_issue)
                created['skipped'] += 1
                continue

            paid_by = self._resolve_user(row.get('paid_by'), row_number, batch)
            if paid_by is None:
                issues.append(self._record_issue(
                    batch,
                    row_number,
                    'Unknown payer',
                    'error',
                    'Could not identify payer from the row.',
                    'skipped row'
                ))
                created['skipped'] += 1
                continue

            if kind == 'settlement':
                receiver = self._resolve_user(row.get('receiver'), row_number, batch)
                if receiver is None:
                    issues.append(self._record_issue(
                        batch,
                        row_number,
                        'Invalid settlement',
                        'error',
                        'Settlement rows require a valid receiver.',
                        'skipped row'
                    ))
                    created['skipped'] += 1
                    continue

                self._create_settlement(
                    group, paid_by, receiver, amount, currency, date, row
                )
                created['settlements'] += 1
                continue

            participants, participant_issues = self._resolve_participants(
                row, group, date, paid_by, row_number, batch
            )
            issues.extend(participant_issues)

            if not participants:
                issues.append(self._record_issue(
                    batch,
                    row_number,
                    'Missing participants',
                    'error',
                    'No valid participants could be resolved for this expense.',
                    'skipped row'
                ))
                created['skipped'] += 1
                continue

            split_type = self._get_field(row, 'split_type') or 'equal'
            share_rows, share_issue = self._build_shares(
                row, split_type, participants, amount, row_number, batch
            )

            if share_rows is None:
                issues.append(share_issue)
                created['skipped'] += 1
                continue

            self._create_expense(
                group,
                paid_by,
                amount,
                currency,
                date,
                row,
                split_type,
                share_rows
            )
            created['expenses'] += 1

        return {
            'created': created,
            'issues': [issue for issue in issues if issue is not None]
        }

    def _open_text_file(self, file_obj):
        if hasattr(file_obj, 'read') and hasattr(file_obj, 'encoding'):
            return io.TextIOWrapper(file_obj, encoding='utf-8', newline='')
        return io.TextIOWrapper(file_obj, encoding='utf-8', newline='')

    def _normalize_row(self, raw_row):
        return {
            self._normalize_header(key): (value or '').strip()
            for key, value in raw_row.items()
        }

    def _normalize_header(self, header):
        return re.sub(r'[^a-z0-9_]+', '_', header.strip().lower())

    def _get_field(self, row, field_name):
        for alias in self.FIELD_ALIASES.get(field_name, []):
            if alias in row and row[alias] != '':
                return row[alias]
        return None

    def _parse_amount(self, row, row_number, batch):
        raw_amount = self._get_field(row, 'amount')
        raw_currency = self._get_field(row, 'currency')
        if not raw_amount:
            return None, None, self._record_issue(
                batch,
                row_number,
                'Missing amount',
                'error',
                'Amount is required for every row.',
                'skipped row'
            )

        currency = self.DEFAULT_CURRENCY
        if raw_currency:
            currency = raw_currency.strip().upper()

        raw_amount = raw_amount.replace(',', '')
        raw_amount = raw_amount.replace('USD', '').replace('INR', '')
        if raw_amount.startswith('$'):
            currency = 'USD'
            raw_amount = raw_amount[1:]

        try:
            amount = Decimal(raw_amount)
        except InvalidOperation:
            return None, None, self._record_issue(
                batch,
                row_number,
                'Invalid amount',
                'error',
                f'Unable to parse amount "{self._get_field(row, "amount")}".',
                'skipped row'
            )

        if amount < 0:
            description = self._get_field(row, 'description') or ''
            if any(keyword in description.lower() for keyword in self.REFUND_KEYWORDS):
                amount = abs(amount)
                self._record_issue(
                    batch,
                    row_number,
                    'Refund detected',
                    'warning',
                    'Negative amount treated as refund and converted to positive value.',
                    'accepted as refund'
                )
            else:
                return None, None, self._record_issue(
                    batch,
                    row_number,
                    'Negative amount',
                    'error',
                    'Negative amounts are not allowed unless the row is a refund.',
                    'skipped row'
                )

        return amount.quantize(Decimal('0.01')), currency, None

    def _parse_date(self, row, row_number, batch):
        raw_date = self._get_field(row, 'date')
        if not raw_date:
            return None, self._record_issue(
                batch,
                row_number,
                'Missing date',
                'error',
                'Every row must include a date.',
                'skipped row'
            )

        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(raw_date, fmt).date(), None
            except ValueError:
                continue

        return None, self._record_issue(
            batch,
            row_number,
            'Invalid date',
            'error',
            f'Unable to parse date "{raw_date}".',
            'skipped row'
        )

    def _resolve_group(self, row, row_number, batch):
        name = self._get_field(row, 'group')
        if not name:
            return None, self._record_issue(
                batch,
                row_number,
                'Missing group',
                'error',
                'Every row must include a group name.',
                'skipped row'
            )

        group, created = Group.objects.get_or_create(name=name)
        if created:
            self._record_issue(
                batch,
                row_number,
                'Group created',
                'info',
                f'Created a new group named "{name}".',
                'created group'
            )
        return group, None

    def _resolve_user(self, raw_user, row_number, batch):
        if not raw_user:
            return None

        raw_user = raw_user.strip()
        if '@' in raw_user:
            user = User.objects.filter(email__iexact=raw_user).first()
            if user:
                return user
            name = raw_user.split('@')[0].replace('.', ' ').title()
            email = raw_user
        else:
            name = raw_user.title()
            email = f"{re.sub(r'[^a-z0-9]+', '.', raw_user.strip().lower())}@import.local"
            email = re.sub(r'\.+', '.', email).strip('.')

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'password': 'imported'
            }
        )

        if created:
            self._record_issue(
                batch,
                row_number,
                'Created user',
                'info',
                f'Created user profile for "{name}".',
                'created user'
            )

        return user

    def _resolve_participants(self, row, group, date, payer, row_number, batch):
        issues = []
        participant_names = self._get_field(row, 'participants')
        participants = []

        if participant_names:
            participants = [name.strip() for name in re.split(r'[;,]', participant_names) if name.strip()]

        if not participants:
            active_members = self._active_group_members(group, date)
            if active_members:
                participants = [member.user.name for member in active_members]
                issues.append(self._record_issue(
                    batch,
                    row_number,
                    'Participants inferred',
                    'warning',
                    'Participants were missing; inferred from active group membership on this date.',
                    'used active members'
                ))
            else:
                participants = [payer.name]
                issues.append(self._record_issue(
                    batch,
                    row_number,
                    'Default participant',
                    'warning',
                    'No participants could be inferred; expense will be recorded for the payer only.',
                    'used payer only'
                ))

        resolved = []
        for participant_name in participants:
            user = self._resolve_user(participant_name, row_number, batch)
            if user:
                self._ensure_membership(group, user, date)
                resolved.append(user)
            else:
                issues.append(self._record_issue(
                    batch,
                    row_number,
                    'Unknown participant',
                    'warning',
                    f'Could not resolve participant "{participant_name}".',
                    'skipped participant'
                ))

        if payer not in resolved:
            resolved.append(payer)

        mapped = []
        for user in resolved:
            mapped.append({
                'user': user,
                'share_amount': None,
                'percentage': None,
                'weight': None
            })

        return mapped, issues

    def _active_group_members(self, group, date):
        return GroupMember.objects.filter(
            group=group,
            joined_at__lte=date,
            is_active=True
        ).filter(
            models.Q(left_at__isnull=True) | models.Q(left_at__gte=date)
        )

    def _ensure_membership(self, group, user, date):
        membership = GroupMember.objects.filter(group=group, user=user).order_by('-joined_at').first()
        if membership is None:
            GroupMember.objects.create(group=group, user=user, joined_at=date, is_active=True)
            return

        if membership.left_at and date > membership.left_at:
            GroupMember.objects.create(group=group, user=user, joined_at=date, is_active=True)

    def _build_shares(self, row, split_type, participants, total_amount, row_number, batch):
        share_values = self._get_field(row, 'split_values')
        if split_type == 'equal' or not share_values:
            count = len(participants)
            if count == 0:
                return None, self._record_issue(
                    batch,
                    row_number,
                    'Empty participant list',
                    'error',
                    'Equal split requires at least one participant.',
                    'skipped row'
                )
            share = (total_amount / Decimal(count)).quantize(Decimal('0.01'))
            return [
                {
                    'user': participant['user'],
                    'share_amount': share,
                    'percentage': None,
                    'weight': None
                }
                for participant in participants
            ], None

        parsed = self._parse_split_values(share_values)
        if parsed is None or len(parsed) != len(participants):
            return None, self._record_issue(
                batch,
                row_number,
                'Invalid split values',
                'error',
                'Split values could not be mapped to participants or do not match participant count.',
                'skipped row'
            )

        if split_type == 'exact':
            return [
                {
                    'user': participants[idx]['user'],
                    'share_amount': Decimal(value).quantize(Decimal('0.01')),
                    'percentage': None,
                    'weight': None
                }
                for idx, value in enumerate(parsed)
            ], None

        if split_type == 'percentage':
            computed = []
            for idx, value in enumerate(parsed):
                try:
                    pct = Decimal(value)
                except InvalidOperation:
                    return None, self._record_issue(
                        batch,
                        row_number,
                        'Invalid percentage',
                        'error',
                        'Percentage values must be numeric.',
                        'skipped row'
                    )
                share_amount = (total_amount * pct / Decimal('100')).quantize(Decimal('0.01'))
                computed.append({
                    'user': participants[idx]['user'],
                    'share_amount': share_amount,
                    'percentage': pct,
                    'weight': None
                })
            return computed, None

        if split_type == 'weight':
            weights = [Decimal(value) for value in parsed]
            total_weight = sum(weights)
            if total_weight == 0:
                return None, self._record_issue(
                    batch,
                    row_number,
                    'Invalid weights',
                    'error',
                    'Weight split type requires positive weight values.',
                    'skipped row'
                )
            computed = []
            for idx, weight in enumerate(weights):
                share_amount = (total_amount * weight / total_weight).quantize(Decimal('0.01'))
                computed.append({
                    'user': participants[idx]['user'],
                    'share_amount': share_amount,
                    'percentage': None,
                    'weight': int(weight)
                })
            return computed, None

        return None, self._record_issue(
            batch,
            row_number,
            'Unsupported split type',
            'error',
            f'Split type "{split_type}" is not supported.',
            'skipped row'
        )

    def _parse_split_values(self, share_values):
        if isinstance(share_values, str):
            values = re.split(r'[;,]', share_values)
            parsed = [value.strip().replace('%', '') for value in values if value.strip()]
            return parsed
        return None

    def _create_expense(self, group, paid_by, amount, currency, date, row, split_type, share_rows):
        title = self._get_field(row, 'description') or 'Imported expense'
        expense = Expense.objects.create(
            group=group,
            title=title,
            description=self._get_field(row, 'description') or '',
            amount=amount,
            currency=currency,
            paid_by=paid_by,
            split_type=split_type,
            expense_date=date
        )

        for share in share_rows:
            ExpenseParticipant.objects.create(
                expense=expense,
                user=share['user'],
                share_amount=share['share_amount'],
                percentage=share.get('percentage') or Decimal('0'),
                weight=share.get('weight') or 0
            )

    def _create_settlement(self, group, payer, receiver, amount, currency, date, row):
        Settlement.objects.create(
            group=group,
            payer=payer,
            receiver=receiver,
            amount=amount,
            currency=currency,
            settlement_date=date,
            notes=self._get_field(row, 'description') or ''
        )

    def _determine_row_kind(self, row):
        row_type = self._get_field(row, 'type')
        if row_type:
            row_type = row_type.strip().lower()
            if row_type in ['payment', 'settlement', 'transfer']:
                return 'settlement'
        if self._get_field(row, 'receiver'):
            return 'settlement'
        return 'expense'

    def _record_issue(self, batch, row_number, issue_type, severity, description, action_taken):
        issue_data = {
            'row_number': row_number,
            'issue_type': issue_type,
            'severity': severity,
            'description': description,
            'action_taken': action_taken,
            'status': 'pending'
        }
        if batch is not None:
            ImportIssue.objects.create(batch=batch, **issue_data)
        return issue_data

    def _row_signature(self, row):
        return (
            self._get_field(row, 'date') or '',
            self._get_field(row, 'description') or '',
            self._get_field(row, 'amount') or '',
            self._get_field(row, 'paid_by') or '',
            self._get_field(row, 'group') or ''
        )

    def _find_duplicates(self, rows):
        seen = {}
        duplicates = {}
        for index, raw_row in enumerate(rows):
            row = self._normalize_row(raw_row)
            signature = self._row_signature(row)
            if signature in seen:
                duplicates[signature] = seen[signature]
            else:
                seen[signature] = index
        return duplicates
