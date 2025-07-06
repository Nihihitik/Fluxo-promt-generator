const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface RegisterResponse {
  message: string;
  email_confirmed: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface EmailConfirmationRequest {
  email: string;
  code: string;
}

export interface EmailConfirmationResponse {
  message: string;
  email_confirmed: boolean;
}

export interface ResendConfirmationRequest {
  email: string;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export interface PasswordChangeResponse {
  message: string;
}

export interface User {
  id: number;
  email: string;
  name?: string;
  is_email_confirmed: boolean;
  daily_limit: number;
  requests_today: number;
  last_request_date?: string;
  created_at: string;
  updated_at: string;
}

export interface ApiError {
  message: string;
  detail?: string;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('An unexpected error occurred');
    }
  }

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async register(userData: RegisterRequest): Promise<RegisterResponse> {
    return this.request<RegisterResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async confirmEmail(data: EmailConfirmationRequest): Promise<EmailConfirmationResponse> {
    return this.request<EmailConfirmationResponse>('/auth/confirm-email', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async resendConfirmation(data: ResendConfirmationRequest): Promise<EmailConfirmationResponse> {
    return this.request<EmailConfirmationResponse>('/auth/resend-confirmation', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async changePassword(data: PasswordChangeRequest, token: string): Promise<PasswordChangeResponse> {
    return this.request<PasswordChangeResponse>('/auth/change-password', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
  }

  async getCurrentUser(token: string): Promise<User> {
    return this.request<User>('/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async createPrompt(
    originalPrompt: string,
    styleId: number,
    token: string
  ): Promise<any> {
    return this.request('/prompts/create', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        original_prompt: originalPrompt,
        style_id: styleId,
      }),
    });
  }

  async getPromptHistory(
    token: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<any[]> {
    return this.request(`/prompts/history?limit=${limit}&offset=${offset}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async getPromptStyles(token: string): Promise<any> {
    return this.request('/prompts/styles', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async getUserLimits(token: string): Promise<any> {
    return this.request('/prompts/limits', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async checkHealth(): Promise<{ status: string }> {
    return this.request('/health');
  }
}

export const apiClient = new ApiClient();