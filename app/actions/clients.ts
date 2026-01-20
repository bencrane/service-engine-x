"use server";

import { supabase } from "@/lib/supabase";

interface CreateClientInput {
  name_f: string;
  name_l: string;
  email: string;
  phone?: string;
  company?: string;
  address?: {
    line_1?: string;
    line_2?: string;
    city?: string;
    state?: string;
    postcode?: string;
    country?: string;
  };
  note?: string;
}

interface ActionResult {
  success: boolean;
  data?: Record<string, unknown>;
  error?: string;
}

export async function createClientAction(input: CreateClientInput): Promise<ActionResult> {
  // Validate required fields
  if (!input.name_f?.trim()) {
    return { success: false, error: "First name is required" };
  }
  if (!input.name_l?.trim()) {
    return { success: false, error: "Last name is required" };
  }
  if (!input.email?.trim()) {
    return { success: false, error: "Email is required" };
  }

  // Check email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(input.email)) {
    return { success: false, error: "Invalid email format" };
  }

  // Check if email already exists
  const { data: existingUser } = await supabase
    .from("users")
    .select("id")
    .eq("email", input.email.toLowerCase().trim())
    .single();

  if (existingUser) {
    return { success: false, error: "Email already taken" };
  }

  // Get client role
  const { data: clientRole } = await supabase
    .from("roles")
    .select("id")
    .eq("dashboard_access", 0)
    .single();

  if (!clientRole) {
    return { success: false, error: "Client role not configured" };
  }

  // Create address if provided
  let addressId: string | null = null;
  if (input.address && Object.values(input.address).some(v => v)) {
    const { data: newAddress, error: addressError } = await supabase
      .from("addresses")
      .insert({
        line_1: input.address.line_1 || null,
        line_2: input.address.line_2 || null,
        city: input.address.city || null,
        state: input.address.state || null,
        postcode: input.address.postcode || null,
        country: input.address.country || null,
        name_f: input.name_f,
        name_l: input.name_l,
      })
      .select("id")
      .single();

    if (addressError) {
      return { success: false, error: "Failed to create address" };
    }
    addressId = newAddress.id;
  }

  // Generate affiliate info
  const affId = Math.floor(Math.random() * 900000) + 100000;
  const affCode = Array.from({ length: 6 }, () =>
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"[Math.floor(Math.random() * 36)]
  ).join("");

  // Create user
  const { data: newUser, error: userError } = await supabase
    .from("users")
    .insert({
      email: input.email.toLowerCase().trim(),
      name_f: input.name_f.trim(),
      name_l: input.name_l.trim(),
      company: input.company || null,
      phone: input.phone || null,
      note: input.note || null,
      role_id: clientRole.id,
      status: 1,
      balance: "0.00",
      aff_id: affId,
      aff_link: `https://example.com/r/${affCode}`,
      address_id: addressId,
    })
    .select()
    .single();

  if (userError) {
    // Cleanup address if user creation failed
    if (addressId) {
      await supabase.from("addresses").delete().eq("id", addressId);
    }
    return { success: false, error: "Failed to create client" };
  }

  return {
    success: true,
    data: {
      id: newUser.id,
      name: `${newUser.name_f} ${newUser.name_l}`,
      email: newUser.email,
    },
  };
}
