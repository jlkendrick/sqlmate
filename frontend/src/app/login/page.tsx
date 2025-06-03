"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Header } from "@/components/header";
import { authService } from "@/services/api";
import { toast } from "@/components/ui/use-toast";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { setToken, setUser } = useAuth();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await authService.login(form.username, form.password);
      const token = response.token!!;

      localStorage.setItem("token", token);
      setToken(token);
      
      const userInfo = await authService.getCurrentUser();
      setUser({
        username: userInfo.username!!,
        email: userInfo.email!!,
      });
      
      toast({
        title: "Login successful!",
        description: "Welcome back! Redirecting to the home screen.",
        variant: "default",
      });

      router.push("/");
      
    } catch (err: any) {
      console.error("Login error:", err);

      // Show error toast
      toast({
        title: "Login failed",
        description: err.message || "Please check your credentials.",
        variant: "destructive",
      });

      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <div className="flex-1 flex items-center justify-center py-10">
        <form
          onSubmit={onSubmit}
          className="max-w-sm mx-auto p-6 space-y-4 bg-card rounded shadow"
        >
          <h2 className="text-xl font-semibold text-center">Sign In</h2>
          {error && <p className="text-sm text-destructive">{error}</p>}
          {["username", "password"].map((field) => (
            <div key={field}>
              <label className="block text-sm capitalize">{field}</label>
              <input
                name={field}
                type={field === "password" ? "password" : "text"}
                value={field === "username" ? form.username : form.password}
                onChange={onChange}
                required
                className={cn(
                  "w-full mt-1 p-2 border rounded",
                  "focus:outline-none focus:ring focus:ring-primary/50"
                )}
              />
            </div>
          ))}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Signing In…" : "Sign In"}
          </Button>
          <div className="text-center text-sm">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="text-primary hover:underline">
              Register
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
