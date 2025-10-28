import React, { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Upload, Camera, FileText, Check, X, Clock, AlertCircle } from 'lucide-react'
import { receiptAPI, inventoryAPI } from '@/services/api'
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { formatDate, formatCurrency } from '@/utils/format'
import toast from 'react-hot-toast'
import type { Receipt, ReceiptLineItem } from '@/types'

export const ReceiptsPage: React.FC = () => {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null)
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set())
  const [isUploading, setIsUploading] = useState(false)

  const { data: receipts, isLoading } = useQuery({
    queryKey: ['receipts'],
    queryFn: receiptAPI.getAll
  })

  const uploadMutation = useMutation({
    mutationFn: receiptAPI.upload,
    onSuccess: async (data) => {
      toast.success('Receipt uploaded! Processing...')

      // Poll for processing completion
      let attempts = 0
      const pollInterval = setInterval(async () => {
        attempts++
        try {
          const receipt = await receiptAPI.getById(data.receipt_id)

          if (receipt.processing_status === 'completed') {
            clearInterval(pollInterval)
            queryClient.invalidateQueries({ queryKey: ['receipts'] })
            setSelectedReceipt(receipt)
            toast.success(`Found ${receipt.line_items.length} items!`)
          } else if (receipt.processing_status === 'failed' || attempts > 20) {
            clearInterval(pollInterval)
            toast.error('Receipt processing failed')
          }
        } catch (error) {
          clearInterval(pollInterval)
        }
      }, 2000)

      setIsUploading(false)
    },
    onError: () => {
      toast.error('Failed to upload receipt')
      setIsUploading(false)
    }
  })

  const confirmMutation = useMutation({
    mutationFn: ({ receiptId, items }: { receiptId: number; items: number[] }) =>
      receiptAPI.confirm(receiptId, items),
    onSuccess: () => {
      toast.success('Items added to inventory!')
      queryClient.invalidateQueries({ queryKey: ['receipts'] })
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
      setSelectedReceipt(null)
      setSelectedItems(new Set())
    }
  })

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file')
      return
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB')
      return
    }

    setIsUploading(true)
    uploadMutation.mutate(file)
  }

  const handleItemToggle = (itemId: number) => {
    const newSelected = new Set(selectedItems)
    if (newSelected.has(itemId)) {
      newSelected.delete(itemId)
    } else {
      newSelected.add(itemId)
    }
    setSelectedItems(newSelected)
  }

  const handleConfirm = () => {
    if (selectedReceipt && selectedItems.size > 0) {
      confirmMutation.mutate({
        receiptId: selectedReceipt.id,
        items: Array.from(selectedItems)
      })
    }
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: { color: 'bg-gray-100 text-gray-800', icon: <Clock size={14} /> },
      processing: { color: 'bg-blue-100 text-blue-800', icon: <Clock size={14} /> },
      completed: { color: 'bg-green-100 text-green-800', icon: <Check size={14} /> },
      failed: { color: 'bg-red-100 text-red-800', icon: <AlertCircle size={14} /> }
    }
    const badge = badges[status as keyof typeof badges] || badges.pending

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        {badge.icon}
        {status}
      </span>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Receipts</h1>
        <p className="text-gray-600 mt-1">Scan receipts to auto-add items to inventory</p>
      </div>

      {/* Upload Section */}
      <Card className="mb-8">
        <CardBody className="text-center py-12">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Camera className="w-10 h-10 text-primary-600" />
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Receipt</h2>
            <p className="text-gray-600 mb-6">
              Take a photo of your receipt or upload an image
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button
                variant="primary"
                size="lg"
                onClick={() => fileInputRef.current?.click()}
                isLoading={isUploading}
                className="min-w-[200px]"
              >
                <Upload className="mr-2" size={20} />
                {isUploading ? 'Processing...' : 'Upload Receipt'}
              </Button>

              <Button
                variant="secondary"
                size="lg"
                onClick={() => {
                  if (fileInputRef.current) {
                    fileInputRef.current.setAttribute('capture', 'environment')
                    fileInputRef.current.click()
                  }
                }}
                className="min-w-[200px]"
              >
                <Camera className="mr-2" size={20} />
                Take Photo
              </Button>
            </div>

            <p className="text-xs text-gray-500 mt-4">
              Supports: JPG, PNG, PDF • Max size: 10MB
            </p>
          </div>
        </CardBody>
      </Card>

      {/* Item Confirmation Modal */}
      {selectedReceipt && (
        <Card className="mb-8 border-2 border-primary-500">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  Confirm Items from {selectedReceipt.merchant_name || 'Receipt'}
                </h3>
                <p className="text-sm text-gray-600">
                  {selectedReceipt.purchase_date && formatDate(selectedReceipt.purchase_date)} •{' '}
                  {formatCurrency(selectedReceipt.total_amount || 0)}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSelectedReceipt(null)
                  setSelectedItems(new Set())
                }}
              >
                <X size={20} />
              </Button>
            </div>
          </CardHeader>

          <CardBody>
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                Select items to add to inventory ({selectedItems.size} selected)
              </p>
            </div>

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {selectedReceipt.line_items.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleItemToggle(item.id)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedItems.has(item.id)
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                            selectedItems.has(item.id)
                              ? 'bg-primary-600 border-primary-600'
                              : 'border-gray-300'
                          }`}
                        >
                          {selectedItems.has(item.id) && (
                            <Check size={14} className="text-white" />
                          )}
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">{item.description}</h4>
                          <p className="text-sm text-gray-600">
                            Qty: {item.quantity} • {formatCurrency(item.total_price || 0)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>

          <CardFooter>
            <div className="flex gap-3 w-full">
              <Button
                variant="secondary"
                className="flex-1"
                onClick={() => {
                  // Select all
                  const allIds = new Set(selectedReceipt.line_items.map(i => i.id))
                  setSelectedItems(allIds)
                }}
              >
                Select All
              </Button>
              <Button
                variant="primary"
                className="flex-1"
                onClick={handleConfirm}
                disabled={selectedItems.size === 0}
                isLoading={confirmMutation.isPending}
              >
                Add {selectedItems.size} Items to Inventory
              </Button>
            </div>
          </CardFooter>
        </Card>
      )}

      {/* Receipt History */}
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900">Receipt History</h2>
        <p className="text-sm text-gray-600">View and manage your uploaded receipts</p>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Loading receipts...</p>
        </div>
      ) : !receipts || receipts.length === 0 ? (
        <Card>
          <CardBody className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No receipts uploaded yet</p>
            <p className="text-sm text-gray-400 mt-1">
              Upload your first receipt to get started!
            </p>
          </CardBody>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {receipts.map((receipt) => (
            <Card key={receipt.id} className="hover:shadow-md transition-shadow">
              <CardBody>
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900">
                      {receipt.merchant_name || 'Unknown Store'}
                    </h3>
                    {receipt.purchase_date && (
                      <p className="text-sm text-gray-600">
                        {formatDate(receipt.purchase_date)}
                      </p>
                    )}
                  </div>
                  {getStatusBadge(receipt.processing_status)}
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total:</span>
                    <span className="font-medium">
                      {formatCurrency(receipt.total_amount || 0)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Items:</span>
                    <span className="font-medium">{receipt.line_items?.length || 0}</span>
                  </div>
                  {receipt.is_duplicate && (
                    <div className="flex items-center gap-1 text-sm text-orange-600">
                      <AlertCircle size={14} />
                      <span>Possible duplicate</span>
                    </div>
                  )}
                  {receipt.items_added && (
                    <div className="flex items-center gap-1 text-sm text-green-600">
                      <Check size={14} />
                      <span>Items added to inventory</span>
                    </div>
                  )}
                </div>

                {receipt.processing_status === 'completed' && !receipt.items_added && (
                  <Button
                    variant="primary"
                    size="sm"
                    className="w-full"
                    onClick={() => {
                      setSelectedReceipt(receipt)
                      setSelectedItems(new Set(receipt.line_items.map(i => i.id)))
                    }}
                  >
                    Review & Add Items
                  </Button>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
