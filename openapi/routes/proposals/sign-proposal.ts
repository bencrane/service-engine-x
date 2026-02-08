import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "PATCH",
  path: "/api/proposals/{id}/sign",
  summary: "Sign a proposal and create order",
  description: "Marks a sent proposal as signed. Creates an order from the proposal items and links it via converted_order_id. Returns both the updated proposal and the created order.",
  tags: ["Proposals"],
  operationId: "signProposal",
  responses: {
    "200": {
      description: "Proposal signed and order created successfully",
    },
    "400": {
      description: "Cannot sign proposal - invalid status transition",
    },
    "401": {
      description: "Unauthorized - invalid or missing API token",
    },
    "404": {
      description: "Proposal not found",
    },
    "500": {
      description: "Failed to create order",
    },
  },
};
