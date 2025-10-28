import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, TrendingDown, DollarSign, Trash2, Package, AlertTriangle } from 'lucide-react'
import { analyticsAPI } from '@/services/api'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { formatCurrency } from '@/utils/format'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6']

export const AnalyticsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState(30)

  const { data: wasteStats } = useQuery({
    queryKey: ['analytics', 'waste', timeRange],
    queryFn: () => analyticsAPI.getWasteStats(timeRange)
  })

  const { data: spendingStats } = useQuery({
    queryKey: ['analytics', 'spending', timeRange],
    queryFn: () => analyticsAPI.getSpendingStats(timeRange)
  })

  const { data: inventorySummary } = useQuery({
    queryKey: ['analytics', 'summary'],
    queryFn: () => analyticsAPI.getInventorySummary()
  })

  const timeRanges = [
    { label: '7 Days', value: 7 },
    { label: '30 Days', value: 30 },
    { label: '90 Days', value: 90 }
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">Track your spending, waste, and inventory trends</p>
        </div>

        {/* Time Range Selector */}
        <div className="flex gap-2">
          {timeRanges.map((range) => (
            <button
              key={range.value}
              onClick={() => setTimeRange(range.value)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                timeRange === range.value
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardBody className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Items</p>
              <p className="text-2xl font-bold text-gray-900">
                {inventorySummary?.total_items || 0}
              </p>
              <p className="text-xs text-green-600 mt-1">Active inventory</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <Package className="w-6 h-6 text-blue-600" />
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Spent</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(spendingStats?.total_spent || 0)}
              </p>
              <p className="text-xs text-gray-600 mt-1">Last {timeRange} days</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Wasted Value</p>
              <p className="text-2xl font-bold text-red-600">
                {formatCurrency(wasteStats?.total_value_wasted || 0)}
              </p>
              <p className="text-xs text-gray-600 mt-1">
                {wasteStats?.total_wasted_items || 0} items
              </p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <Trash2 className="w-6 h-6 text-red-600" />
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
              <p className="text-xs text-gray-600 mt-1">Next 7 days</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-orange-600" />
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Spending Over Time */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-gray-900">Spending Trend</h2>
            <p className="text-sm text-gray-600">Daily spending over time</p>
          </CardHeader>
          <CardBody>
            {spendingStats?.spending_timeline && spendingStats.spending_timeline.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={spendingStats.spending_timeline}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis />
                  <Tooltip
                    formatter={(value: number) => formatCurrency(value)}
                    labelFormatter={(label) => new Date(label).toLocaleDateString()}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="total"
                    stroke="#10b981"
                    strokeWidth={2}
                    name="Spending"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center">
                <p className="text-gray-500">No spending data available</p>
              </div>
            )}
          </CardBody>
        </Card>

        {/* Spending by Category */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-gray-900">Spending by Category</h2>
            <p className="text-sm text-gray-600">Category breakdown</p>
          </CardHeader>
          <CardBody>
            {spendingStats?.spending_by_category && spendingStats.spending_by_category.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={spendingStats.spending_by_category}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ category, total }) => `${category}: ${formatCurrency(total)}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="total"
                  >
                    {spendingStats.spending_by_category.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center">
                <p className="text-gray-500">No category data available</p>
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Waste by Category */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-gray-900">Waste by Category</h2>
            <p className="text-sm text-gray-600">What categories waste the most</p>
          </CardHeader>
          <CardBody>
            {wasteStats?.waste_by_category && wasteStats.waste_by_category.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={wasteStats.waste_by_category}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  <Legend />
                  <Bar dataKey="total_value" fill="#ef4444" name="Value Wasted" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center">
                <p className="text-gray-500">No waste data yet - keep it up! 🎉</p>
              </div>
            )}
          </CardBody>
        </Card>

        {/* Most Wasted Items */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-gray-900">Most Wasted Items</h2>
            <p className="text-sm text-gray-600">Items you waste most often</p>
          </CardHeader>
          <CardBody>
            {wasteStats?.most_wasted_items && wasteStats.most_wasted_items.length > 0 ? (
              <div className="space-y-3">
                {wasteStats.most_wasted_items.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center text-red-600 font-bold">
                        {index + 1}
                      </div>
                      <span className="font-medium text-gray-900">{item.name}</span>
                    </div>
                    <span className="text-sm text-gray-600">{item.count} times</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-[300px] flex items-center justify-center">
                <p className="text-gray-500">No waste data available</p>
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Waste Reasons */}
      {wasteStats?.waste_reasons && wasteStats.waste_reasons.length > 0 && (
        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-gray-900">Why Food Gets Wasted</h2>
            <p className="text-sm text-gray-600">Common reasons for waste</p>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {wasteStats.waste_reasons.map((reason, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <p className="font-medium text-gray-900 mb-1">{reason.reason}</p>
                  <p className="text-2xl font-bold text-red-600">{reason.count}</p>
                  <p className="text-xs text-gray-600">times</p>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Insights & Recommendations */}
      <Card className="mt-6">
        <CardHeader>
          <h2 className="text-lg font-bold text-gray-900">💡 Insights & Recommendations</h2>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            {wasteStats && wasteStats.total_value_wasted > 0 && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="font-medium text-yellow-900 mb-1">
                  You've wasted {formatCurrency(wasteStats.total_value_wasted)} in the last {timeRange} days
                </p>
                <p className="text-sm text-yellow-800">
                  That's approximately {formatCurrency((wasteStats.total_value_wasted / timeRange) * 365)} per year!
                  Consider using the "Eat First" section on your dashboard.
                </p>
              </div>
            )}

            {inventorySummary && inventorySummary.expiring_soon > 0 && (
              <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <p className="font-medium text-orange-900 mb-1">
                  {inventorySummary.expiring_soon} items expiring soon
                </p>
                <p className="text-sm text-orange-800">
                  Check your dashboard's "Eat First" section to prioritize these items.
                </p>
              </div>
            )}

            {(!wasteStats || wasteStats.total_value_wasted === 0) && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="font-medium text-green-900 mb-1">
                  🎉 Great job! No waste recorded
                </p>
                <p className="text-sm text-green-800">
                  Keep up the good work! You're saving money and helping the environment.
                </p>
              </div>
            )}
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
