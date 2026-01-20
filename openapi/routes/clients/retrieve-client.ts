import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "GET",
  path: "/api/clients/{client}",
  summary: "Retrieve a client",
  description: "Returns a single client by ID.",
  tags: ["Clients"],
  operationId: "retrieveClient",
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
    "200": {
      description: "Successful response",
      content: {
        "application/json": {
          schema: { $ref: "#/components/schemas/Client" },
        },
      },
    },
    "401": {
      description: "Unauthorized",
    },
    "404": {
      description: "Not Found",
    },
  },
};
