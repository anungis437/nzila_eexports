# Nzila Export Hub - Modern Frontend

## 🎨 Design System

### Font
- **Primary Font**: Poppins (weights: 300, 400, 500, 600, 700)
- Modern, clean, professional appearance

### Color Palette
- **Primary (Amber)**: #f59e0b (primary-500)
- **Gradients**: Amber gradient for CTAs and highlights
- **Background**: Subtle gradient from amber-50 to white
- **Text**: Slate scale for hierarchy

### Components
- Built with Radix UI primitives
- Tailwind CSS for styling
- Framer Motion for animations
- Modern, card-based layouts

## 🚀 Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will run on `http://localhost:3000` and proxy API requests to `http://localhost:8000`.

### Build

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.tsx          # Main app layout with sidebar
│   │   └── ui/                 # Reusable UI components
│   ├── contexts/
│   │   ├── AuthContext.tsx     # Authentication state
│   │   └── LanguageContext.tsx # i18n (EN/FR)
│   ├── lib/
│   │   ├── api.ts             # API client
│   │   └── utils.ts           # Utility functions
│   ├── pages/
│   │   ├── Login.tsx          # Login page
│   │   ├── Dashboard.tsx      # Main dashboard
│   │   ├── Vehicles.tsx       # Vehicle management
│   │   ├── Leads.tsx          # Lead tracking
│   │   ├── Deals.tsx          # Deal pipeline
│   │   ├── Commissions.tsx    # Commission tracking
│   │   ├── Shipments.tsx      # Shipment tracking
│   │   ├── BuyerPortal.tsx    # Public buyer portal
│   │   └── Settings.tsx       # User settings
│   ├── App.tsx                # Root component
│   ├── Routes.tsx             # Route configuration
│   ├── main.tsx               # Entry point
│   └── index.css              # Global styles
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## 🔑 Key Features

### Authentication
- JWT-based authentication
- Role-based access control (Admin, Dealer, Broker, Buyer)
- Protected routes

### Internationalization
- English / French support
- Context-based translation system
- Currency conversion (CAD ↔ XOF)

### API Integration
- Axios-based API client
- React Query for data fetching and caching
- Automatic token management
- Request/response interceptors

### User Roles & Permissions
- **Admin**: Full system access
- **Dealer**: Vehicle management, view deals
- **Broker**: Lead creation, deal facilitation
- **Buyer**: Public portal access

### Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Collapsible sidebar on mobile
- Touch-friendly interactions

## 🎯 Pages Overview

### Dashboard
- Key metrics cards
- Recent activity
- Quick actions
- Role-specific views

### Vehicles
- Vehicle catalog
- Add/edit vehicles
- Photo uploads
- Filtering and search

### Leads
- Lead pipeline
- AI-powered matching
- Status management
- Buyer information

### Deals
- Deal tracking
- Workflow visualization
- Document management
- Commission calculation

### Commissions
- Earnings tracking
- Payment status
- Performance metrics

### Shipments
- Real-time tracking
- GPS integration
- Customs status
- Delivery updates

### Buyer Portal
- Access code authentication
- Order tracking
- Document upload
- Shipment monitoring

## 🔧 API Endpoints

All endpoints are proxied through Vite:
- `/api/*` → Django backend
- `/admin/*` → Django admin
- `/media/*` → Media files

### Main Endpoints
- `POST /api/accounts/login/` - User login
- `GET /api/accounts/me/` - Current user
- `GET /api/vehicles/vehicles/` - List vehicles
- `GET /api/deals/leads/` - List leads
- `GET /api/deals/deals/` - List deals
- `GET /api/commissions/commissions/` - List commissions
- `GET /api/shipments/shipments/` - List shipments

## 🎨 UI Components

### Radix UI Primitives Used
- Dialog (modals)
- Dropdown Menu
- Select
- Tabs
- Toast (notifications)
- Avatar
- Switch
- Label
- Slot

### Custom Components
- Button (variants: default, destructive, outline, secondary, ghost, link)
- Card
- Input
- Textarea
- Badge
- Skeleton (loading states)

## 🌍 Internationalization

Translation keys available in `LanguageContext`:
- Navigation items
- Common actions
- Status labels
- Form labels
- Messages

## 💾 State Management

### React Query
- Automatic caching
- Background refetching
- Optimistic updates
- Cache invalidation

### Local Storage
- JWT tokens
- Language preference
- User preferences

## 🎭 Animations

Using Framer Motion for:
- Page transitions
- Card hover effects
- Loading states
- Micro-interactions

## 📱 Marketing Site

Located in `/marketing-site`:
- Next.js 14
- Poppins font
- Modern landing page
- Responsive design
- Amber color scheme

Run with:
```bash
cd marketing-site
npm install
npm run dev
```

## 🔐 Environment Variables

Create `.env` in frontend root:

```env
VITE_API_URL=http://localhost:8000/api
```

## 🛠️ Development Workflow

1. Start Django backend: `python manage.py runserver`
2. Start frontend: `cd frontend && npm run dev`
3. Start marketing site: `cd marketing-site && npm run dev`

Access:
- App: http://localhost:3000
- API: http://localhost:8000
- Marketing: http://localhost:3001

## 📝 Code Standards

- TypeScript for type safety
- ESLint for code quality
- Prettier for formatting
- Tailwind for styling
- Functional components with hooks
- Context for global state

## 🚀 Deployment

### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder to CDN or static hosting
```

### Marketing Site
```bash
cd marketing-site
npm run build
# Deploy .next/ folder to Vercel or similar
```

## 📦 Dependencies

### Core
- React 18.2
- TypeScript 5.2
- Vite 5.0

### Routing & State
- React Router DOM 6.20
- TanStack React Query 5.13

### UI & Styling
- Tailwind CSS 3.3
- Radix UI
- Lucide React (icons)
- Framer Motion

### Utilities
- Axios
- date-fns
- clsx / tailwind-merge

## 🎯 Next Steps

1. Complete all page implementations
2. Add more UI components as needed
3. Implement real-time features (WebSockets)
4. Add unit tests
5. Performance optimization
6. SEO optimization for marketing site

## 📞 Support

For issues or questions, refer to the main project README or API documentation.
