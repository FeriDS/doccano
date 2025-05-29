import Vue from 'vue'

export default Vue.extend({
  methods: {
    truncateText(value: string, length: number): string {
      if (!value) return ''
      if (value.length <= length) return value
      return value.substring(0, length) + '...'
    }
  }
}) 