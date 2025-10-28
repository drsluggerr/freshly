import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Sparkles, Calendar, ChefHat, Clock, TrendingUp, Plus } from 'lucide-react'
import { mealAPI } from '@/services/api'
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import toast from 'react-hot-toast'
import type { MealSuggestion } from '@/types'

export const MealsPage: React.FC = () => {
  const queryClient = useQueryClient()
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false)
  const [suggestions, setSuggestions] = useState<MealSuggestion[]>([])
  const [dietaryPreferences, setDietaryPreferences] = useState<string[]>([])

  const getSuggestionsMutation = useMutation({
    mutationFn: () => mealAPI.getSuggestions(dietaryPreferences.length > 0 ? dietaryPreferences : undefined),
    onSuccess: (data) => {
      setSuggestions(data.suggestions)
      toast.success(`Got ${data.suggestions.length} meal ideas!`)
      setIsLoadingSuggestions(false)
    },
    onError: () => {
      toast.error('Failed to get meal suggestions')
      setIsLoadingSuggestions(false)
    }
  })

  const handleGetSuggestions = () => {
    setIsLoadingSuggestions(true)
    getSuggestionsMutation.mutate()
  }

  const toggleDietaryPref = (pref: string) => {
    setDietaryPreferences(prev =>
      prev.includes(pref)
        ? prev.filter(p => p !== pref)
        : [...prev, pref]
    )
  }

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      easy: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      hard: 'bg-red-100 text-red-800'
    }
    return colors[difficulty as keyof typeof colors] || colors.medium
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Meal Planning</h1>
        <p className="text-gray-600 mt-1">Get AI-powered meal suggestions from your inventory</p>
      </div>

      {/* AI Suggestions Section */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">AI Meal Suggestions</h2>
              <p className="text-sm text-gray-600">
                Get personalized recipe ideas based on what you have
              </p>
            </div>
          </div>
        </CardHeader>

        <CardBody>
          {/* Dietary Preferences */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Dietary Preferences (Optional)
            </label>
            <div className="flex flex-wrap gap-2">
              {['Vegan', 'Vegetarian', 'Gluten-Free', 'Dairy-Free', 'Low-Carb', 'Keto'].map(
                (pref) => (
                  <button
                    key={pref}
                    onClick={() => toggleDietaryPref(pref.toLowerCase())}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      dietaryPreferences.includes(pref.toLowerCase())
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {pref}
                  </button>
                )
              )}
            </div>
          </div>

          <Button
            variant="primary"
            size="lg"
            onClick={handleGetSuggestions}
            isLoading={isLoadingSuggestions}
            className="w-full"
          >
            <Sparkles className="mr-2" size={20} />
            {isLoadingSuggestions ? 'Getting Suggestions...' : 'Get AI Meal Ideas'}
          </Button>

          {suggestions.length > 0 && (
            <div className="mt-6">
              <h3 className="font-bold text-gray-900 mb-4">Suggested Meals:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {suggestions.map((meal, index) => (
                  <Card key={index} className="hover:shadow-md transition-shadow">
                    <CardBody>
                      <div className="flex items-start justify-between mb-3">
                        <h4 className="font-bold text-gray-900 text-lg">{meal.name}</h4>
                        <span
                          className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(
                            meal.difficulty
                          )}`}
                        >
                          {meal.difficulty}
                        </span>
                      </div>

                      <p className="text-gray-600 text-sm mb-4">{meal.description}</p>

                      <div className="space-y-3">
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase mb-1">
                            Using from your inventory:
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {meal.ingredients_from_inventory.map((ing, i) => (
                              <span
                                key={i}
                                className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full"
                              >
                                {ing}
                              </span>
                            ))}
                          </div>
                        </div>

                        {meal.additional_ingredients &&
                          meal.additional_ingredients.length > 0 && (
                            <div>
                              <p className="text-xs font-medium text-gray-500 uppercase mb-1">
                                Need to buy:
                              </p>
                              <div className="flex flex-wrap gap-1">
                                {meal.additional_ingredients.map((ing, i) => (
                                  <span
                                    key={i}
                                    className="text-xs px-2 py-1 bg-orange-100 text-orange-800 rounded-full"
                                  >
                                    {ing}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                        <div className="flex items-center gap-4 text-sm text-gray-600 pt-2">
                          <div className="flex items-center gap-1">
                            <Clock size={14} />
                            <span>{meal.prep_time} min</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <ChefHat size={14} />
                            <span>{meal.difficulty}</span>
                          </div>
                        </div>
                      </div>
                    </CardBody>

                    <CardFooter>
                      <Button variant="primary" size="sm" className="w-full">
                        <Plus size={16} className="mr-1" />
                        Add to Meal Plan
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Weekly Meal Plan */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Calendar className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-bold text-gray-900">This Week's Meal Plan</h2>
                <p className="text-sm text-gray-600">Plan your meals for the week</p>
              </div>
            </div>
            <Button variant="secondary" size="sm">
              <Plus size={16} className="mr-1" />
              Add Meal
            </Button>
          </div>
        </CardHeader>

        <CardBody>
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              No meals planned yet
            </h3>
            <p className="text-gray-600 mb-4">
              Get AI suggestions above or add meals manually
            </p>
            <Button variant="primary">
              Plan Your Week
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <Card>
          <CardBody className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <ChefHat className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Meals This Week</p>
              <p className="text-2xl font-bold text-gray-900">0</p>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="flex items-center gap-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Ingredients Used</p>
              <p className="text-2xl font-bold text-gray-900">0%</p>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="flex items-center gap-4">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">AI Suggestions</p>
              <p className="text-2xl font-bold text-gray-900">{suggestions.length}</p>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
