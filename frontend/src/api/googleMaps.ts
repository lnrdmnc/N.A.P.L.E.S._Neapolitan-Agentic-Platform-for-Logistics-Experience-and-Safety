// Loads the Google Maps JavaScript API once, with the browser key from /api/config.
// No key, or no network: the promise rejects and the map panel says so. No fallback data.

type Config = { maps_js_api_key: string | null }

let loading: Promise<typeof google.maps> | null = null

export async function fetchMapsKey(): Promise<string | null> {
  const response = await fetch('/api/config')
  if (!response.ok) return null
  const body = (await response.json()) as Config
  return body.maps_js_api_key
}

export function loadGoogleMaps(key: string): Promise<typeof google.maps> {
  if (loading) return loading
  loading = new Promise((resolve, reject) => {
    const callback = '__naplesMapsReady'
    ;(window as unknown as Record<string, () => void>)[callback] = () => resolve(google.maps)
    const script = document.createElement('script')
    const params = new URLSearchParams({
      key,
      libraries: 'geometry',
      language: 'it',
      region: 'IT',
      loading: 'async',
      callback,
    })
    script.src = `https://maps.googleapis.com/maps/api/js?${params}`
    script.async = true
    script.onerror = () => {
      loading = null
      reject(new Error('Google Maps non raggiungibile'))
    }
    document.head.appendChild(script)
  })
  return loading
}
