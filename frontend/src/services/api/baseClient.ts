// Base API client with common functionality
export class BaseApiClient {
  protected baseUrl: string;

  constructor(baseUrl: string = "") {
    this.baseUrl = baseUrl;
  }

  // Get auth headers for protected endpoints
  protected getAuthHeaders() {
    const token = localStorage.getItem("token");
    const headers: Record<string, string> = {
      "Content-Type": "application/json"
    };
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    
    return headers;
  }

  // Common GET request method
  protected async get<T>(
    endpoint: string,
    requiresAuth: boolean = true
  ): Promise<T> {
    const headers = requiresAuth
      ? this.getAuthHeaders()
      : { "Content-Type": "application/json" };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: "GET",
      headers,
      credentials: "include",
    });

    return this.handleResponse<T>(response);
  }

  // Common POST request method
  protected async post<T, U>(
    endpoint: string,
    data: T,
    requiresAuth: boolean = true
  ): Promise<U> {
    const headers = requiresAuth
      ? this.getAuthHeaders()
      : { "Content-Type": "application/json" };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: "POST",
      headers,
      credentials: "include",
      body: JSON.stringify(data),
    });

    return this.handleResponse<U>(response);
  }

  // Common DELETE request method
  protected async delete<T>(
    endpoint: string,
    requiresAuth: boolean = true
  ): Promise<T> {
    const headers = requiresAuth
      ? this.getAuthHeaders()
      : { "Content-Type": "application/json" };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: "DELETE",
      headers,
      credentials: "include",
    });

    return this.handleResponse<T>(response);
  }

  // Common response handler with proper error handling
  protected async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      if (!errorData || !errorData.details || !errorData.details.message) {
        throw new Error("Unknown error"); // Unknown error
      } else {
        // If errorData has a details field, use it
        throw new Error(errorData.details.message);
      }
    }

    return response.json();
  }
}
