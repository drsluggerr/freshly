import { formatDistanceToNow, format, differenceInDays } from 'date-fns'

export function formatDate(date: string | Date): string {
  return format(new Date(date), 'MMM dd, yyyy')
}

export function formatDateTime(date: string | Date): string {
  return format(new Date(date), 'MMM dd, yyyy h:mm a')
}

export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency
  }).format(amount)
}

export function getExpirationStatus(expirationDate: string | null): {
  status: 'expired' | 'expiring-soon' | 'fresh' | 'unknown'
  daysLeft: number
  color: string
} {
  if (!expirationDate) {
    return { status: 'unknown', daysLeft: 0, color: 'text-gray-500' }
  }

  const days = differenceInDays(new Date(expirationDate), new Date())

  if (days < 0) {
    return { status: 'expired', daysLeft: days, color: 'text-red-600' }
  } else if (days <= 3) {
    return { status: 'expiring-soon', daysLeft: days, color: 'text-orange-600' }
  } else {
    return { status: 'fresh', daysLeft: days, color: 'text-green-600' }
  }
}

export function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    produce: 'bg-green-100 text-green-800',
    dairy: 'bg-blue-100 text-blue-800',
    meat: 'bg-red-100 text-red-800',
    seafood: 'bg-cyan-100 text-cyan-800',
    bakery: 'bg-amber-100 text-amber-800',
    frozen: 'bg-indigo-100 text-indigo-800',
    canned: 'bg-gray-100 text-gray-800',
    dry_goods: 'bg-yellow-100 text-yellow-800',
    beverages: 'bg-purple-100 text-purple-800',
    snacks: 'bg-pink-100 text-pink-800',
    condiments: 'bg-orange-100 text-orange-800',
    spices: 'bg-rose-100 text-rose-800',
    other: 'bg-slate-100 text-slate-800'
  }
  return colors[category] || colors.other
}
