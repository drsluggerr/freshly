import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Camera, Barcode, Edit } from 'lucide-react'
import { cn } from '@/utils/cn'

interface FABAction {
  icon: React.ReactNode
  label: string
  onClick: () => void
  color?: string
}

interface FloatingActionButtonProps {
  actions: FABAction[]
}

export const FloatingActionButton: React.FC<FloatingActionButtonProps> = ({ actions }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="absolute bottom-16 right-0 flex flex-col gap-3 mb-2"
          >
            {actions.map((action, index) => (
              <motion.button
                key={index}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 50 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => {
                  action.onClick()
                  setIsOpen(false)
                }}
                className={cn(
                  'flex items-center gap-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-all px-4 py-3',
                  action.color || 'text-gray-700'
                )}
              >
                <span className="text-sm font-medium whitespace-nowrap">{action.label}</span>
                <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-white">
                  {action.icon}
                </div>
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 rounded-full bg-primary-600 text-white shadow-lg hover:shadow-xl transition-all flex items-center justify-center"
      >
        <motion.div
          animate={{ rotate: isOpen ? 45 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <Plus size={28} />
        </motion.div>
      </motion.button>
    </div>
  )
}
