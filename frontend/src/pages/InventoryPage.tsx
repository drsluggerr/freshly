import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, Filter, Camera, Barcode, Edit as EditIcon } from 'lucide-react'
import { inventoryAPI } from '@/services/api'
import { Card, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { FloatingActionButton } from '@/components/ui/FloatingActionButton'
import { formatDate, getExpirationStatus, getCategoryColor } from '@/utils/format'
import toast from 'react-hot-toast'

export const InventoryPage: React.FC = () => {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('')

  const { data: items, isLoading } = useQuery({
    queryKey: ['inventory', search, categoryFilter],
    queryFn: () => inventoryAPI.getAll({
      search: search || undefined,
      category: categoryFilter || undefined
    })
  })

  const deleteMutation = useMutation({
    mutationFn: inventoryAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
      toast.success('Item deleted')
    }
  })

  const wasteMutation = useMutation({
    mutationFn: ({ id, reason }: { id: number; reason: string }) =>
      inventoryAPI.markAsWasted(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
      toast.success('Item marked as wasted')
    }
  })

  const fabActions = [
    {
      icon: <Camera size={20} />,
      label: 'Scan Receipt',
      onClick: () => {
        // Navigate to receipt upload
        window.location.href = '/receipts'
      }
    },
    {
      icon: <Barcode size={20} />,
      label: 'Scan Barcode',
      onClick: () => {
        toast('Barcode scanner coming soon!', { icon: '📱' })
      }
    },
    {
      icon: <EditIcon size={20} />,
      label: 'Add Manually',
      onClick: () => {
        toast('Manual entry coming soon!', { icon: '✏️' })
      }
    }
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 pb-24">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Inventory</h1>
        <p className="text-gray-600 mt-1">Manage your pantry and fridge items</p>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search items..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="">All Categories</option>
          <option value="produce">Produce</option>
          <option value="dairy">Dairy</option>
          <option value="meat">Meat</option>
          <option value="seafood">Seafood</option>
          <option value="bakery">Bakery</option>
          <option value="frozen">Frozen</option>
          <option value="canned">Canned</option>
          <option value="dry_goods">Dry Goods</option>
          <option value="beverages">Beverages</option>
          <option value="snacks">Snacks</option>
          <option value="condiments">Condiments</option>
          <option value="spices">Spices</option>
        </select>
      </div>

      {/* Items Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Loading...</p>
        </div>
      ) : !items || items.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No items found</p>
          <Button onClick={() => window.location.href = '/receipts'}>
            Add Items
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((item) => {
            const expStatus = getExpirationStatus(item.expiration_date || null)

            return (
              <Card key={item.id}>
                <CardBody>
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 text-lg">{item.name}</h3>
                      {item.brand && (
                        <p className="text-sm text-gray-500">{item.brand}</p>
                      )}
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${getCategoryColor(item.category)}`}>
                      {item.category}
                    </span>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Quantity:</span>
                      <span className="font-medium">{item.quantity} {item.unit}</span>
                    </div>

                    {item.expiration_date && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Expires:</span>
                        <span className={`font-medium ${expStatus.color}`}>
                          {formatDate(item.expiration_date)}
                        </span>
                      </div>
                    )}

                    {item.price && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Price:</span>
                        <span className="font-medium">${item.price.toFixed(2)}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      className="flex-1"
                      onClick={() => {
                        const reason = prompt('Why are you discarding this item?')
                        if (reason) {
                          wasteMutation.mutate({ id: item.id, reason })
                        }
                      }}
                    >
                      Mark Wasted
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => {
                        if (confirm('Delete this item?')) {
                          deleteMutation.mutate(item.id)
                        }
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                </CardBody>
              </Card>
            )
          })}
        </div>
      )}

      <FloatingActionButton actions={fabActions} />
    </div>
  )
}
