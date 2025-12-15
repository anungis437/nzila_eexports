# Nzila Export Hub - Marketing Website

Public-facing marketing website for the Nzila Export Hub platform.

## 🎯 Purpose

This is the storefront for Nzila Export Hub - designed to attract:
- Canadian vehicle dealers
- Export brokers
- West African buyers
- Investors and funders (IRAP, CDAP, MEIE)

## 🚀 Tech Stack

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- Static site generation for optimal performance

## 📦 Features

### Implemented Sections

1. **Hero Section** - Clear value proposition with bilingual support (EN/FR)
2. **How It Works** - 4-step process visualization
3. **Platform Features** - 8 key feature cards
4. **Live Metrics** - Animated statistics with geographic reach
5. **Testimonials** - Social proof with partner badges
6. **Call to Action** - Lead capture form with role selection
7. **Footer** - Complete site navigation and contact info

### Key Highlights

✅ Fully responsive mobile-first design
✅ Bilingual (English/French) throughout
✅ SEO optimized with meta tags
✅ Clean, modern B2B SaaS aesthetic
✅ Nzila brand colors (emerald green, deep blue)
✅ Lead capture form ready for backend integration
✅ Partner badges (IRAP, CDAP, MEIE)
✅ Trust signals and testimonials

## 🛠️ Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd marketing-site
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

### Static Export

```bash
npm run build
# Output in /out directory
```

## 📁 Project Structure

```
marketing-site/
├── app/
│   ├── layout.tsx       # Root layout with metadata
│   ├── page.tsx         # Home page
│   └── globals.css      # Global styles
├── components/
│   ├── Hero.tsx         # Hero section with language switcher
│   ├── HowItWorks.tsx   # 4-step process
│   ├── Features.tsx     # Platform features grid
│   ├── LiveMetrics.tsx  # Animated statistics
│   ├── Testimonials.tsx # Social proof
│   ├── CallToAction.tsx # Lead capture form
│   └── Footer.tsx       # Footer with links
├── public/              # Static assets
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

## 🎨 Design System

### Colors

- **Nzila Green**: Emerald (primary action color)
  - `nzila-green-500`: #10b981
- **Nzila Blue**: Deep blue (secondary/trust color)
  - `nzila-blue-900`: #1e3a8a

### Typography

- **Font**: Inter (system font)
- **Headings**: Bold, large scale
- **Body**: Regular weight, comfortable reading size

## 🔌 Backend Integration Points

### Lead Capture Form

Currently logs to console. To integrate:

1. **Supabase** (recommended):
```typescript
// In CallToAction.tsx
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  const { data, error } = await supabase
    .from('leads')
    .insert([{ email, role, company }])
  // Handle response
}
```

2. **Direct API**:
```typescript
const response = await fetch('/api/leads', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, role, company })
})
```

### Live Metrics

Currently uses static animated numbers. To show real data:

```typescript
// In LiveMetrics.tsx
useEffect(() => {
  fetch('/api/public/metrics')
    .then(res => res.json())
    .then(data => setMetrics(data))
}, [])
```

## 🌍 Internationalization

### Language Switching

Implemented in Hero and Footer components. To expand:

1. Create `locales/en.json` and `locales/fr.json`
2. Use `next-intl` or `i18next`
3. Update all components to use translation keys

## 📱 Mobile Optimization

- Fully responsive breakpoints (sm, md, lg)
- Touch-friendly buttons and forms
- Optimized images and assets
- Fast page load times

## 🔍 SEO Optimization

### Current Implementation

```typescript
// In app/layout.tsx
export const metadata: Metadata = {
  title: 'Nzila Export Hub - Connect Canadian Dealers...',
  description: 'Export Smarter. Nzila Does the Heavy Lifting...',
  keywords: 'vehicle export, Canada to Africa, auto trade...'
}
```

### Recommended Additions

- Structured data (JSON-LD)
- Open Graph tags
- Twitter cards
- Sitemap.xml
- robots.txt

## 📊 Analytics Integration

Add to `app/layout.tsx`:

```typescript
// Google Analytics
<Script src="https://www.googletagmanager.com/gtag/js?id=GA_ID" />
<Script id="google-analytics">
  {`
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'GA_ID');
  `}
</Script>
```

## 🚢 Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm run build
# Deploy /out directory
```

### Custom Server

```bash
npm run build
npm start
# Or use PM2, Docker, etc.
```

## 📝 Content Updates

### Testimonials

Edit `components/Testimonials.tsx`:
```typescript
const testimonials = [
  {
    quote: "Your testimonial here...",
    author: "Name",
    role: "Title",
    location: "City",
    image: "🚗"
  }
]
```

### Metrics

Edit `components/LiveMetrics.tsx`:
```typescript
const targetMetrics = {
  vehiclesExported: 2847,  // Update these
  verifiedBuyers: 156,
  // ...
}
```

## 🤝 Contributing

This is the marketing site for the Nzila Export Hub backend platform. See main project README for full platform documentation.

## 📄 License

Proprietary - Nzila Export Hub

## 🆘 Support

For questions about this marketing site:
- Email: dev@nzilaexport.com
- Slack: #marketing-site

---

Built with ❤️ for international trade success
