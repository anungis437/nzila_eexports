from django.core.management.base import BaseCommand
from payments.models import Currency
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed initial currency data with African currencies'

    def handle(self, *args, **kwargs):
        currencies_data = [
            # Major Global Currencies
            {
                'code': 'USD',
                'name': 'US Dollar',
                'symbol': '$',
                'exchange_rate_to_usd': Decimal('1.00'),
                'is_african': False,
                'country': 'United States',
                'stripe_supported': True,
            },
            {
                'code': 'EUR',
                'name': 'Euro',
                'symbol': '€',
                'exchange_rate_to_usd': Decimal('1.10'),
                'is_african': False,
                'country': 'European Union',
                'stripe_supported': True,
            },
            {
                'code': 'GBP',
                'name': 'British Pound',
                'symbol': '£',
                'exchange_rate_to_usd': Decimal('1.27'),
                'is_african': False,
                'country': 'United Kingdom',
                'stripe_supported': True,
            },
            
            # African Currencies - Southern Africa
            {
                'code': 'ZAR',
                'name': 'South African Rand',
                'symbol': 'R',
                'exchange_rate_to_usd': Decimal('0.054'),  # ~18.5 ZAR = 1 USD
                'is_african': True,
                'country': 'South Africa',
                'stripe_supported': True,
            },
            {
                'code': 'BWP',
                'name': 'Botswana Pula',
                'symbol': 'P',
                'exchange_rate_to_usd': Decimal('0.073'),  # ~13.7 BWP = 1 USD
                'is_african': True,
                'country': 'Botswana',
                'stripe_supported': False,
            },
            {
                'code': 'NAD',
                'name': 'Namibian Dollar',
                'symbol': 'N$',
                'exchange_rate_to_usd': Decimal('0.054'),
                'is_african': True,
                'country': 'Namibia',
                'stripe_supported': False,
            },
            {
                'code': 'ZMW',
                'name': 'Zambian Kwacha',
                'symbol': 'ZK',
                'exchange_rate_to_usd': Decimal('0.047'),  # ~21 ZMW = 1 USD
                'is_african': True,
                'country': 'Zambia',
                'stripe_supported': False,
            },
            {
                'code': 'MWK',
                'name': 'Malawian Kwacha',
                'symbol': 'MK',
                'exchange_rate_to_usd': Decimal('0.00097'),  # ~1030 MWK = 1 USD
                'is_african': True,
                'country': 'Malawi',
                'stripe_supported': False,
            },
            {
                'code': 'SZL',
                'name': 'Eswatini Lilangeni',
                'symbol': 'L',
                'exchange_rate_to_usd': Decimal('0.054'),
                'is_african': True,
                'country': 'Eswatini',
                'stripe_supported': False,
            },
            {
                'code': 'LSL',
                'name': 'Lesotho Loti',
                'symbol': 'L',
                'exchange_rate_to_usd': Decimal('0.054'),
                'is_african': True,
                'country': 'Lesotho',
                'stripe_supported': False,
            },
            {
                'code': 'MZN',
                'name': 'Mozambican Metical',
                'symbol': 'MT',
                'exchange_rate_to_usd': Decimal('0.016'),  # ~63 MZN = 1 USD
                'is_african': True,
                'country': 'Mozambique',
                'stripe_supported': False,
            },
            
            # African Currencies - West Africa
            {
                'code': 'NGN',
                'name': 'Nigerian Naira',
                'symbol': '₦',
                'exchange_rate_to_usd': Decimal('0.0013'),  # ~770 NGN = 1 USD
                'is_african': True,
                'country': 'Nigeria',
                'stripe_supported': False,
            },
            {
                'code': 'GHS',
                'name': 'Ghanaian Cedi',
                'symbol': 'GH₵',
                'exchange_rate_to_usd': Decimal('0.084'),  # ~11.9 GHS = 1 USD
                'is_african': True,
                'country': 'Ghana',
                'stripe_supported': False,
            },
            {
                'code': 'XOF',
                'name': 'West African CFA Franc',
                'symbol': 'CFA',
                'exchange_rate_to_usd': Decimal('0.0017'),  # ~600 XOF = 1 USD
                'is_african': True,
                'country': 'West African Economic and Monetary Union',
                'stripe_supported': False,
            },
            {
                'code': 'SLL',
                'name': 'Sierra Leonean Leone',
                'symbol': 'Le',
                'exchange_rate_to_usd': Decimal('0.000051'),
                'is_african': True,
                'country': 'Sierra Leone',
                'stripe_supported': False,
            },
            {
                'code': 'LRD',
                'name': 'Liberian Dollar',
                'symbol': 'L$',
                'exchange_rate_to_usd': Decimal('0.0053'),
                'is_african': True,
                'country': 'Liberia',
                'stripe_supported': False,
            },
            
            # African Currencies - East Africa
            {
                'code': 'KES',
                'name': 'Kenyan Shilling',
                'symbol': 'KSh',
                'exchange_rate_to_usd': Decimal('0.0077'),  # ~130 KES = 1 USD
                'is_african': True,
                'country': 'Kenya',
                'stripe_supported': False,
            },
            {
                'code': 'TZS',
                'name': 'Tanzanian Shilling',
                'symbol': 'TSh',
                'exchange_rate_to_usd': Decimal('0.00040'),  # ~2500 TZS = 1 USD
                'is_african': True,
                'country': 'Tanzania',
                'stripe_supported': False,
            },
            {
                'code': 'UGX',
                'name': 'Ugandan Shilling',
                'symbol': 'USh',
                'exchange_rate_to_usd': Decimal('0.00027'),  # ~3700 UGX = 1 USD
                'is_african': True,
                'country': 'Uganda',
                'stripe_supported': False,
            },
            {
                'code': 'RWF',
                'name': 'Rwandan Franc',
                'symbol': 'FRw',
                'exchange_rate_to_usd': Decimal('0.00082'),  # ~1220 RWF = 1 USD
                'is_african': True,
                'country': 'Rwanda',
                'stripe_supported': False,
            },
            {
                'code': 'ETB',
                'name': 'Ethiopian Birr',
                'symbol': 'Br',
                'exchange_rate_to_usd': Decimal('0.018'),
                'is_african': True,
                'country': 'Ethiopia',
                'stripe_supported': False,
            },
            {
                'code': 'SOS',
                'name': 'Somali Shilling',
                'symbol': 'Sh',
                'exchange_rate_to_usd': Decimal('0.0018'),
                'is_african': True,
                'country': 'Somalia',
                'stripe_supported': False,
            },
            
            # African Currencies - North Africa
            {
                'code': 'EGP',
                'name': 'Egyptian Pound',
                'symbol': 'E£',
                'exchange_rate_to_usd': Decimal('0.032'),  # ~31 EGP = 1 USD
                'is_african': True,
                'country': 'Egypt',
                'stripe_supported': False,
            },
            {
                'code': 'MAD',
                'name': 'Moroccan Dirham',
                'symbol': 'د.م.',
                'exchange_rate_to_usd': Decimal('0.10'),  # ~10 MAD = 1 USD
                'is_african': True,
                'country': 'Morocco',
                'stripe_supported': False,
            },
            {
                'code': 'TND',
                'name': 'Tunisian Dinar',
                'symbol': 'د.ت',
                'exchange_rate_to_usd': Decimal('0.32'),  # ~3.1 TND = 1 USD
                'is_african': True,
                'country': 'Tunisia',
                'stripe_supported': False,
            },
            {
                'code': 'DZD',
                'name': 'Algerian Dinar',
                'symbol': 'د.ج',
                'exchange_rate_to_usd': Decimal('0.0075'),
                'is_african': True,
                'country': 'Algeria',
                'stripe_supported': False,
            },
            {
                'code': 'LYD',
                'name': 'Libyan Dinar',
                'symbol': 'ل.د',
                'exchange_rate_to_usd': Decimal('0.21'),
                'is_african': True,
                'country': 'Libya',
                'stripe_supported': False,
            },
            
            # African Currencies - Central Africa
            {
                'code': 'XAF',
                'name': 'Central African CFA Franc',
                'symbol': 'FCFA',
                'exchange_rate_to_usd': Decimal('0.0017'),  # ~600 XAF = 1 USD
                'is_african': True,
                'country': 'Central African Economic and Monetary Community',
                'stripe_supported': False,
            },
            {
                'code': 'AOA',
                'name': 'Angolan Kwanza',
                'symbol': 'Kz',
                'exchange_rate_to_usd': Decimal('0.0012'),  # ~830 AOA = 1 USD
                'is_african': True,
                'country': 'Angola',
                'stripe_supported': False,
            },
            {
                'code': 'CDF',
                'name': 'Congolese Franc',
                'symbol': 'FC',
                'exchange_rate_to_usd': Decimal('0.00037'),
                'is_african': True,
                'country': 'Democratic Republic of the Congo',
                'stripe_supported': False,
            },
            
            # African Currencies - Island Nations
            {
                'code': 'MUR',
                'name': 'Mauritian Rupee',
                'symbol': '₨',
                'exchange_rate_to_usd': Decimal('0.022'),  # ~45 MUR = 1 USD
                'is_african': True,
                'country': 'Mauritius',
                'stripe_supported': False,
            },
            {
                'code': 'SCR',
                'name': 'Seychellois Rupee',
                'symbol': '₨',
                'exchange_rate_to_usd': Decimal('0.074'),  # ~13.5 SCR = 1 USD
                'is_african': True,
                'country': 'Seychelles',
                'stripe_supported': False,
            },
            {
                'code': 'MGA',
                'name': 'Malagasy Ariary',
                'symbol': 'Ar',
                'exchange_rate_to_usd': Decimal('0.00022'),
                'is_african': True,
                'country': 'Madagascar',
                'stripe_supported': False,
            },
        ]

        created_count = 0
        updated_count = 0

        for currency_data in currencies_data:
            currency, created = Currency.objects.update_or_create(
                code=currency_data['code'],
                defaults=currency_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {currency.code} - {currency.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'→ Updated: {currency.code} - {currency.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Currency seeding complete!'
                f'\n   Created: {created_count} currencies'
                f'\n   Updated: {updated_count} currencies'
                f'\n   Total: {Currency.objects.count()} currencies in database'
                f'\n   African currencies: {Currency.objects.filter(is_african=True).count()}'
            )
        )
