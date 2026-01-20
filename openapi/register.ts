/**
 * OpenAPI Route Registration
 *
 * Explicitly imports all route metadata and registers them.
 * No filesystem scanning - all imports are explicit.
 */

import { openapi, registerRoute } from "./index";
import { schemas } from "./schemas";

// Clients endpoints
import { openapi as listClients } from "./routes/clients/list-clients";
import { openapi as createClient } from "./routes/clients/create-client";
import { openapi as retrieveClient } from "./routes/clients/retrieve-client";
import { openapi as updateClient } from "./routes/clients/update-client";
import { openapi as deleteClient } from "./routes/clients/delete-client";

/**
 * Register all schemas
 */
function registerSchemas(): void {
  Object.assign(openapi.components.schemas, schemas);
}

/**
 * Register all Clients routes
 */
function registerClientsRoutes(): void {
  registerRoute(listClients);
  registerRoute(createClient);
  registerRoute(retrieveClient);
  registerRoute(updateClient);
  registerRoute(deleteClient);
}

/**
 * Initialize OpenAPI spec with all registered routes
 */
export function initializeOpenAPI(): void {
  registerSchemas();
  registerClientsRoutes();
}

// Auto-initialize on import
initializeOpenAPI();
