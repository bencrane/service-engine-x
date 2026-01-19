"use client";

import { useActionState } from "react";
import { join } from "./actions";

export default function JoinPage() {
  const [state, formAction, pending] = useActionState(join, null);

  return (
    <main className="min-h-screen bg-black flex items-center justify-center">
      <form action={formAction} className="bg-white p-8 w-full max-w-sm">
        <h1 className="text-xl font-semibold mb-6">Create Account</h1>

        {state?.error && (
          <p className="text-red-600 text-sm mb-4">{state.error}</p>
        )}

        <label className="block mb-4">
          <span className="text-sm">Email</span>
          <input
            type="email"
            name="email"
            required
            className="mt-1 block w-full border border-gray-300 px-3 py-2"
          />
        </label>

        <label className="block mb-4">
          <span className="text-sm">Password</span>
          <input
            type="password"
            name="password"
            required
            className="mt-1 block w-full border border-gray-300 px-3 py-2"
          />
        </label>

        <label className="block mb-6">
          <span className="text-sm">Organization Name</span>
          <input
            type="text"
            name="orgName"
            required
            className="mt-1 block w-full border border-gray-300 px-3 py-2"
          />
        </label>

        <button
          type="submit"
          disabled={pending}
          className="w-full bg-black text-white py-2 disabled:opacity-50"
        >
          {pending ? "Creating..." : "Create Account"}
        </button>

        <p className="text-sm text-center mt-4">
          Already have an account?{" "}
          <a href="/login" className="underline">
            Sign in
          </a>
        </p>
      </form>
    </main>
  );
}
