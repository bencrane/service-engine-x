/**
 * OpenAPI Route Registration
 *
 * Explicitly imports all route metadata and registers them.
 * No filesystem scanning - all imports are explicit.
 */

import { openapi, registerRoute } from "./index";
import { schemas } from "./schemas";

// Health endpoint
import { openapi as healthCheck } from "./routes/health/index";

// Clients endpoints
import { openapi as listClients } from "./routes/clients/list-clients";
import { openapi as createClient } from "./routes/clients/create-client";
import { openapi as retrieveClient } from "./routes/clients/retrieve-client";
import { openapi as updateClient } from "./routes/clients/update-client";
import { openapi as deleteClient } from "./routes/clients/delete-client";

// Services endpoints
import { openapi as listServices } from "./routes/services/list-services";
import { openapi as createService } from "./routes/services/create-service";
import { openapi as retrieveService } from "./routes/services/retrieve-service";
import { openapi as updateService } from "./routes/services/update-service";
import { openapi as deleteService } from "./routes/services/delete-service";

// Order Messages endpoints
import { openapi as listOrderMessages } from "./routes/orders/list-order-messages";
import { openapi as createOrderMessage } from "./routes/orders/create-order-message";
import { openapi as deleteOrderMessage } from "./routes/orders/delete-order-message";

// Order Tasks endpoints
import { openapi as listOrderTasks } from "./routes/orders/list-order-tasks";
import { openapi as createOrderTask } from "./routes/orders/create-order-task";
import { openapi as updateOrderTask } from "./routes/orders/update-order-task";
import { openapi as deleteOrderTask } from "./routes/orders/delete-order-task";

// Proposals endpoints
import { openapi as listProposals } from "./routes/proposals/list-proposals";
import { openapi as createProposal } from "./routes/proposals/create-proposal";
import { openapi as retrieveProposal } from "./routes/proposals/retrieve-proposal";
import { openapi as sendProposal } from "./routes/proposals/send-proposal";
import { openapi as signProposal } from "./routes/proposals/sign-proposal";

/**
 * Register all schemas
 */
function registerSchemas(): void {
  Object.assign(openapi.components.schemas, schemas);
}

/**
 * Register all routes
 */
function registerAllRoutes(): void {
  // Health
  registerRoute(healthCheck);

  // Clients
  registerRoute(listClients);
  registerRoute(createClient);
  registerRoute(retrieveClient);
  registerRoute(updateClient);
  registerRoute(deleteClient);

  // Services
  registerRoute(listServices);
  registerRoute(createService);
  registerRoute(retrieveService);
  registerRoute(updateService);
  registerRoute(deleteService);

  // Order Messages
  registerRoute(listOrderMessages);
  registerRoute(createOrderMessage);
  registerRoute(deleteOrderMessage);

  // Order Tasks
  registerRoute(listOrderTasks);
  registerRoute(createOrderTask);
  registerRoute(updateOrderTask);
  registerRoute(deleteOrderTask);

  // Proposals
  registerRoute(listProposals);
  registerRoute(createProposal);
  registerRoute(retrieveProposal);
  registerRoute(sendProposal);
  registerRoute(signProposal);
}

/**
 * Initialize OpenAPI spec with all registered routes
 */
export function initializeOpenAPI(): void {
  registerSchemas();
  registerAllRoutes();
}

// Auto-initialize on import
initializeOpenAPI();
