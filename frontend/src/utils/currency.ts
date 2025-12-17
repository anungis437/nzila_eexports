// Currency exchange rates (base: CAD)
// These should ideally come from an API, but for now we'll use approximate rates
export const EXCHANGE_RATES = {
  CAD: 1.0,
  // West Africa (CFA Franc BCEAO)
  XOF: 400.0,
  // Central Africa (CFA Franc BEAC)
  XAF: 400.0,
  // Nigerian Naira
  NGN: 620.0,
  // Ghanaian Cedi
  GHS: 8.2,
  // Kenyan Shilling
  KES: 93.0,
  // South African Rand
  ZAR: 13.5,
  // Tanzanian Shilling
  TZS: 1850.0,
  // Ugandan Shilling
  UGX: 2750.0,
  // Rwandan Franc
  RWF: 935.0,
  // Ethiopian Birr
  ETB: 80.0,
  // Egyptian Pound
  EGP: 36.0,
  // Moroccan Dirham
  MAD: 7.2,
  // Tunisian Dinar
  TND: 2.3,
  // Algerian Dinar
  DZD: 99.0,
  // Botswana Pula
  BWP: 9.9,
  // Zambian Kwacha
  ZMW: 19.5,
  // Mozambican Metical
  MZN: 47.0,
  // Angolan Kwanza
  AOA: 620.0,
  // CDF (Congolese Franc)
  CDF: 2050.0,
  // USD
  USD: 0.73,
  // EUR
  EUR: 0.67,
  // GBP
  GBP: 0.57,
};

export interface Currency {
  code: string;
  name: string;
  symbol: string;
  isAfrican: boolean;
}

export const CURRENCIES: Currency[] = [
  { code: 'CAD', name: 'Canadian Dollar', symbol: '$', isAfrican: false },
  { code: 'XOF', name: 'West African CFA Franc', symbol: 'CFA', isAfrican: true },
  { code: 'XAF', name: 'Central African CFA Franc', symbol: 'FCFA', isAfrican: true },
  { code: 'NGN', name: 'Nigerian Naira', symbol: '₦', isAfrican: true },
  { code: 'GHS', name: 'Ghanaian Cedi', symbol: '₵', isAfrican: true },
  { code: 'KES', name: 'Kenyan Shilling', symbol: 'KSh', isAfrican: true },
  { code: 'ZAR', name: 'South African Rand', symbol: 'R', isAfrican: true },
  { code: 'TZS', name: 'Tanzanian Shilling', symbol: 'TSh', isAfrican: true },
  { code: 'UGX', name: 'Ugandan Shilling', symbol: 'USh', isAfrican: true },
  { code: 'RWF', name: 'Rwandan Franc', symbol: 'FRw', isAfrican: true },
  { code: 'ETB', name: 'Ethiopian Birr', symbol: 'Br', isAfrican: true },
  { code: 'EGP', name: 'Egyptian Pound', symbol: 'E£', isAfrican: true },
  { code: 'MAD', name: 'Moroccan Dirham', symbol: 'MAD', isAfrican: true },
  { code: 'TND', name: 'Tunisian Dinar', symbol: 'DT', isAfrican: true },
  { code: 'DZD', name: 'Algerian Dinar', symbol: 'DA', isAfrican: true },
  { code: 'BWP', name: 'Botswana Pula', symbol: 'P', isAfrican: true },
  { code: 'ZMW', name: 'Zambian Kwacha', symbol: 'ZK', isAfrican: true },
  { code: 'MZN', name: 'Mozambican Metical', symbol: 'MT', isAfrican: true },
  { code: 'AOA', name: 'Angolan Kwanza', symbol: 'Kz', isAfrican: true },
  { code: 'CDF', name: 'Congolese Franc', symbol: 'FC', isAfrican: true },
  { code: 'USD', name: 'US Dollar', symbol: '$', isAfrican: false },
  { code: 'EUR', name: 'Euro', symbol: '€', isAfrican: false },
  { code: 'GBP', name: 'British Pound', symbol: '£', isAfrican: false },
];

export const convertCurrency = (
  amount: number,
  fromCurrency: string,
  toCurrency: string
): number => {
  const fromRate = EXCHANGE_RATES[fromCurrency as keyof typeof EXCHANGE_RATES] || 1;
  const toRate = EXCHANGE_RATES[toCurrency as keyof typeof EXCHANGE_RATES] || 1;
  
  // Convert to CAD first, then to target currency
  const amountInCAD = amount / fromRate;
  return amountInCAD * toRate;
};

export const formatCurrency = (amount: number, currencyCode: string): string => {
  const currency = CURRENCIES.find(c => c.code === currencyCode);
  const symbol = currency?.symbol || currencyCode;
  
  return `${symbol} ${amount.toLocaleString('en-US', { 
    minimumFractionDigits: 0,
    maximumFractionDigits: 0 
  })}`;
};
