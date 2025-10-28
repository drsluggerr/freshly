import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, ShoppingCart, Check, X, Trash2 } from 'lucide-react'
import { shoppingAPI } from '@/services/api'
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import toast from 'react-hot-toast'

export const ShoppingPage: React.FC = () => {
  const queryClient = useQueryClient()
  const [showNewList, setShowNewList] = useState(false)
  const [newListName, setNewListName] = useState('')
  const [newListStore, setNewListStore] = useState('')
  const [activeListId, setActiveListId] = useState<number | null>(null)
  const [newItemName, setNewItemName] = useState('')
  const [newItemQuantity, setNewItemQuantity] = useState('1')

  const { data: lists } = useQuery({
    queryKey: ['shopping', 'active'],
    queryFn: () => shoppingAPI.getLists('active')
  })

  const createListMutation = useMutation({
    mutationFn: ({ name, store }: { name: string; store?: string }) =>
      shoppingAPI.createList(name, store),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['shopping'] })
      setShowNewList(false)
      setNewListName('')
      setNewListStore('')
      setActiveListId(data.id)
      toast.success('Shopping list created!')
    }
  })

  const addItemMutation = useMutation({
    mutationFn: ({ listId, name, quantity }: { listId: number; name: string; quantity: number }) =>
      shoppingAPI.addItem(listId, { name, quantity }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopping'] })
      setNewItemName('')
      setNewItemQuantity('1')
      toast.success('Item added!')
    }
  })

  const togglePurchasedMutation = useMutation({
    mutationFn: ({ listId, itemId, purchased }: { listId: number; itemId: number; purchased: boolean }) =>
      shoppingAPI.markPurchased(listId, itemId, purchased),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopping'] })
    }
  })

  const deleteItemMutation = useMutation({
    mutationFn: ({ listId, itemId }: { listId: number; itemId: number }) =>
      shoppingAPI.deleteItem(listId, itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopping'] })
      toast.success('Item removed')
    }
  })

  const handleCreateList = (e: React.FormEvent) => {
    e.preventDefault()
    if (newListName.trim()) {
      createListMutation.mutate({
        name: newListName,
        store: newListStore || undefined
      })
    }
  }

  const handleAddItem = (e: React.FormEvent, listId: number) => {
    e.preventDefault()
    if (newItemName.trim()) {
      addItemMutation.mutate({
        listId,
        name: newItemName,
        quantity: parseFloat(newItemQuantity) || 1
      })
    }
  }

  const activeList = lists?.find(list => list.id === activeListId)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Shopping Lists</h1>
        <p className="text-gray-600 mt-1">Manage your shopping lists and track purchases</p>
      </div>

      {/* Lists Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Sidebar - List Selection */}
        <div className="md:col-span-1">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-bold text-gray-900">My Lists</h2>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setShowNewList(true)}
            >
              <Plus size={16} className="mr-1" />
              New
            </Button>
          </div>

          {showNewList && (
            <Card className="mb-4 border-2 border-primary-500">
              <form onSubmit={handleCreateList}>
                <CardBody className="space-y-3">
                  <input
                    type="text"
                    placeholder="List name"
                    value={newListName}
                    onChange={(e) => setNewListName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    autoFocus
                  />
                  <input
                    type="text"
                    placeholder="Store (optional)"
                    value={newListStore}
                    onChange={(e) => setNewListStore(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <div className="flex gap-2">
                    <Button
                      type="submit"
                      variant="primary"
                      size="sm"
                      className="flex-1"
                      isLoading={createListMutation.isPending}
                    >
                      Create
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        setShowNewList(false)
                        setNewListName('')
                        setNewListStore('')
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </CardBody>
              </form>
            </Card>
          )}

          {!lists || lists.length === 0 ? (
            <Card>
              <CardBody className="text-center py-8">
                <ShoppingCart className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500 text-sm">No shopping lists yet</p>
              </CardBody>
            </Card>
          ) : (
            <div className="space-y-2">
              {lists.map((list) => {
                const totalItems = list.items?.length || 0
                const purchasedItems = list.items?.filter(i => i.is_purchased).length || 0

                return (
                  <Card
                    key={list.id}
                    className={`cursor-pointer transition-all ${
                      activeListId === list.id
                        ? 'border-2 border-primary-500 bg-primary-50'
                        : 'hover:shadow-md'
                    }`}
                    onClick={() => setActiveListId(list.id)}
                  >
                    <CardBody>
                      <h3 className="font-bold text-gray-900">{list.name}</h3>
                      {list.store && (
                        <p className="text-sm text-gray-600">{list.store}</p>
                      )}
                      <div className="flex items-center gap-2 mt-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all"
                            style={{
                              width: totalItems > 0
                                ? `${(purchasedItems / totalItems) * 100}%`
                                : '0%'
                            }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">
                          {purchasedItems}/{totalItems}
                        </span>
                      </div>
                    </CardBody>
                  </Card>
                )
              })}
            </div>
          )}
        </div>

        {/* Main - List Items */}
        <div className="md:col-span-2">
          {!activeList ? (
            <Card>
              <CardBody className="text-center py-16">
                <ShoppingCart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Select a Shopping List
                </h3>
                <p className="text-gray-600">
                  Choose a list from the sidebar or create a new one
                </p>
              </CardBody>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <h2 className="text-2xl font-bold text-gray-900">{activeList.name}</h2>
                {activeList.store && (
                  <p className="text-gray-600">{activeList.store}</p>
                )}
              </CardHeader>

              <CardBody>
                {/* Add Item Form */}
                <form
                  onSubmit={(e) => handleAddItem(e, activeList.id)}
                  className="mb-6 pb-6 border-b border-gray-200"
                >
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Add item..."
                      value={newItemName}
                      onChange={(e) => setNewItemName(e.target.value)}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <input
                      type="number"
                      placeholder="Qty"
                      value={newItemQuantity}
                      onChange={(e) => setNewItemQuantity(e.target.value)}
                      className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      min="0.1"
                      step="0.1"
                    />
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={addItemMutation.isPending}
                    >
                      <Plus size={20} />
                    </Button>
                  </div>
                </form>

                {/* Items List */}
                {!activeList.items || activeList.items.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No items in this list</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {activeList.items.map((item) => (
                      <div
                        key={item.id}
                        className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                          item.is_purchased
                            ? 'bg-gray-50 border-gray-200'
                            : 'bg-white border-gray-300'
                        }`}
                      >
                        <button
                          onClick={() =>
                            togglePurchasedMutation.mutate({
                              listId: activeList.id,
                              itemId: item.id,
                              purchased: !item.is_purchased
                            })
                          }
                          className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-all ${
                            item.is_purchased
                              ? 'bg-primary-600 border-primary-600'
                              : 'border-gray-300 hover:border-primary-500'
                          }`}
                        >
                          {item.is_purchased && <Check size={16} className="text-white" />}
                        </button>

                        <div className="flex-1">
                          <h4
                            className={`font-medium ${
                              item.is_purchased
                                ? 'line-through text-gray-500'
                                : 'text-gray-900'
                            }`}
                          >
                            {item.name}
                          </h4>
                          <p className="text-sm text-gray-600">
                            Qty: {item.quantity}
                            {item.estimated_price && ` • ~$${item.estimated_price.toFixed(2)}`}
                          </p>
                        </div>

                        <button
                          onClick={() =>
                            deleteItemMutation.mutate({
                              listId: activeList.id,
                              itemId: item.id
                            })
                          }
                          className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
