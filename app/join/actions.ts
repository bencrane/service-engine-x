"use server";

import { redirect } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { hashPassword, createSession } from "@/lib/auth";

export async function join(_prevState: unknown, formData: FormData) {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const orgName = formData.get("orgName") as string;

  // Check if email exists
  const { data: existingUser } = await supabase
    .from("users")
    .select("id")
    .eq("email", email)
    .single();

  if (existingUser) {
    return { error: "Email already exists" };
  }

  // Create user
  const passwordHash = await hashPassword(password);
  const { data: user, error: userError } = await supabase
    .from("users")
    .insert({ email, password_hash: passwordHash })
    .select()
    .single();

  if (userError || !user) {
    return { error: "Failed to create account" };
  }

  // Create org
  const slug = orgName.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "");
  const { data: org, error: orgError } = await supabase
    .from("orgs")
    .insert({ name: orgName, slug, owner_user_id: user.id })
    .select()
    .single();

  if (orgError || !org) {
    return { error: "Failed to create organization" };
  }

  // Add user as owner in org_members
  await supabase.from("org_members").insert({
    org_id: org.id,
    user_id: user.id,
    role: "owner",
  });

  // Create session
  await createSession(user.id);

  redirect("/dashboard");
}
