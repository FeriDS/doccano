this.instance.interceptors.response.use(
  response => response,
  error => {
    // Redireciona apenas em caso de erro de rede ou status 500, 502, 503, 504
    if (
      !error.response ||
      [500, 502, 503, 504].includes(error.response?.status)
    ) {
      window.location.href = '/?error=techissue'
    }
    return Promise.reject(error)
  }
) 