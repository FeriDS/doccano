import { APIPerspectiveRepository } from '~/repositories/perspectives/apiPerspectiveRepository'

interface MiddlewareContext {
  route: {
    path: string
    params: {
      id: string
    }
    query: {
      [key: string]: any
    }
  }
  redirect: (path: string) => void
  $services: any
}

export default async function checkPerspective({ route, redirect }: MiddlewareContext) {
  // Check if this is an annotation route (any of the annotation pages)
  const annotationRoutes = [
    'text-classification',
    'sequence-labeling', 
    'sequence-to-sequence',
    'intent-detection-and-slot-filling',
    'image-classification',
    'image-captioning',
    'object-detection',
    'segmentation',
    'speech-to-text'
  ]
  
  const isAnnotationRoute = annotationRoutes.some(route_name => 
    route.path.includes(`/projects/`) && route.path.includes(`/${route_name}`)
  )
  
  if (!isAnnotationRoute) {
    return
  }

  const projectId = route.params.id
  const perspectiveRepository = new APIPerspectiveRepository()

  try {
    // Check if project has a perspective configured
    const projectPerspective = await perspectiveRepository.getProjectPerspective(projectId)
    if (!projectPerspective) {
      return // No perspective configured for this project
    }

    // Check if user has filled their perspective
    const userAnswer = await perspectiveRepository.getUserPerspectiveAnswer(projectId)
    if (!userAnswer || !userAnswer.is_complete) {
      // Redirect to perspectives page with flag indicating this was a redirect
      console.log('Redirecting to perspectives from:', route.path, 'user answer:', userAnswer)
      const redirectUrl = `/projects/${projectId}/perspectives?redirected=true`
      console.log('Redirect URL:', redirectUrl)
      redirect(redirectUrl)
    }
  } catch (error) {
    console.error('Error checking perspective:', error)
    // Allow access in case of error to avoid blocking users
  }
} 