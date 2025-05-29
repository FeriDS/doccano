import Vue from 'vue'

Vue.filter('truncate', (value: string, length: number) => {
  if (!value) return ''
  if (value.length <= length) return value
  return value.substring(0, length) + '...'
}) 