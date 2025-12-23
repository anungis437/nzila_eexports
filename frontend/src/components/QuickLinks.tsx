import { Link } from 'react-router-dom'
import { 
  Users, 
  Activity, 
  FileText, 
  FileCheck,
  Plus,
  BarChart3,
  DollarSign,
  Package,
  UserPlus,
  GitBranch,
  TrendingUp,
  UsersRound,
  Car,
  ShoppingBag,
  MapPin,
  MessageSquare,
  LucideIcon
} from 'lucide-react'

interface QuickLink {
  title: string
  description: string
  icon: LucideIcon
  path: string
  color: string
}

interface QuickLinksProps {
  userRole: 'admin' | 'dealer' | 'broker' | 'buyer'
}

const roleLinks: Record<string, QuickLink[]> = {
  admin: [
    {
      title: 'User Management',
      description: 'Manage users and permissions',
      icon: Users,
      path: '/users',
      color: 'from-blue-500 to-blue-600'
    },
    {
      title: 'System Health',
      description: 'Monitor performance and uptime',
      icon: Activity,
      path: '/system-health',
      color: 'from-green-500 to-green-600'
    },
    {
      title: 'Reports',
      description: 'View platform analytics',
      icon: FileText,
      path: '/reports',
      color: 'from-purple-500 to-purple-600'
    },
    {
      title: 'Documents',
      description: 'Manage compliance docs',
      icon: FileCheck,
      path: '/documents',
      color: 'from-orange-500 to-orange-600'
    }
  ],
  dealer: [
    {
      title: 'Add Vehicle',
      description: 'List a new vehicle for sale',
      icon: Plus,
      path: '/vehicles/new',
      color: 'from-blue-500 to-blue-600'
    },
    {
      title: 'Inventory Analytics',
      description: 'Track vehicle performance',
      icon: BarChart3,
      path: '/inventory-analytics',
      color: 'from-green-500 to-green-600'
    },
    {
      title: 'Commissions',
      description: 'View earnings and payouts',
      icon: DollarSign,
      path: '/commissions',
      color: 'from-purple-500 to-purple-600'
    },
    {
      title: 'Shipments',
      description: 'Manage logistics and tracking',
      icon: Package,
      path: '/shipments',
      color: 'from-orange-500 to-orange-600'
    }
  ],
  broker: [
    {
      title: 'Create Lead',
      description: 'Add new buyer lead',
      icon: UserPlus,
      path: '/leads/new',
      color: 'from-blue-500 to-blue-600'
    },
    {
      title: 'Pipeline',
      description: 'Manage your sales funnel',
      icon: GitBranch,
      path: '/leads',
      color: 'from-green-500 to-green-600'
    },
    {
      title: 'Performance',
      description: 'Track tier and earnings',
      icon: TrendingUp,
      path: '/broker-analytics',
      color: 'from-purple-500 to-purple-600'
    },
    {
      title: 'Buyers',
      description: 'Manage buyer relationships',
      icon: UsersRound,
      path: '/buyers',
      color: 'from-orange-500 to-orange-600'
    }
  ],
  buyer: [
    {
      title: 'Browse Vehicles',
      description: 'Search our inventory',
      icon: Car,
      path: '/vehicles',
      color: 'from-blue-500 to-blue-600'
    },
    {
      title: 'My Orders',
      description: 'View purchase history',
      icon: ShoppingBag,
      path: '/deals',
      color: 'from-green-500 to-green-600'
    },
    {
      title: 'Track Shipment',
      description: 'Monitor delivery status',
      icon: MapPin,
      path: '/shipments',
      color: 'from-purple-500 to-purple-600'
    },
    {
      title: 'Messages',
      description: 'Chat with dealers',
      icon: MessageSquare,
      path: '/messages',
      color: 'from-orange-500 to-orange-600'
    }
  ]
}

export default function QuickLinks({ userRole }: QuickLinksProps) {
  const links = roleLinks[userRole] || []

  return (
    <div className="mt-8">
      <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {links.map((link) => {
          const Icon = link.icon
          return (
            <Link
              key={link.path}
              to={link.path}
              className="group relative overflow-hidden rounded-xl bg-white border border-slate-200 p-5 hover:shadow-lg hover:border-slate-300 transition-all duration-200"
            >
              {/* Gradient background on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${link.color} opacity-0 group-hover:opacity-5 transition-opacity duration-200`} />
              
              <div className="relative">
                {/* Icon */}
                <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-br ${link.color} mb-3 shadow-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>

                {/* Title */}
                <h3 className="font-semibold text-slate-900 mb-1 group-hover:text-primary-600 transition-colors">
                  {link.title}
                </h3>

                {/* Description */}
                <p className="text-sm text-slate-500">
                  {link.description}
                </p>
              </div>

              {/* Arrow indicator */}
              <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transform translate-x-2 group-hover:translate-x-0 transition-all duration-200">
                <svg className="w-5 h-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
