import axios from 'axios'
import type {
  AuthTokens,
  LoginCredentials,
  RegisterData,
  User,
  InventoryItem,
  InventoryItemCreate,
  Receipt,
  MealSuggestion,
  ShoppingList,
  WasteStats,
  SpendingStats
} from '@/types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken
          })

          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth endpoints
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await api.post<AuthTokens>('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  register: async (data: RegisterData): Promise<User> => {
    const response = await api.post<User>('/auth/register', data)
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  }
}

// Inventory endpoints
export const inventoryAPI = {
  getAll: async (params?: {
    location_id?: number
    category?: string
    expiring_soon?: boolean
    search?: string
  }): Promise<InventoryItem[]> => {
    const response = await api.get<InventoryItem[]>('/inventory', { params })
    return response.data
  },

  getById: async (id: number): Promise<InventoryItem> => {
    const response = await api.get<InventoryItem>(`/inventory/${id}`)
    return response.data
  },

  create: async (data: InventoryItemCreate): Promise<InventoryItem> => {
    const response = await api.post<InventoryItem>('/inventory', data)
    return response.data
  },

  update: async (id: number, data: Partial<InventoryItemCreate>): Promise<InventoryItem> => {
    const response = await api.patch<InventoryItem>(`/inventory/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/inventory/${id}`)
  },

  usePartial: async (id: number, quantityUsed: number): Promise<InventoryItem> => {
    const response = await api.post<InventoryItem>(`/inventory/${id}/use`, {
      item_id: id,
      quantity_used: quantityUsed
    })
    return response.data
  },

  markAsWasted: async (id: number, reason: string): Promise<InventoryItem> => {
    const response = await api.post<InventoryItem>(`/inventory/${id}/waste`, {
      item_id: id,
      waste_reason: reason
    })
    return response.data
  },

  bulkAdd: async (items: InventoryItemCreate[]): Promise<InventoryItem[]> => {
    const response = await api.post<InventoryItem[]>('/inventory/bulk', { items })
    return response.data
  }
}

// Receipt endpoints
export const receiptAPI = {
  getAll: async (): Promise<Receipt[]> => {
    const response = await api.get<Receipt[]>('/receipts')
    return response.data
  },

  getById: async (id: number): Promise<Receipt> => {
    const response = await api.get<Receipt>(`/receipts/${id}`)
    return response.data
  },

  upload: async (file: File): Promise<{ receipt_id: number; status: string }> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/receipts/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  confirm: async (receiptId: number, confirmedItems: number[]): Promise<void> => {
    await api.post(`/receipts/${receiptId}/confirm`, {
      receipt_id: receiptId,
      confirmed_items: confirmedItems
    })
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/receipts/${id}`)
  }
}

// Meal endpoints
export const mealAPI = {
  getSuggestions: async (dietaryPreferences?: string[]): Promise<{ suggestions: MealSuggestion[] }> => {
    const response = await api.post('/meals/suggest', { dietary_preferences: dietaryPreferences })
    return response.data
  },

  getRecipes: async (params?: { search?: string; meal_type?: string }): Promise<any[]> => {
    const response = await api.get('/meals/recipes', { params })
    return response.data
  },

  getMealPlan: async (startDate?: string, endDate?: string): Promise<any[]> => {
    const response = await api.get('/meals/plan', {
      params: { start_date: startDate, end_date: endDate }
    })
    return response.data
  },

  createMealPlan: async (data: {
    recipe_id: number
    planned_date: string
    meal_type: string
    servings?: number
  }): Promise<any> => {
    const response = await api.post('/meals/plan', data)
    return response.data
  },

  deleteMealPlan: async (id: number): Promise<void> => {
    await api.delete(`/meals/plan/${id}`)
  }
}

// Shopping endpoints
export const shoppingAPI = {
  getLists: async (status?: string): Promise<ShoppingList[]> => {
    const response = await api.get<ShoppingList[]>('/shopping/lists', {
      params: { status }
    })
    return response.data
  },

  createList: async (name: string, store?: string): Promise<ShoppingList> => {
    const response = await api.post<ShoppingList>('/shopping/lists', { name, store })
    return response.data
  },

  addItem: async (listId: number, item: {
    name: string
    quantity?: number
    unit?: string
    category?: string
  }): Promise<any> => {
    const response = await api.post(`/shopping/lists/${listId}/items`, item)
    return response.data
  },

  markPurchased: async (listId: number, itemId: number, purchased: boolean): Promise<any> => {
    const response = await api.patch(`/shopping/lists/${listId}/items/${itemId}/purchase`, {
      purchased
    })
    return response.data
  },

  deleteItem: async (listId: number, itemId: number): Promise<void> => {
    await api.delete(`/shopping/lists/${listId}/items/${itemId}`)
  }
}

// Analytics endpoints
export const analyticsAPI = {
  getWasteStats: async (days: number = 30): Promise<WasteStats> => {
    const response = await api.get<WasteStats>('/analytics/waste-stats', {
      params: { days }
    })
    return response.data
  },

  getSpendingStats: async (days: number = 30): Promise<SpendingStats> => {
    const response = await api.get<SpendingStats>('/analytics/spending', {
      params: { days }
    })
    return response.data
  },

  getInventorySummary: async (): Promise<any> => {
    const response = await api.get('/analytics/inventory-summary')
    return response.data
  }
}

export default api
