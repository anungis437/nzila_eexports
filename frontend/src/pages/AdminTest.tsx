import { useAuth } from '../contexts/AuthContext'

export default function AdminTest() {
  const { user, isAdmin, isSuperuser, isStaff, isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white shadow-lg rounded-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            Admin Access Test
          </h1>

          <div className="space-y-4">
            <div className="border-b pb-4">
              <h2 className="text-xl font-semibold mb-3">Authentication Status</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center">
                  <span className="font-medium mr-2">Authenticated:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    isAuthenticated ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {isAuthenticated ? '✓ Yes' : '✗ No'}
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="font-medium mr-2">Admin:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    isAdmin ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {isAdmin ? '✓ Yes' : '✗ No'}
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="font-medium mr-2">Superuser:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    isSuperuser ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {isSuperuser ? '✓ Yes' : '✗ No'}
                  </span>
                </div>
                <div className="flex items-center">
                  <span className="font-medium mr-2">Staff:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    isStaff ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {isStaff ? '✓ Yes' : '✗ No'}
                  </span>
                </div>
              </div>
            </div>

            {user && (
              <div className="border-b pb-4">
                <h2 className="text-xl font-semibold mb-3">User Information</h2>
                <div className="space-y-2">
                  <div className="flex">
                    <span className="font-medium w-40">ID:</span>
                    <span className="text-gray-700">{user.id}</span>
                  </div>
                  <div className="flex">
                    <span className="font-medium w-40">Email:</span>
                    <span className="text-gray-700">{user.email}</span>
                  </div>
                  <div className="flex">
                    <span className="font-medium w-40">Username:</span>
                    <span className="text-gray-700">{user.username}</span>
                  </div>
                  <div className="flex">
                    <span className="font-medium w-40">Full Name:</span>
                    <span className="text-gray-700">{user.full_name || 'N/A'}</span>
                  </div>
                  <div className="flex">
                    <span className="font-medium w-40">Role:</span>
                    <span className="text-gray-700 capitalize">{user.role}</span>
                  </div>
                  <div className="flex">
                    <span className="font-medium w-40">Company:</span>
                    <span className="text-gray-700">{user.company_name || 'N/A'}</span>
                  </div>
                </div>
              </div>
            )}

            <div className="mt-6">
              <h2 className="text-xl font-semibold mb-3">Raw User Object</h2>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-auto text-sm">
                {JSON.stringify(user, null, 2)}
              </pre>
            </div>

            {isSuperuser && (
              <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">
                  🎉 Superuser Access Confirmed!
                </h3>
                <p className="text-blue-700">
                  You have full superuser access to the platform. You can access all admin features and settings.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
