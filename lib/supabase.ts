import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.SERVICE_ENGINE_X_SUPABASE_URL!;
const supabaseServiceKey = process.env.SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY!;

export const supabase = createClient(supabaseUrl, supabaseServiceKey);
