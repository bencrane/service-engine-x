import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "GET",
  path: "/api/clients",
  summary: "List all clients",
  description: "Returns a paginated list of all clients.",
  tags: ["Clients"],
  operationId: "listClients",
  parameters: [
    {
      name: "limit",
      in: "query",
      required: false,
      description: "Items per page",
      schema: { type: "integer", default: 10 },
    },
    {
      name: "page",
      in: "query",
      required: false,
      description: "Page number",
      schema: { type: "integer", default: 1 },
    },
    {
      name: "sort",
      in: "query",
      required: false,
      description: "Sort by fields (e.g., id:desc)",
      schema: { type: "string" },
    },
    {
      name: "filters[email][$eq]",
      in: "query",
      required: false,
      description: "Filter by email",
      schema: { type: "string" },
    },
    {
      name: "filters[status][$eq]",
      in: "query",
      required: false,
      description: "Filter by status",
      schema: { type: "integer" },
    },
  ],
  responses: {
    "200": {
      description: "Successful response",
      content: {
        "application/json": {
          schema: {
            type: "object",
            properties: {
              data: {
                type: "array",
                items: { $ref: "#/components/schemas/Client" },
              },
              links: { $ref: "#/components/schemas/PaginationLinks" },
              meta: { $ref: "#/components/schemas/PaginationMeta" },
            },
          },
        },
      },
    },
    "401": {
      description: "Unauthorized",
    },
  },
};
