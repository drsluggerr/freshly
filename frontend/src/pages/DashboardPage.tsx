import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, Package, TrendingUp, Calendar } from 'lucide-react'
import { inventoryAPI, analyticsAPI } from '@/services/api'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { formatDate, getExpirationStatus, formatCurrency } from '@/utils/format'

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate()

  const { data: expiringItems } = useQuery({
    queryKey: ['inventory', 'expiring'],
    queryFn: () => inventoryAPI.getAll({ expiring_soon: true })
  })

  const { data: inventorySummary } = useQuery({
    queryKey: ['analytics', 'summary'],
    queryFn: () => analyticsAPI.getInventorySummary()
  })

  const { data: wasteStats } = useQuery({
    queryKey: ['analytics', 'waste', 7],
    queryFn: () => analyticsAPI.getWasteStats(7)
  })

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your pantry and fridge</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardBody className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Items</p>
              <p className="text-2xl font-bold text-gray-900">
                {inventorySummary?.total_items || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
              <Package className="w-6 h-6 text-primary-600" />
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Expiring Soon</p>
              <p className="text-2xl font-bold text-orange-600">
                {inventorySummary?.expiring_soon || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-orange-600" />
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Expired</p>
              <p className="text-2xl font-bold text-red-600">
                {inventorySummary?.expired || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Wasted (7d)</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(wasteStats?.total_value_wasted || 0)}
              </p>
            </div>
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-gray-600" />
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Eat First - Priority Items */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">🍽️ Eat First</h2>
              <p className="text-sm text-gray-600">Items expiring soon that need your attention</p>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => navigate('/inventory?filter=expiring')}
            >
              View All
            </Button>
          </div>
        </CardHeader>
        <CardBody>
          {!expiringItems || expiringItems.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No items expiring soon! 🎉</p>
            </div>
          ) : (
            <div className="space-y-3">
              {expiringItems.slice(0, 5).map((item) => {
                const expStatus = getExpirationStatus(item.expiration_date || null)

                return (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                    onClick={() => navigate(`/inventory/${item.id}`)}
                  >
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{item.name}</h3>
                      <p className="text-sm text-gray-600">
                        {item.quantity} {item.unit} • {item.brand || 'No brand'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-medium ${expStatus.color}`}>
                        {expStatus.daysLeft === 0
                          ? 'Expires today'
                          : expStatus.daysLeft < 0
                          ? 'Expired'
                          : `${expStatus.daysLeft}d left`}
                      </p>
                      {item.expiration_date && (
                        <p className="text-xs text-gray-500">
                          {formatDate(item.expiration_date)}
                        </p>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => navigate('/receipts')}>
          <CardBody className="text-center py-8">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">📸</span>
            </div>
            <h3 className="font-bold text-gray-900 mb-2">Scan Receipt</h3>
            <p className="text-sm text-gray-600">Upload a receipt to auto-add items</p>
          </CardBody>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => navigate('/meals')}>
          <CardBody className="text-center py-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🤖</span>
            </div>
            <h3 className="font-bold text-gray-900 mb-2">AI Meal Ideas</h3>
            <p className="text-sm text-gray-600">Get recipe suggestions from your inventory</p>
          </CardBody>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => navigate('/shopping')}>
          <CardBody className="text-center py-8">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🛒</span>
            </div>
            <h3 className="font-bold text-gray-900 mb-2">Shopping List</h3>
            <p className="text-sm text-gray-600">Create and manage shopping lists</p>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
