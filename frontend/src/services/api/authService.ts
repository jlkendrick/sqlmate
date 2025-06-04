import { BaseApiClient } from "./baseClient";
import { StatusResponse } from "@/types/http";

interface RegisterRequest {
  username: string;
  password: string;
  email: string;
}

interface RegisterResponse {
  details: StatusResponse;
}

interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  details: StatusResponse;
  token: string | null;
}

interface UserInfoResponse {
  details: StatusResponse;
  username?: string;
  email?: string;
}

interface DeleteUserResponse {
  details: StatusResponse;
}

export class AuthApiService extends BaseApiClient {
  constructor() {
    super();
  }

  /**
   * Register a new user
   */
  async register(
    username: string,
    password: string,
    email: string
  ): Promise<RegisterResponse> {
    const data: RegisterRequest = { username, password, email };
    return await this.post<RegisterRequest, RegisterResponse>(
      "/auth/register",
      data,
      false
    );
  }

  /**
   * Log in a user and get auth token
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const data: LoginRequest = { username, password };
    return await this.post<LoginRequest, LoginResponse>(
      "/auth/login",
      data,
      false
    );
  }

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<UserInfoResponse> {
    return await this.get<UserInfoResponse>("/auth/me");
  }

  /**
   * Delete user account
   */
  async deleteUser(): Promise<DeleteUserResponse> {
    return await this.delete<DeleteUserResponse>("/auth/delete_user");
  }
}
