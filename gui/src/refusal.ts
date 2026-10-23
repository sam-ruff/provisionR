interface ApiError {
  detail?: unknown
}

const REFUSED = 'This action is disabled on this read-only demo'

// Why a request was refused (the read-only demo, or a proxy in front of it), or null if it was not.
export async function refusalDetail(response: Response): Promise<string | null> {
  if (response.status !== 403) return null
  try {
    const body = (await response.json()) as ApiError
    return typeof body.detail === 'string' ? body.detail : REFUSED
  } catch {
    return REFUSED
  }
}
