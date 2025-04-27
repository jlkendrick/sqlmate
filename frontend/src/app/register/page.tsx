"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import Link from "next/link";
import { Header } from "@/components/header";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form.username, form.password, form.email);
      router.push("/login");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
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
          <h2 className="text-xl font-semibold text-center">Create Account</h2>
          {error && <p className="text-sm text-destructive">{error}</p>}
          {["username", "email", "password"].map((field) => (
            <div key={field}>
              <label className="block text-sm capitalize">{field}</label>
              <input
                name={field}
                type={field === "password" ? "password" : "text"}
                value={
                  field === "username"
                    ? form.username
                    : field === "email"
                    ? form.email
                    : form.password
                }
                onChange={onChange}
                required
                className={cn(
                  "w-full mt-1 p-2 border rounded",
                  "focus:outline-none focus:ring focus:ring-primary/50"
                )}
              />
            </div>
          ))}
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Registering…" : "Register"}
          </Button>
          <div className="text-center text-sm">
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:underline">
              Sign In
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
