import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "PATCH",
  path: "/api/proposals/{id}/send",
  summary: "Send a proposal",
  description: "Marks a draft proposal as sent. Sets status to 'Sent' and records sent_at timestamp.",
  tags: ["Proposals"],
  operationId: "sendProposal",
  responses: {
    "200": {
      description: "Proposal sent successfully",
    },
    "400": {
      description: "Cannot send proposal - invalid status transition",
    },
    "401": {
      description: "Unauthorized - invalid or missing API token",
    },
    "404": {
      description: "Proposal not found",
    },
  },
};
