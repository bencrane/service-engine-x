import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "DELETE",
  path: "/api/clients/{client}",
  summary: "Delete a client",
  description: "Deletes a client. May be a soft delete.",
  tags: ["Clients"],
  operationId: "deleteClient",
  parameters: [
    {
      name: "client",
      in: "path",
      required: true,
      description: "Client user ID",
      schema: { type: "integer" },
    },
  ],
  responses: {
    "204": {
      description: "No Content - Deleted",
    },
    "401": {
      description: "Unauthorized",
    },
    "404": {
      description: "Not Found",
    },
  },
};
