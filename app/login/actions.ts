"use server";

import { redirect } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { verifyPassword, createSession } from "@/lib/auth";

export async function login(_prevState: unknown, formData: FormData) {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  // Find user
  const { data: user } = await supabase
    .from("users")
    .select("*")
    .eq("email", email)
    .single();

  if (!user) {
    return { error: "Invalid email or password" };
  }

  // Verify password
  const valid = await verifyPassword(password, user.password_hash);
  if (!valid) {
    return { error: "Invalid email or password" };
  }

  // Create session
  await createSession(user.id);

  redirect("/dashboard");
}
