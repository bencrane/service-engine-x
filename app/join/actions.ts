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

  // Create organization first
  const slug = orgName.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "");

  // Check if slug exists
  const { data: existingOrg } = await supabase
    .from("organizations")
    .select("id")
    .eq("slug", slug)
    .single();

  if (existingOrg) {
    return { error: "Organization name already taken" };
  }

  const { data: org, error: orgError } = await supabase
    .from("organizations")
    .insert({ name: orgName, slug })
    .select()
    .single();

  if (orgError || !org) {
    return { error: "Failed to create organization" };
  }

  // Get administrator role
  const { data: adminRole } = await supabase
    .from("roles")
    .select("id")
    .eq("name", "Administrator")
    .single();

  if (!adminRole) {
    return { error: "System configuration error" };
  }

  // Create user with org_id
  const passwordHash = await hashPassword(password);
  const { data: user, error: userError } = await supabase
    .from("users")
    .insert({
      email,
      password_hash: passwordHash,
      name_f: "",
      name_l: "",
      org_id: org.id,
      role_id: adminRole.id,
    })
    .select()
    .single();

  if (userError || !user) {
    // Rollback org creation
    await supabase.from("organizations").delete().eq("id", org.id);
    return { error: "Failed to create account" };
  }

  // Create session with org context
  await createSession(user.id, org.id);

  redirect("/dashboard");
}
