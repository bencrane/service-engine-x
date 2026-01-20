"use client";

import { useActionState } from "react";
import { login } from "./actions";

export default function LoginPage() {
  const [state, formAction, pending] = useActionState(login, null);

  return (
    <main className="min-h-screen bg-background text-foreground flex items-center justify-center">
      <form
        action={formAction}
        className="bg-card text-card-foreground p-8 w-full max-w-sm rounded-xl border border-border"
      >
        <h1 className="text-xl font-semibold mb-6">Sign In</h1>

        {state?.error && (
          <p className="text-destructive text-sm mb-4">{state.error}</p>
        )}

        <label className="block mb-4">
          <span className="text-sm text-muted-foreground">Email</span>
          <input
            type="email"
            name="email"
            required
            className="mt-1 block w-full bg-input border border-border text-foreground px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </label>

        <label className="block mb-6">
          <span className="text-sm text-muted-foreground">Password</span>
          <input
            type="password"
            name="password"
            required
            className="mt-1 block w-full bg-input border border-border text-foreground px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </label>

        <button
          type="submit"
          disabled={pending}
          className="w-full bg-primary text-primary-foreground py-2 rounded-md disabled:opacity-50 hover:opacity-90 transition-opacity"
        >
          {pending ? "Signing in..." : "Sign In"}
        </button>

        <p className="text-sm text-center mt-4 text-muted-foreground">
          Need an account?{" "}
          <a href="/join" className="text-foreground underline hover:opacity-80">
            Create one
          </a>
        </p>
      </form>
    </main>
  );
}
