import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "POST",
  path: "/api/clients",
  summary: "Create a client",
  description: "Creates a new client user account.",
  tags: ["Clients"],
  operationId: "createClient",
  requestBody: {
    required: true,
    description: "Client data",
    content: {
      "application/json": {
        schema: {
          type: "object",
          required: ["email", "name_f", "name_l"],
          properties: {
            email: {
              type: "string",
              format: "email",
              description: "Email address",
            },
            name_f: {
              type: "string",
              description: "First name",
            },
            name_l: {
              type: "string",
              description: "Last name",
            },
            company: {
              type: "string",
              description: "Company name",
            },
            phone: {
              type: "string",
              description: "Phone number",
            },
            tax_id: {
              type: "string",
              description: "Tax ID",
            },
            address: {
              type: "object",
              properties: {
                line_1: { type: "string" },
                line_2: { type: "string" },
                city: { type: "string" },
                state: { type: "string" },
                country: { type: "string" },
                postcode: { type: "string" },
              },
            },
            password: {
              type: "string",
              description: "Account password",
            },
            role_id: {
              type: "integer",
              description: "Role ID",
            },
            custom_fields: {
              type: "object",
              description: "Custom field data",
            },
            note: {
              type: "string",
              description: "Internal note",
            },
            optin: {
              type: "string",
              description: "Marketing consent",
            },
            employee_id: {
              type: "integer",
              description: "Assigned employee ID",
            },
          },
        },
      },
    },
  },
  responses: {
    "201": {
      description: "Client created successfully",
      content: {
        "application/json": {
          schema: { $ref: "#/components/schemas/Client" },
        },
      },
    },
    "400": {
      description: "Bad Request - Validation error",
    },
    "401": {
      description: "Unauthorized",
    },
  },
};
