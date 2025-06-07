export default async function ({ _store, redirect, route, $axios }) {
  // Only check on annotation routes
  if (!route.path.includes('/projects/') || !route.path.includes('/annotation')) {
    return
  }

  const projectId = parseInt(route.params.id)
  
  try {
    const response = await $axios.$get(`/projects/${projectId}/perspective/check-completion`)
    
    if (!response.is_complete) {
      // Redirect to perspective form if not complete
      return redirect(`/projects/${projectId}/perspective`)
    }
  } catch (error) {
    // If there's an error (like no perspective configured), allow access
    console.warn('Error checking perspective completion:', error)
  }
} 