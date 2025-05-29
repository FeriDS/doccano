export function truncateText(value: string, length: number): string {
  if (!value) return ''
  if (value.length <= length) return value
  return value.substring(0, length) + '...'
} 